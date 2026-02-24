from tkinter import *
from tkinter import messagebox, END
from tkinter import ttk
import pymysql
import os
from PIL import Image,ImageTk
import tkinter.messagebox as messagebox
from reportlab.pdfgen import canvas
from tkinter import filedialog
from tkinter import PhotoImage, Button, Entry, Frame, Label, Scrollbar, HORIZONTAL, VERTICAL, BOTH



# Connect to MySQL
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="1234",
    database="handloom"
)

cursor = conn.cursor()

# Modify the table creation query to check if the table exists
create_stock_table_query = """
CREATE TABLE IF NOT EXISTS stock (
    itemid INT  PRIMARY KEY,
    itemname VARCHAR(100) NOT NULL,
    itemtype VARCHAR(100) NOT NULL,
    qty INT DEFAULT 0
);
"""

# Execute the query to create the item table if it does not exist
cursor.execute(create_stock_table_query)
conn.commit()
print("Stock table created successfully!")

# Close connection
cursor.close()
conn.close()






def fetch_stock_data():
    """Fetch item data along with dynamically calculated stock quantity from the database and update the Treeview and stock table."""
    stock_treeview.delete(*stock_treeview.get_children())  # Clear old data

    # Connect to MySQL
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="1234",
        database="handloom"
    )
    cursor = conn.cursor()

    # Query to compute stock quantity dynamically
    query = """
    SELECT i.itemid, i.itemname, i.itemtype,
       (i.qty + 
       COALESCE((SELECT SUM(p.puqty) FROM purchase p WHERE p.itemname = i.itemname), 0) - 
       COALESCE((SELECT SUM(s.saquantity) FROM sales s WHERE s.itemname = i.itemname), 0) - 
       COALESCE((SELECT SUM(pr.return_quantity) FROM purchase_return pr WHERE pr.itemname = i.itemname), 0) +
       COALESCE((SELECT SUM(sr.retquantity) FROM sales_return sr WHERE sr.itemname = i.itemname), 0)
       ) AS stock_qty
    FROM item i
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()  # Close connection to the database after fetching data

    # Insert fetched data into the Treeview and also insert or update it into the stock table
    conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
    cursor = conn.cursor()

    for row in rows:
        # Insert into Treeview
        stock_treeview.insert("", END, values=row)

        # Check if the item already exists in the stock table (by itemid)
        check_query = "SELECT itemid FROM stock WHERE itemid = %s"
        cursor.execute(check_query, (row[0],))
        existing_item = cursor.fetchone()

        # If the item exists, update the qty in the stock table
        if existing_item:
            update_query = """
            UPDATE stock 
            SET qty = %s 
            WHERE itemid = %s
            """
            cursor.execute(update_query, (row[3], row[0]))  # Update qty based on stock_qty
        else:
            # If the item doesn't exist, insert it into the stock table
            insert_query = """
            INSERT INTO stock (itemid, itemname, itemtype, qty) 
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (row[0], row[1], row[2], row[3]))  # Insert new record

    conn.commit()  # Commit the changes to the database
    cursor.close()
    conn.close()  # Close the connection to the database

    print("Stock data has been updated in the stock table successfully.")

def search_stock_data(search_combobox, search_entry):
    search_criteria = search_combobox.get().strip()
    search_value = search_entry.get().strip()

    if not search_value:
        messagebox.showerror("Error", "Please enter a value to search.")
        return

    conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
    cursor = conn.cursor()

    try:
        if search_criteria == "Id":
            query = "SELECT * FROM stock WHERE itemid = %s"
            cursor.execute(query, (search_value,))
        elif search_criteria == "Name":
            query = "SELECT * FROM stock WHERE itemname LIKE %s"
            cursor.execute(query, ('%' + search_value + '%',))
        elif search_criteria == "All":
            query = "SELECT * FROM stock"
            cursor.execute(query)

        records = cursor.fetchall()

        # Clear existing data in Treeview
        stock_treeview.delete(*stock_treeview.get_children())

        for row in records:
            stock_treeview.insert("", "end", values=row)

    except Exception as e:
        messagebox.showerror("Error", f"Error fetching data: {e}")

    finally:
        cursor.close()
        conn.close()

def generate_pdf_report(records, report_name):
    # Prompt user to select the folder to save the report
    folder_selected = filedialog.askdirectory(title="Select Folder")
    if not folder_selected:
        messagebox.showerror("Error", "No folder selected.")
        return

    # Define the path for the PDF file (dynamically named based on company name or 'All' for all records)
    report_path = os.path.join(folder_selected, report_name + ".pdf")

    try:
        # Increase the page width if necessary (for wider tables)
        page_width = 400  # Custom width to increase space on the page
        page_height = 1100  # Standard height (you can adjust this as well)

        # Create a canvas object to generate the PDF
        pdf = canvas.Canvas(report_path, pagesize=(page_width, page_height))
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(150, 1050, "Stock Report")

        # Set font for table headers and data
        pdf.setFont("Helvetica", 10)

        # Adjusted column widths with increased width for Address and City
        col_widths = [100, 100, 100, 100]  # Address and City columns increased

        # Draw table headers
        header = ["Item Id", "Item Name","Item Type", "Quantity"]
        x_pos = 30  # Starting position for the first column
        y_pos = 1020  # Starting vertical position (closer to the top of the page)

        for i, header_text in enumerate(header):
            pdf.drawString(x_pos, y_pos, header_text)
            x_pos += col_widths[i]  # Move to the next column

        # Draw the company data rows
        y_pos -= 20  # Move down for the data rows
        for row in records:
            x_pos = 30  # Reset starting position for each row
            for i, data in enumerate(row):
                pdf.drawString(x_pos, y_pos, str(data))
                x_pos += col_widths[i]  # Move to the next column
            y_pos -= 20  # Move down for the next row

            # Check if we need to add a new page when space is running out
            if y_pos < 50:
                pdf.showPage()  # Start a new page
                pdf.setFont("Helvetica", 10)
                y_pos = 1050  # Reset y-position for the new page
                x_pos = 30  # Reset x-position for the new page

                # Draw the headers again on the new page
                for i, header_text in enumerate(header):
                    pdf.drawString(x_pos, y_pos, header_text)
                    x_pos += col_widths[i]  # Move to the next column

                y_pos -= 20  # Move down for the next row after header

        # Save the PDF
        pdf.save()

        messagebox.showinfo("Success", f"Report saved as PDF at: {report_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate PDF: {e}")

# Updated function for "Report" button to generate the PDF directly
def on_report_button_click(search_combobox, search_entry):
    search_criteria = search_combobox.get().strip()
    search_value = search_entry.get().strip()

    if not search_value and search_criteria != "All":
        messagebox.showerror("Error", "Please enter a value to search.")
        return

    try:
        conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
        cursor = conn.cursor()

        # Determine the SQL query based on search criteria
        if search_criteria == "Id":
            query = "SELECT * FROM stock WHERE itemid = %s"
            cursor.execute(query, (search_value,))
            report_name = f"Stock_Report_{search_value}"  # Dynamic name for the report
        elif search_criteria == "Name":
            query = "SELECT * FROM stock WHERE itemname LIKE %s"
            cursor.execute(query, ('%' + search_value + '%',))
            report_name = f"Stock_Report_{search_value}"  # Dynamic name for the report
        elif search_criteria == "All":
            query = "SELECT * FROM stock"
            cursor.execute(query)
            report_name = "Stock_Report_All"  # Generic name for all companies

        records = cursor.fetchall()

        if not records:
            messagebox.showerror("Error", "No data found for the given search criteria.")
            return

        # Generate the PDF report with dynamic name
        generate_pdf_report(records, report_name)

    except Exception as e:
        messagebox.showerror("Error", f"Error fetching data: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Function to trigger the report generation directly
def trigger_report_generation():
    on_report_button_click()  # Call the function for generating the report

# Function to open the generated PDF report


def open_pdf_report():
    # Open a file dialog to allow the user to select a PDF file
    pdf_path = filedialog.askopenfilename(
        title="Select PDF Report",
        filetypes=[("PDF Files", "*.pdf")]
    )

    # Check if the user selected a file
    if not pdf_path:
        messagebox.showwarning("No file selected", "No PDF file selected.")
        return

    # Try to open the selected PDF file
    try:
        if os.path.exists(pdf_path):
            # Try opening the file using the default system PDF viewer
            os.startfile(pdf_path)
        else:
            messagebox.showwarning("File Not Found", f"The selected PDF file does not exist:\n{pdf_path}")
    except Exception as e:
        # Handle any errors that occur while opening the file
        messagebox.showerror("Error", f"Could not open the PDF file: {str(e)}")




def stock_form(window):
    global back_image, stock_treeview
    company_frame = Frame(window, width=1270, height=542,bg='#DFF2EB')
    company_frame.place(x=0, y=99)
    heading_label = Label(company_frame, text='Manage Stock Detail', font=('times new roman', 18, 'bold'),fg='white',
                          bg='#7AB2D3')
    heading_label.place(x=0, y=0, relwidth='1')


    # -----------------------------------------
    top_frame = Frame(company_frame, bg='#DFF2EB')
    top_frame.place(x=0, y=40, relwidth=1, height=200)
    search_frame = Frame(top_frame, bg='#DFF2EB')
    search_frame.pack()

    search_combobox = ttk.Combobox(search_frame, values=('Id', 'Name', 'All'), font=('times new roman', 13),
                                   state='readonly')
    search_combobox.set('Search By')
    search_combobox.grid(row=0, column=0, padx=20)

    search_entry = Entry(search_frame, font=('times new roman', 13))
    search_entry.grid(row=0, column=1)

    search_button = Button(search_frame, text='Search', font=('times new roman', 13), cursor='hand1', width=10,
                           height=0, bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3',
                           border=2, command=lambda: search_stock_data(search_combobox, search_entry))  # Use the function for searching
    search_button.grid(row=0, column=2, padx=10)

    show_button = Button(search_frame, text='Show All', font=('times new roman', 13), cursor='hand1', width=10,
                         bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2, command=fetch_stock_data)
    show_button.grid(row=0, column=3,padx=10)

    report_button = Button(search_frame, text='Report', font=('times new roman', 13), cursor='hand1', width=10,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                           command=lambda: on_report_button_click(search_combobox,
                                                                  search_entry))  # Updated function for report generation
    report_button.grid(row=0, column=4, padx=10)

    # Add the Fetch button
    fetch_button = Button(search_frame, text='View', font=('times new roman', 13), cursor='hand1', width=10,
                          bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                          command=open_pdf_report)  # Call open_pdf_report function
    fetch_button.grid(row=0, column=5, padx=10)

    back_image = PhotoImage(file='image\\back .png')
    back_button = Button(company_frame, image=back_image, border=0, cursor='hand2', bg='#DFF2EB',
                         activebackground='#DFF2EB', command=lambda: company_frame.place_forget())
    back_button.place(x=13, y=35)

    leftframe = Frame(company_frame, bg='black')
    leftframe.place(x=50, y=110, width=250, height=200)

    # Open and resize the image
    image = Image.open("image\\img.jpg")  # Replace with your image file path
    image = image.resize((300, 200), Image.Resampling.LANCZOS)  # Resize the image to fit
    img = ImageTk.PhotoImage(image)  # Convert to Tkinter-compatible photo image

    # Create a label to display the image
    image_label = Label(company_frame, image=img)
    image_label.place(x=50, y=110)  # Position the label (you can adjust coordinates)

    # Keep a reference to the image to avoid garbage collection
    image_label.image = img

    lleftframe = Frame(company_frame, bg='black')
    lleftframe.place(x=350, y=110, width=250, height=200)

    # Open and resize the image
    image = Image.open("image\\towel.jpg")  # Replace with your image file path
    image = image.resize((300, 200), Image.Resampling.LANCZOS)  # Resize the image to fit
    img = ImageTk.PhotoImage(image)  # Convert to Tkinter-compatible photo image

    # Create a label to display the image
    image_label = Label(company_frame, image=img)
    image_label.place(x=350, y=110)  # Position the label (you can adjust coordinates)

    # Keep a reference to the image to avoid garbage collection
    image_label.image = img

    llleftframe = Frame(company_frame, bg='black')
    llleftframe.place(x=650, y=110, width=250, height=200)

    # Open and resize the image
    image = Image.open("image\\bad.jpg")  # Replace with your image file path
    image = image.resize((300, 200), Image.Resampling.LANCZOS)  # Resize the image to fit
    img = ImageTk.PhotoImage(image)  # Convert to Tkinter-compatible photo image

    # Create a label to display the image
    image_label = Label(company_frame, image=img)
    image_label.place(x=650, y=110)  # Position the label (you can adjust coordinates)

    # Keep a reference to the image to avoid garbage collection
    image_label.image = img

    llleftframe = Frame(company_frame, bg='black')
    llleftframe.place(x=920, y=110, width=250, height=200)

    # Open and resize the image
    image = Image.open("image\\blan.jpg")  # Replace with your image file path
    image = image.resize((300, 200), Image.Resampling.LANCZOS)  # Resize the image to fit
    img = ImageTk.PhotoImage(image)  # Convert to Tkinter-compatible photo image

    # Create a label to display the image
    image_label = Label(company_frame, image=img)
    image_label.place(x=920, y=110)  # Position the label (you can adjust coordinates)

    # Keep a reference to the image to avoid garbage collection
    image_label.image = img
    # -----------------------------------------------------------
    # Adjusted Top Frame and Treeview placement
    top_frame = Frame(company_frame, bg='#DFF2EB')
    top_frame.place(x=0, y=350, relwidth=1, height=190)  # Placed at the bottom of item_frame

    # Create horizontal and vertical scrollbars
    horizontal_scrollbar = Scrollbar(top_frame, orient=HORIZONTAL)
    vertical_scrollbar = Scrollbar(top_frame, orient=VERTICAL)

    stock_treeview = ttk.Treeview(top_frame, columns=(
        'itemid', 'itemname', 'itemtype', 'qty'), show='headings',yscrollcommand=vertical_scrollbar.set,xscrollcommand=horizontal_scrollbar.set)
    horizontal_scrollbar.pack(side=BOTTOM, fill=X, pady=(0, 0), padx=(0,0))
    vertical_scrollbar.pack(side=RIGHT, fill=Y, pady=(0, 0), padx=(0, 0))
    horizontal_scrollbar.config(command=stock_treeview.xview)
    vertical_scrollbar.config(command=stock_treeview.yview)
    stock_treeview.pack(fill=BOTH, expand=True, pady=(0, 0))

    stock_treeview.heading('itemid', text='Item Id')
    stock_treeview.heading('itemname', text='Item Name')
    stock_treeview.heading('itemtype', text='Item Type')
    stock_treeview.heading('qty', text='Quantity')

    stock_treeview.column('itemid',width=180)
    stock_treeview.column('itemname',width=180)
    stock_treeview.column('itemtype',width=180)
    stock_treeview.column('qty',width=180)

    fetch_stock_data()

