from tkinter import *
import tkinter as tk
import qrcode
from PIL import Image, ImageTk
import webbrowser
from tkcalendar import DateEntry
import qrcode
import pymysql
import os
from tkinter import ttk, PhotoImage, Entry, Frame, Label, Button, Text, Scrollbar, HORIZONTAL, VERTICAL, BOTH, END
from datetime import datetime
from reportlab.pdfgen import canvas
from tkinter import Tk, ttk, filedialog, messagebox
from tkinter import Button
from tkinter import Toplevel


# Connect to MySQL
conn = pymysql.connect(
    host="localhost",      # Change if needed
    user="root",           # Your MySQL username
    password="1234",           # Your MySQL password
    database="handloom"    # Target database
)

# Create a cursor
cursor = conn.cursor()

create_sales_table_query = """
CREATE TABLE IF NOT EXISTS bill (
    billno INT AUTO_INCREMENT PRIMARY KEY,
    salesid INT,
    salesdate DATE NOT NULL,
    custname VARCHAR(255) NOT NULL,
    itemname VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    saquantity INT NOT NULL,
    saamount DECIMAL(10, 2) NOT NULL,
    sagst DECIMAL(10, 2) NOT NULL,
    sadiscount DECIMAL(10, 2) NOT NULL,
    satotalamount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (salesid) REFERENCES sales(salesid)
) AUTO_INCREMENT = 10001;

"""

cursor.execute(create_sales_table_query)
conn.commit()
print("Bill table created successfully!")




# Function to generate the QR code
def generate_qr_code(payment_amount):
    # Create the data for the QR code, e.g., the payment amount
    data = f"Payment Amount: {payment_amount}"

    # Generate the QR code
    qr = qrcode.QRCode(
        version=1,  # Size of the QR code
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,  # Size of each box
        border=4,  # Border size
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create an image of the QR code
    img = qr.make_image(fill='black', back_color='white')

    # Show the QR code in a new window
    top = Toplevel()  # Create a new window
    top.title("QR Code for Payment")
    top.geometry("300x300")

    # Convert the QR code image to a Tkinter-compatible image
    img_tk = ImageTk.PhotoImage(img)
    qr_label = Label(top, image=img_tk)
    qr_label.image = img_tk  # Keep a reference to avoid garbage collection
    qr_label.pack()


# Function to handle the button click and trigger QR code generation
def on_payment_button_click(s_total_amt_entry):
    # Get the total amount from the form (you can adjust this according to your form fields)
    total_amount = s_total_amt_entry.get().strip()  # Use .strip() to remove any leading/trailing spaces

    if not total_amount:
        messagebox.showerror("Error", "Total amount is missing.")
        return

    try:
        total_amount = float(total_amount)  # Attempt to convert to float
        generate_qr_code(total_amount)  # Generate QR code based on the total amount
    except ValueError:
        messagebox.showerror("Error", "Invalid total amount entered. Please enter a valid number.")




def get_next_billno():
    cursor.execute("SELECT MAX(billno) FROM bill")
    result = cursor.fetchone()
    # If there is no bill, start from 10001
    next_billno = result[0] + 1 if result[0] is not None else 10001
    return next_billno

def on_billno_click(event, sbill_id_entry):
    next_billno = get_next_billno()
    sbill_id_entry.delete(0, END)  # Clear any existing text
    sbill_id_entry.insert(0, str(next_billno))  # Insert the next bill number

def populate_sales_ids():
    # Open a new connection and cursor for the query
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="1234",
        database="handloom"
    )
    cursor = conn.cursor()

    # Query to fetch customer ids in ascending order
    cursor.execute("SELECT salesid FROM sales ORDER BY custid ASC")

    # Fetching all customer ids
    sales_ids = cursor.fetchall()

    # Close the cursor and connection after use
    cursor.close()
    conn.close()

    # Return a list of customer ids
    return [str(row[0]) for row in sales_ids]  # return as a list of strings

def fill_sales_details(event, sal_id_combobox, s_date_entry, s_cust_name_entry, s_item_nm_entry, s_price_entry,
                       s_qty_entry, s_total_entry, s_gst_entry, s_dis_entry, s_total_amt_entry):
    # Get the selected salesid
    salesid = sal_id_combobox.get()
    if salesid != 'Select Id' and salesid != '':
        try:
            # Fetch the sales details for the selected salesid
            cursor.execute("""
                SELECT salesdate, custname, itemname, price, saquantity, saamount, sagst, sadiscount, satotalamount
                FROM sales WHERE salesid = %s
            """, (salesid,))
            result = cursor.fetchone()

            if result:
                # Fill the entries with the fetched data
                s_date_entry.set_date(result[0])  # Setting date in the DateEntry widget
                s_cust_name_entry.delete(0, END)
                s_cust_name_entry.insert(0, result[1])

                s_item_nm_entry.delete(0, END)
                s_item_nm_entry.insert(0, result[2])

                s_price_entry.delete(0, END)
                s_price_entry.insert(0, result[3])

                s_qty_entry.delete(0, END)
                s_qty_entry.insert(0, result[4])

                s_total_entry.delete(0, END)
                s_total_entry.insert(0, result[5])

                s_gst_entry.delete(0, END)
                s_gst_entry.insert(0, result[6])

                s_dis_entry.delete(0, END)
                s_dis_entry.insert(0, result[7])

                s_total_amt_entry.delete(0, END)
                s_total_amt_entry.insert(0, result[8])
            else:
                # If no data is found, show a message
                messagebox.showinfo("No Data", f"No data found for salesid: {salesid}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


def add_data(sbill_id_entry, sal_id_combobox, s_date_entry, s_cust_name_entry, s_item_nm_entry, s_price_entry,
             s_qty_entry, s_total_entry, s_gst_entry, s_dis_entry, s_total_amt_entry):
    bill_no = sbill_id_entry.get()
    sales_id = sal_id_combobox.get()

    # Check if the DateEntry has a valid date
    sales_date = s_date_entry.get_date()
    if not sales_date:
        messagebox.showerror("Invalid Date", "Please select a valid date.")
        return

    customer_name = s_cust_name_entry.get()
    item_name = s_item_nm_entry.get()
    price = float(s_price_entry.get())
    quantity = int(s_qty_entry.get())
    amount = float(s_total_entry.get())
    gst = float(s_gst_entry.get())
    discount = float(s_dis_entry.get())
    total_amount = float(s_total_amt_entry.get())

    try:
        # Insert the data into the bill table
        cursor.execute("""
            INSERT INTO bill (billno, salesid, salesdate, custname, itemname, price, saquantity, saamount, sagst, 
            sadiscount, satotalamount) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
        bill_no, sales_id, sales_date, customer_name, item_name, price, quantity, amount, gst, discount, total_amount))

        conn.commit()
        messagebox.showinfo("Success", "Bill added successfully")
        # Clear the form fields after adding the bill
        clear_form(sbill_id_entry, sal_id_combobox, s_date_entry, s_cust_name_entry, s_item_nm_entry,
                   s_price_entry, s_qty_entry, s_total_entry, s_gst_entry, s_dis_entry, s_total_amt_entry)
        populate_treeview()  # Refresh Treeview after adding data
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def populate_treeview():
    # Clear the existing data in the Treeview
    for row in item_treeview.get_children():
        item_treeview.delete(row)

    # Fetch all bills from the database
    cursor.execute("SELECT billno, salesid, salesdate, custname, itemname, price, saquantity, saamount, sagst, "
                   "sadiscount, satotalamount FROM bill")
    rows = cursor.fetchall()

    # Insert each record into the Treeview
    for row in rows:
        item_treeview.insert("", END, values=row)





def on_treeview_select(event, sbill_id_entry, sal_id_combobox, s_date_entry, s_cust_name_entry,
                       s_item_nm_entry, s_price_entry, s_qty_entry, s_total_entry, s_gst_entry,
                       s_dis_entry, s_total_amt_entry):
    selected_item = item_treeview.selection()  # Get the selected item in the treeview
    if selected_item:
        # Get the values from the selected record
        values = item_treeview.item(selected_item[0], 'values')

        # Fill the form with the selected record's data
        sbill_id_entry.delete(0, END)
        sbill_id_entry.insert(0, values[0])

        sal_id_combobox.set(values[1])

        # Convert the date string to a datetime object and set the date entry
        try:
            date_value = datetime.strptime(values[2], '%Y-%m-%d').date()
            s_date_entry.set_date(date_value)
        except ValueError:
            # Handle invalid date format if needed
            print(f"Invalid date format for {values[2]}")

        s_cust_name_entry.delete(0, END)
        s_cust_name_entry.insert(0, values[3])

        s_item_nm_entry.delete(0, END)
        s_item_nm_entry.insert(0, values[4])

        s_price_entry.delete(0, END)
        s_price_entry.insert(0, values[5])

        s_qty_entry.delete(0, END)
        s_qty_entry.insert(0, values[6])

        s_total_entry.delete(0, END)
        s_total_entry.insert(0, values[7])

        s_gst_entry.delete(0, END)
        s_gst_entry.insert(0, values[8])

        s_dis_entry.delete(0, END)
        s_dis_entry.insert(0, values[9])

        s_total_amt_entry.delete(0, END)
        s_total_amt_entry.insert(0, values[10])


def clear_form(sbill_id_entry, sal_id_combobox, s_date_entry, s_cust_name_entry, s_item_nm_entry,
               s_price_entry, s_qty_entry, s_total_entry, s_gst_entry, s_dis_entry, s_total_amt_entry):
    sbill_id_entry.delete(0, END)
    sal_id_combobox.set('Select Id')

    # Set the DateEntry widget to None to clear the date
    s_date_entry.set_date(None)

    s_cust_name_entry.delete(0, END)
    s_item_nm_entry.delete(0, END)
    s_price_entry.delete(0, END)
    s_qty_entry.delete(0, END)
    s_total_entry.delete(0, END)
    s_gst_entry.delete(0, END)
    s_dis_entry.delete(0, END)
    s_total_amt_entry.delete(0, END)

def search_bill_data(search_combobox, search_entry):
    search_criteria = search_combobox.get().strip()
    search_value = search_entry.get().strip()

    if not search_value:
        messagebox.showerror("Error", "Please enter a value to search.")
        return

    conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
    cursor = conn.cursor()

    try:
        if search_criteria == "Id":
            query = "SELECT * FROM bill WHERE billno = %s"
            cursor.execute(query, (search_value,))
        elif search_criteria == "Name":
            query = "SELECT * FROM bill WHERE custname LIKE %s"
            cursor.execute(query, ('%' + search_value + '%',))
        elif search_criteria == "All":
            query = "SELECT * FROM bill"
            cursor.execute(query)

        records = cursor.fetchall()

        # Clear existing data in Treeview
        item_treeview.delete(*item_treeview.get_children())

        for row in records:
            item_treeview.insert("", "end", values=row)

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

    # Define the path for the PDF file
    report_path = os.path.join(folder_selected, report_name + ".pdf")

    try:
        # Define page dimensions
        page_width = 360
        page_height = 1100

        # Create PDF canvas
        pdf = canvas.Canvas(report_path, pagesize=(page_width, page_height))
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(80, 1050, "Khodiyar Handloom Bill")

        # Set font for the data
        pdf.setFont("Helvetica", 10)

        # Define positions for labels and values
        x_pos_label = 30   # Starting position for labels
        x_pos_value = 180
        x_pos_name = 30
        x_pos_qty = 100    # Position for Quantity column
        x_pos_price = 160  # Position for Price column
        x_pos_amount = 250 # Position for Amount column
        y_pos = 1020       # Starting vertical position

        pdf.setFont("Helvetica", 10)

        for row in records:
            # Display Bill No, Sales Id, Date, and Customer Name
            pdf.drawString(x_pos_label, y_pos, f"Bill No: {row[0]}")
            pdf.drawString(x_pos_value, y_pos, f"Sales Id: {row[1]}")
            y_pos -= 20

            pdf.drawString(x_pos_label, y_pos, f"Date: {row[2]}")
            pdf.drawString(x_pos_value, y_pos, f"Customer Name: {row[3]}")
            y_pos -= 20  # Add space before Item Name

            # Draw table headers
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(x_pos_name, y_pos, "Item Name:")
            pdf.drawString(x_pos_qty, y_pos, "Quantity")
            pdf.drawString(x_pos_price, y_pos, "Price (per unit)")
            pdf.drawString(x_pos_amount, y_pos, "Amount")
            y_pos -= 20  # Move down for item data

            # Draw item details in tabular format
            pdf.setFont("Helvetica", 10)
            pdf.drawString(x_pos_name, y_pos, row[4])  # Item Name
            pdf.drawString(x_pos_qty, y_pos, str(row[6]))  # Quantity
            pdf.drawString(x_pos_price, y_pos, str(row[5]))  # Price per unit
            pdf.drawString(x_pos_amount, y_pos, str(row[7]))  # Amount
            y_pos -= 40  # Extra space before next entry

            pdf.drawString(x_pos_value, y_pos, f"Gst: {row[8]}")
            y_pos -= 20
            pdf.drawString(x_pos_value, y_pos, f"Discount: {row[9]}")
            y_pos -= 20
            pdf.drawString(x_pos_value, y_pos, f"Total Amount: {row[10]}")
            y_pos -= 20

            # If space runs out, start a new page
            if y_pos < 50:
                pdf.showPage()
                pdf.setFont("Helvetica", 10)
                y_pos = 1020  # Reset position for new page

        # Save the PDF
        pdf.save()
        messagebox.showinfo("Success", f"Report saved as PDF at: {report_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate PDF: {e}")

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
            query = "SELECT * FROM bill WHERE billno = %s"
            cursor.execute(query, (search_value,))
            report_name = f"Bill_Report_{search_value}"  # Dynamic name for the report
        elif search_criteria == "Name":
            query = "SELECT * FROM bill WHERE itemname LIKE %s"
            cursor.execute(query, ('%' + search_value + '%',))
            report_name = f"Bill_Report_{search_value}"  # Dynamic name for the report
        elif search_criteria == "All":
            query = "SELECT * FROM bill"
            cursor.execute(query)
            report_name = "Bill_Report_All"  # Generic name for all companies

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



def bill_form(window):
    global back_image,item_treeview
    item_frame = Frame(window, width=1270, height=542, bg='#DFF2EB')
    item_frame.place(x=0, y=99)
    heading_label = Label(item_frame, text='Manage Bill Detail', font=('times new roman', 18, 'bold'), fg='white',
                          bg='#7AB2D3')
    heading_label.place(x=0, y=0, relwidth='1')

    # -----------------------------------------
    top_frame = Frame(item_frame, bg='#DFF2EB')
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
                           border=2,command=lambda: search_bill_data(search_combobox, search_entry))
    search_button.grid(row=0, column=2, padx=20)

    show_button = Button(search_frame, text='Show All', font=('times new roman', 13), cursor='hand1', width=10,
                         bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                         command=populate_treeview)
    show_button.grid(row=0, column=3)

    back_image = PhotoImage(file='image\\back .png')
    back_button = Button(item_frame, image=back_image, border=0, cursor='hand2', bg='#DFF2EB',
                         activebackground='#DFF2EB', command=lambda: item_frame.place_forget())
    back_button.place(x=13, y=35)

    # -----------------------------------------
    detail_frame = Frame(item_frame, bg='#DFF2EB')
    detail_frame.place(x=150, y=100)
    # Configure the columns for consistent spacing and alignment
    for col in range(6):
        detail_frame.grid_columnconfigure(col, weight=1)

    # Set the labels and entries with proper alignment
    sbill_id_label = Label(detail_frame, text='Bill No', font=('times new roman', 13), bg='#DFF2EB',
                       height=1)
    sbill_id_label.grid(row=0, column=0, sticky='e', padx=15, pady=5)
    sbill_id_entry = Entry(detail_frame, font=('times new roman', 12))
    sbill_id_entry.grid(row=0, column=1, padx=5, pady=5)
    sbill_id_entry.bind("<FocusIn>", lambda event: on_billno_click(event, sbill_id_entry))

    sal_id_label = Label(detail_frame, text='Sales Id', font=('times new roman', 13), bg='#DFF2EB', height=1)
    sal_id_label.grid(row=1, column=0, sticky='e', padx=15, pady=5)
    sal_id_combobox = ttk.Combobox(detail_frame, width=18,values=populate_sales_ids(),
                                      font=('times new roman', 12), state='readonly')
    sal_id_combobox.set('Select Id')
    sal_id_combobox.grid(row=1, column=1, padx=15, pady=5)


    s_date_label = Label(detail_frame, text='Date', font=('times new roman', 13), bg='#DFF2EB', height=1)
    s_date_label.grid(row=2, column=0, sticky='e', padx=15, pady=5)
    s_date_entry = DateEntry(detail_frame, width=18, font=('times new roman', 12), state='readonly',
                             date_pattern='dd/mm/yy')
    s_date_entry.grid(row=2, column=1, padx=5, pady=5)

    s_cust_name_label = Label(detail_frame, text='Customer Name', font=('times new roman', 13), bg='#DFF2EB', height=1)
    s_cust_name_label.grid(row=3, column=0, sticky='e', padx=15, pady=5)
    s_cust_name_entry = Entry(detail_frame, font=('times new roman', 12))
    s_cust_name_entry.grid(row=3, column=1, padx=5, pady=5)

    s_item_nm_label = Label(detail_frame, text='Item Name', font=('times new roman', 13), bg='#DFF2EB', height=1)
    s_item_nm_label.grid(row=0, column=2, sticky='e', padx=15, pady=5)
    s_item_nm_entry = Entry(detail_frame, font=('times new roman', 12))
    s_item_nm_entry.grid(row=0, column=3, padx=5, pady=5)

    s_price_label = Label(detail_frame, text='Price', font=('times new roman', 13), bg='#DFF2EB', height=1)
    s_price_label.grid(row=1, column=2, sticky='e', padx=15, pady=5)
    s_price_entry = Entry(detail_frame, font=('times new roman', 12))
    s_price_entry.grid(row=1, column=3, padx=5, pady=5)


    s_qty_label = Label(detail_frame, text='Quantity', font=('times new roman', 13), bg='#DFF2EB', height=1)
    s_qty_label.grid(row=2, column=2, sticky='e', padx=15, pady=5)
    s_qty_entry = Entry(detail_frame, font=('times new roman', 12))
    s_qty_entry.grid(row=2, column=3, padx=5, pady=5)

    s_total_label = Label(detail_frame, text='Amount', font=('times new roman', 13), bg='#DFF2EB', height=1)
    s_total_label.grid(row=3, column=2, sticky='e', padx=15, pady=5)
    s_total_entry = Entry(detail_frame, font=('times new roman', 12))
    s_total_entry.grid(row=3, column=3, padx=5, pady=5)

    s_gst_label = Label(detail_frame, text='Gst', font=('times new roman', 13), bg='#DFF2EB', height=1)
    s_gst_label.grid(row=0, column=4, sticky='e', padx=15, pady=5)
    s_gst_entry = Entry(detail_frame, font=('times new roman', 12))
    s_gst_entry.grid(row=0, column=5, padx=5, pady=5)

    s_dis_label = Label(detail_frame, text='Discount', font=('times new roman', 13), bg='#DFF2EB', height=1)
    s_dis_label.grid(row=1, column=4, sticky='e', padx=15, pady=5)
    s_dis_entry = Entry(detail_frame, font=('times new roman', 12))
    s_dis_entry.grid(row=1, column=5, padx=5, pady=5)

    s_total_amt_label = Label(detail_frame, text='Total Amount', font=('times new roman', 13), bg='#DFF2EB', height=1)
    s_total_amt_label.grid(row=2, column=4, sticky='e', padx=15, pady=5)
    s_total_amt_entry = Entry(detail_frame, font=('times new roman', 12))
    s_total_amt_entry.grid(row=2, column=5, padx=5, pady=5)

    sal_id_combobox.bind("<<ComboboxSelected>>", lambda event: fill_sales_details(event, sal_id_combobox,
                                                                                  s_date_entry, s_cust_name_entry,
                                                                                  s_item_nm_entry, s_price_entry,
                                                                                  s_qty_entry, s_total_entry,
                                                                                  s_gst_entry, s_dis_entry,
                                                                                  s_total_amt_entry))

    # Adjusted Top Frame and Treeview placement
    top_frame = Frame(item_frame, bg='#DFF2EB')
    top_frame.place(x=0, y=330, relwidth=1, height=210)  # Placed at the bottom of item_frame

    # Create horizontal and vertical scrollbars
    horizontal_scrollbar = Scrollbar(top_frame, orient=HORIZONTAL)
    vertical_scrollbar = Scrollbar(top_frame, orient=VERTICAL)

    item_treeview = ttk.Treeview(top_frame, columns=(
        'billid','salid','date','custnm', 'itemname', 'price', 'qty', 'amt', 'gst', 'dis','ttl'), show='headings',
                                 yscrollcommand=vertical_scrollbar.set, xscrollcommand=horizontal_scrollbar.set)

    horizontal_scrollbar.pack(side=BOTTOM, fill=X, pady=(0, 0), padx=(0, 0))
    vertical_scrollbar.pack(side=RIGHT, fill=Y, pady=(0, 0), padx=(0, 0))
    horizontal_scrollbar.config(command=item_treeview.xview)
    vertical_scrollbar.config(command=item_treeview.yview)
    item_treeview.pack(fill=BOTH, expand=True, pady=(0, 0))

    item_treeview.heading('billid', text='Bill Id')
    item_treeview.heading('salid', text='sales Id')
    item_treeview.heading('date', text='Date')
    item_treeview.heading('custnm', text='Customer Name')
    item_treeview.heading('itemname', text='Item Name')
    item_treeview.heading('price', text='Price')
    item_treeview.heading('qty', text='Quantity')
    item_treeview.heading('amt', text='Amount')
    item_treeview.heading('gst', text='Gst')
    item_treeview.heading('dis', text='Discount')
    item_treeview.heading('ttl', text='Total')


    item_treeview.column('billid', width=180)
    item_treeview.column('salid', width=180)
    item_treeview.column('date', width=180)
    item_treeview.column('custnm', width=180)
    item_treeview.column('itemname', width=180)
    item_treeview.column('price', width=180)
    item_treeview.column('qty', width=180)
    item_treeview.column('amt', width=170)
    item_treeview.column('gst', width=180)
    item_treeview.column('dis', width=180)
    item_treeview.column('ttl', width=170)

    populate_treeview()
    # After initializing the Treeview and defining its columns
    item_treeview.bind("<ButtonRelease-1>", lambda event: on_treeview_select(event,sbill_id_entry,sal_id_combobox,s_date_entry,s_cust_name_entry,s_item_nm_entry,s_price_entry,s_qty_entry,s_total_entry,s_gst_entry,s_dis_entry,s_total_amt_entry))

    button_frame = Frame(item_frame, bg='#DFF2EB')
    button_frame.place(x=300, y=270)

    add_button = Button(button_frame, text='Add', font=('times new roman', 13), cursor='hand1', width=10,
                        bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                        command=lambda: add_data(sbill_id_entry, sal_id_combobox, s_date_entry, s_cust_name_entry,
                                                 s_item_nm_entry, s_price_entry, s_qty_entry, s_total_entry,
                                                 s_gst_entry, s_dis_entry, s_total_amt_entry))
    add_button.grid(row=0, column=0, padx=10)

    clear_button = Button(button_frame, text='Clear', font=('times new roman', 13), cursor='hand1', width=10,
                        bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,command=lambda: clear_form(sbill_id_entry, sal_id_combobox, s_date_entry, s_cust_name_entry,
                                                 s_item_nm_entry, s_price_entry, s_qty_entry, s_total_entry,
                                                 s_gst_entry, s_dis_entry, s_total_amt_entry))
    clear_button.grid(row=0, column=1, padx=10)

    report_button = Button(button_frame, text='Report', font=('times new roman', 13), cursor='hand1', width=10,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                           command=lambda: on_report_button_click(search_combobox,
                                                                  search_entry))  # Updated function for report generation
    report_button.grid(row=0, column=4, padx=10)

    # Add the Fetch button
    fetch_button = Button(button_frame, text='View', font=('times new roman', 13), cursor='hand1', width=10,
                          bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                          command=open_pdf_report)
    fetch_button.grid(row=0, column=5, padx=10)

    # Updating the pay button to trigger the QR code generation
    pay_button = Button(button_frame, text='Payment', font=('times new roman', 13), cursor='hand1', width=10,
                        bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                        command=lambda :on_payment_button_click(s_total_amt_entry))  # Assign the button's command to the handler
    pay_button.grid(row=0, column=6, padx=10)



