from tkinter import *
import tkinter as tk
from tkinter import colorchooser
import webcolors
import pymysql
from reportlab.pdfgen import canvas
from tkinter import filedialog
import os
import tkinter.messagebox as messagebox
from tkinter import ttk, PhotoImage, Entry, Frame, Label, Button, Text, Scrollbar, HORIZONTAL, VERTICAL, BOTH, END


# Connect to MySQL
conn = pymysql.connect(
    host="localhost",      # Change if needed
    user="root",           # Your MySQL username
    password="1234",           # Your MySQL password
    database="handloom"    # Target database
)

# Create a cursor
cursor = conn.cursor()

create_item_table_query = """
CREATE TABLE IF NOT EXISTS item (
    itemid INT PRIMARY KEY,               -- Item ID
    itemname VARCHAR(255) NOT NULL,        -- Item Name
    itemtype VARCHAR(100) NOT NULL,        -- Item Type
    itemcolor VARCHAR(100),                -- Item Color
    itemsize VARCHAR(50),                  -- Item Size
    qty INT NOT NULL,                      -- Quantity
    price DECIMAL(10, 2) NOT NULL
);
"""

# Execute the query to create the item table
cursor.execute(create_item_table_query)
conn.commit()
print("Item table created successfully!")

# Close connection
cursor.close()
conn.close()


def add_item(iid_entry, iname_entry, itype_text, icolor_entry, isize_entry, iqty_entry, iprice_entry):
    conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
    cursor = conn.cursor()

    # Get data from entry fields
    itemid = iid_entry.get().strip()
    itemname = iname_entry.get().strip()
    itemtype = itype_text.get().strip()
    itemcolor = icolor_entry.get().strip()
    itemsize = isize_entry.get().strip()
    qty = iqty_entry.get().strip()
    price = iprice_entry.get().strip()

    # ========== VALIDATIONS ========== #
    # 1. Check if any field is empty
    if not all([itemid, itemname, itemtype, itemcolor, itemsize, qty, price]):
        messagebox.showerror("Error", "All fields are required!")
        return

    # 2. Validate Item ID (Only digits)
    if not itemid.isdigit():
        messagebox.showerror("Error", "Item ID should contain only numbers!")
        return

    # 3. Validate Quantity (Only digits)
    if not qty.isdigit():
        messagebox.showerror("Error", "Quantity should be a valid number!")
        return

    # 4. Ensure Quantity does not exceed 100
    if int(qty) > 100:
        messagebox.showerror("Error", "Quantity should not be more than 100!")
        return

    # 5. Validate Price (Should be a valid decimal number)
    try:
        price = float(price)
    except ValueError:
        messagebox.showerror("Error", "Price must be a valid number!")
        return

    # 6. Check if itemid already exists
    cursor.execute("SELECT * FROM item WHERE itemid = %s", (itemid,))
    existing_record = cursor.fetchone()

    if existing_record:
        messagebox.showerror("Error", "Item ID already exists!")
        return

    # Insert into database
    try:
        query = """INSERT INTO item (itemid, itemname, itemtype, itemcolor, itemsize, qty, price) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (itemid, itemname, itemtype, itemcolor, itemsize, qty, price))
        conn.commit()
        messagebox.showinfo("Success", "Item added successfully!")
        fetch_item_data()  # Assuming this function fetches and updates the item table view
        clear_item_fields()  # Assuming this function clears the item fields after insertion
    except pymysql.IntegrityError:
        messagebox.showerror("Error", "Error while adding the item.")
    finally:
        cursor.close()
        conn.close()


def update_item(iid_entry, iname_entry, itype_text, icolor_entry, isize_entry, iqty_entry, iprice_entry):
    selected = item_treeview.selection()
    if not selected:
        messagebox.showerror('Error', 'No row is selected')
        return

    conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
    cursor = conn.cursor()

    try:
        # Get selected item ID
        content = item_treeview.item(selected)
        itemid = content['values'][0]  # Extract itemid from selected row

        # Check if item exists in the database
        cursor.execute('SELECT * FROM item WHERE itemid = %s', (itemid,))
        current_data = cursor.fetchone()

        if not current_data:
            messagebox.showerror("Error", "Item not found!")
            return

        # Extract current data for comparison
        current_data = current_data[1:]  # Exclude itemid from the existing data
        new_data = (
            iname_entry.get().strip(),
            itype_text.get().strip(),
            icolor_entry.get().strip(),
            isize_entry.get().strip(),
            iqty_entry.get().strip(),
            iprice_entry.get().strip(),
        )

        # Validate that all fields have been filled out
        if not all(new_data):
            messagebox.showerror("Error", "All fields are required!")
            return

        # Validate Quantity (Only digits)
        if not new_data[4].isdigit():
            messagebox.showerror("Error", "Quantity should be a valid number!")
            return

        # Ensure Quantity does not exceed 100
        if int(new_data[4]) > 100:
            messagebox.showerror("Error", "Quantity should not be more than 100!")
            return

        # Validate Price (Should be a valid decimal number)
        try:
            price = float(new_data[5])
        except ValueError:
            messagebox.showerror("Error", "Price must be a valid number!")
            return

        # Check if the new data is the same as the current data
        if current_data == new_data:
            messagebox.showinfo('Information', 'No changes detected')
            return

        # Update item details in the database
        cursor.execute(
            """UPDATE item SET itemname=%s, itemtype=%s, itemcolor=%s, itemsize=%s, qty=%s, price=%s WHERE itemid=%s""",
            (new_data[0], new_data[1], new_data[2], new_data[3], new_data[4], new_data[5], itemid)
        )
        conn.commit()

        fetch_item_data()  # Refresh data in Treeview
        messagebox.showinfo('Success', 'Item details updated successfully!')
        clear_item_fields()

    except Exception as e:
        messagebox.showerror('Error', f'Error occurred: {e}')

    finally:
        cursor.close()
        conn.close()


def delete_item():
    selected = item_treeview.selection()  # Get the selected item from the treeview
    if not selected:
        messagebox.showerror('Error', 'No row is selected')  # Show error if no item is selected
        return

    # Ask user for confirmation before deleting
    result = messagebox.askyesno('Confirm', 'Do you really want to delete the selected item?')
    if result:
        conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
        cursor = conn.cursor()

        try:
            # Get the selected item's ID (assuming 'itemid' is the first column)
            content = item_treeview.item(selected)
            itemid = content['values'][0]  # Extract the 'itemid' from the row values

            # Perform the deletion in the database
            cursor.execute('DELETE FROM item WHERE itemid=%s', (itemid,))
            conn.commit()

            # Refresh the TreeView after deletion
            fetch_item_data()
            messagebox.showinfo('Success', 'Item record deleted successfully!')  # Show success message

        except Exception as e:
            messagebox.showerror('Error', f'Error occurred: {e}')  # Handle any exceptions
        finally:
            cursor.close()
            conn.close()  # Close the cursor and connection

def clear_item_fields(iid_entry, iname_combobox, itype_combobox, icolor_entry, isize_combobox, iqty_entry, iprice_entry):
    iid_entry.delete(0, tk.END)
    iname_combobox.set('Select Item Name')  # Reset combobox
    itype_combobox.set('Select Item Type')
    icolor_entry.delete(0, tk.END)
    isize_combobox.set('Select Item Size')
    iqty_entry.delete(0, tk.END)
    iprice_entry.delete(0, tk.END)


item_types = {
    'Bedsheet': ['Cotton', 'Bamboo', 'Polyester', 'Linen', 'Tencel™', 'Silk', 'Microfiber', 'Satin'],
    'Blanket': ['Cotton', 'Polyester', 'Microfiber', 'Silk'],
    'Towel': ['Cotton', 'Bamboo', 'Microfiber', 'Polyester'],
    'Napkeen': ['Cotton', 'Polyester'],
    'cushion': ['Cotton', 'Polyester', 'Silk', 'Microfiber'],
    'Shawl': ['Silk', 'Cotton', 'Linen', 'Satin']
}
item_size_options = {
    'Bedsheet': ['60x60', '72x72', '90x90', '108x108'],  # Sizes for bedsheets
    'Blanket': ['Single', 'Double', 'King'],  # Sizes for blankets
    'Towel': ['Small', 'Medium', 'Large'],  # Sizes for towels
    'Napkeen': ['Standard', 'Large'],  # Sizes for napkeen
    'Cushion': ['12x12', '16x16', '18x18'],  # Sizes for cushion
    'Shawl': ['Small', 'Medium', 'Large']  # Sizes for shawl
}

def on_item_name_select(event, iname_combobox, itype_combobox, isize_combobox):
    selected_item = iname_combobox.get()

    # Update Item Type Combobox based on selected item
    if selected_item in item_types:
        itype_combobox['values'] = item_types[selected_item]
        itype_combobox.set('Select Item Type')  # Reset to default text

    if selected_item in item_size_options:
        isize_combobox['values'] = item_size_options[selected_item]
        isize_combobox.set('Select Item Size')  # Reset to default text
    else:
        isize_combobox['values'] = []  # No options for unrecognized item
        isize_combobox.set('Select Item Size')  # Reset to default text


def fetch_item_data():
    conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM item")
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
def select_item_data(event, iid_entry, iname_combobox, itype_combobox, icolor_entry, isize_combobox, iqty_entry, iprice_entry):
    """Handles the selection of an item record from the Treeview and populates the form fields."""

    # Get selected item
    index = item_treeview.selection()
    if not index:
        return  # If no selection, return early

    content = item_treeview.item(index)
    row = content['values']

    # Clear existing data in fields
    clear_item_fields(iid_entry, iname_combobox, itype_combobox, icolor_entry, isize_combobox, iqty_entry, iprice_entry)

    # Populate fields with selected data
    iid_entry.insert(0, row[0])  # Item ID
    iname_combobox.set(row[1])  # Item Name
    itype_combobox.set(row[2])  # Item Type
    icolor_entry.insert(0, row[3])  # Item Color
    isize_combobox.set(row[4])  # Item Size (Fixed the issue here)
    iqty_entry.insert(0, row[5])  # Quantity
    iprice_entry.insert(0, row[6])  # Price

def search_item_data(search_combobox, search_entry):
    search_criteria = search_combobox.get().strip()
    search_value = search_entry.get().strip()

    if not search_value:
        messagebox.showerror("Error", "Please enter a value to search.")
        return

    conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
    cursor = conn.cursor()

    try:
        if search_criteria == "Id":
            query = "SELECT * FROM item WHERE itemid = %s"
            cursor.execute(query, (search_value,))
        elif search_criteria == "Name":
            query = "SELECT * FROM item WHERE itemname LIKE %s"
            cursor.execute(query, ('%' + search_value + '%',))
        elif search_criteria == "All":
            query = "SELECT * FROM item"
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

    # Define the path for the PDF file (dynamically named based on company name or 'All' for all records)
    report_path = os.path.join(folder_selected, report_name + ".pdf")

    try:
        # Increase the page width if necessary (for wider tables)
        page_width = 700  # Custom width to increase space on the page
        page_height = 1100  # Standard height (you can adjust this as well)

        # Create a canvas object to generate the PDF
        pdf = canvas.Canvas(report_path, pagesize=(page_width, page_height))
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(270, 1050, "Item Report")

        # Set font for table headers and data
        pdf.setFont("Helvetica", 10)

        # Adjusted column widths with increased width for Address and City
        col_widths = [100, 100, 100, 100, 100, 100,100]  # Address and City columns increased

        # Draw table headers
        header = ["Item Id", "Item Name","Item Type", "Item Color", "Item Size", "Quantity", "Price"]
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
            query = "SELECT * FROM item WHERE itemid = %s"
            cursor.execute(query, (search_value,))
            report_name = f"Item_Report_{search_value}"  # Dynamic name for the report
        elif search_criteria == "Name":
            query = "SELECT * FROM item WHERE itemname LIKE %s"
            cursor.execute(query, ('%' + search_value + '%',))
            report_name = f"Item_Report_{search_value}"  # Dynamic name for the report
        elif search_criteria == "All":
            query = "SELECT * FROM item"
            cursor.execute(query)
            report_name = "Item_Report_All"  # Generic name for all companies

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
45



def item_form(window):
    global back_image,item_treeview
    item_frame = Frame(window, width=1270, height=542,bg='#DFF2EB')
    item_frame.place(x=0, y=99)
    heading_label = Label(item_frame, text='Manage Item Detail', font=('times new roman', 18, 'bold'),fg='white',
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
                           border=2,
                           command=lambda: search_item_data(search_combobox, search_entry))
    search_button.grid(row=0, column=2, padx=20)

    show_button = Button(search_frame, text='Show All', font=('times new roman', 13), cursor='hand1', width=10,
                         bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,command=fetch_item_data)
    show_button.grid(row=0, column=3)

    back_image = PhotoImage(file='image\\back .png')
    back_button = Button(item_frame, image=back_image, border=0, cursor='hand2', bg='#DFF2EB',
                         activebackground='#DFF2EB', command=lambda: item_frame.place_forget())
    back_button.place(x=13, y=35)

    detail_frame = Frame(item_frame, bg='#DFF2EB')
    detail_frame.place(x=140,y=110)

    iid_label = Label(detail_frame, text='Item Id', font=('times new roman', 13), bg='#DFF2EB',height=0,width=9)
    iid_label.grid(row=0, column=0, padx=15, pady=2, sticky='e')
    iid_entry = Entry(detail_frame, font=('times new roman', 13))
    iid_entry.grid(row=0, column=1, padx=5, pady=2)

    iname_label = Label(detail_frame, text='Item Name', font=('times new roman', 13), bg='#DFF2EB', height=2, width=12)
    iname_label.grid(row=1, column=0, padx=15, pady=2, sticky='e')

    iname_label = Label(detail_frame, text='Item Name', font=('times new roman', 13), bg='#DFF2EB', height=2, width=12)
    iname_label.grid(row=1, column=0, padx=15, pady=2, sticky='e')
    item_name_options = ['Bedsheet', 'Blanket', 'Towel', 'Napkeen', 'Cushion', 'Shawl']
    iname_combobox = ttk.Combobox(detail_frame, values=item_name_options, font=('times new roman', 13), width=18)
    iname_combobox.set('Select Item Name')  # Default text
    iname_combobox.grid(row=1, column=1, padx=5, pady=2)
    iname_combobox.bind("<<ComboboxSelected>>", on_item_name_select)  # Bind to update Item Type on selection

    itype_label = tk.Label(detail_frame, text='Item Type', font=('times new roman', 13), bg='#DFF2EB', height=2,
                           width=12)
    itype_label.grid(row=2, column=0, padx=15, pady=2, sticky='e')

    itype_combobox = ttk.Combobox(detail_frame, font=('times new roman', 13), width=18)
    itype_combobox.set('Select Item Type')  # Default text
    itype_combobox.grid(row=2, column=1, padx=5, pady=2)

    # Bind the event to update Item Type when Item Name is selected
    iname_combobox.bind("<<ComboboxSelected>>",
                        lambda event: on_item_name_select(event, iname_combobox, itype_combobox))

    def hex_to_color_name(hex_code):
        try:
            return webcolors.hex_to_name(hex_code)
        except ValueError:
            return "Custom Color"  # Return "Custom Color" if no exact name is found

    # Function to open the color chooser dialog and update the Entry field with the color name
    def choose_color(event=None):
        color_code = colorchooser.askcolor(title="Choose a color")[1]  # Get the hex color
        if color_code:
            color_name = hex_to_color_name(color_code)  # Convert hex code to color name
            icolor_entry.delete(0, tk.END)  # Clear existing text in the entry
            icolor_entry.insert(0, color_name)  # Insert the color name

    icolor_label = Label(detail_frame, text='Item Color', font=('times new roman', 13),bg='#DFF2EB')
    icolor_label.grid(row=0, column=2, padx=15, pady=2, sticky='e')
    icolor_entry = Entry(detail_frame, font=('times new roman', 13))
    icolor_entry.grid(row=0, column=3, padx=5, pady=2)

    # Bind the entry widget to the color chooser function (using a mouse click or key press event)
    icolor_entry.bind("<Button-1>", choose_color)  # When the entry is clicked, show the color chooser

    # Item Size Label
    isize_label = Label(detail_frame, text='Item Size', font=('times new roman', 13), bg='#DFF2EB')
    isize_label.grid(row=1, column=2, padx=15, pady=2, sticky='e')

    isize_combobox = ttk.Combobox(detail_frame, values=[], font=('times new roman', 13), width=18)
    isize_combobox.set('Select Item Size')  # Default text
    isize_combobox.grid(row=1, column=3, padx=5, pady=2)

    iname_combobox.bind("<<ComboboxSelected>>",
                        lambda event: on_item_name_select(event, iname_combobox, itype_combobox, isize_combobox))

    iqty_label = Label(detail_frame, text='Quantity', font=('times new roman', 13), bg='#DFF2EB')
    iqty_label.grid(row=2, column=2, padx=15, pady=2, sticky='e')
    iqty_entry = Entry(detail_frame, font=('times new roman', 13))
    iqty_entry.grid(row=2, column=3, padx=15, pady=2)

    iprice_label = Label(detail_frame, text='Price', font=('times new roman', 13), bg='#DFF2EB')
    iprice_label.grid(row=0, column=4, padx=15, pady=2, sticky='e')
    iprice_entry = Entry(detail_frame, font=('times new roman', 13))
    iprice_entry.grid(row=0, column=5, padx=5, pady=2)



    # -----------------------------------------------------------------------

    button_frame = Frame(item_frame, bg='#DFF2EB')
    button_frame.place(x=280,y=260)

    add_button = Button(button_frame, text='Add', font=('times new roman', 13), cursor='hand1', width=10,
                        bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                        command=lambda: add_item(iid_entry, iname_combobox, itype_combobox, icolor_entry, isize_combobox,
                                                 iqty_entry, iprice_entry))
    add_button.grid(row=0, column=0, padx=10)

    update_button = Button(button_frame, text='Update', font=('times new roman', 13), cursor='hand1', width=10,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                           command=lambda: update_item(iid_entry, iname_combobox, itype_combobox, icolor_entry, isize_combobox,
                                                       iqty_entry, iprice_entry))
    update_button.grid(row=0, column=1, padx=10)

    delete_button = Button(button_frame, text='Delete', font=('times new roman', 13), cursor='hand1', width=10,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                           command=delete_item)  # Binding the delete_item function to the Delete button
    delete_button.grid(row=0, column=2, padx=10)

    clear_button = Button(button_frame, text='Clear', font=('times new roman', 13), cursor='hand1', width=10,
                          bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,command=lambda :clear_item_fields(iid_entry, iname_combobox, itype_combobox, icolor_entry, isize_combobox, iqty_entry, iprice_entry))
    clear_button.grid(row=0, column=3, padx=10)

    report_button = Button(button_frame, text='Report', font=('times new roman', 13), cursor='hand1', width=10,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                           command=lambda: on_report_button_click(search_combobox,
                                                                  search_entry))  # Updated function for report generation
    report_button.grid(row=0, column=4, padx=10)

    # Add the Fetch button
    fetch_button = Button(button_frame, text='View', font=('times new roman', 13), cursor='hand1', width=10,
                          bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                          command=open_pdf_report)  # Call open_pdf_report function
    fetch_button.grid(row=0, column=5, padx=10)

    # -----------------------------------------------------------

    # Adjusted Top Frame and Treeview placement
    top_frame = Frame(item_frame, bg='#DFF2EB')
    top_frame.place(x=0, y=330, relwidth=1, height=210)  # Placed at the bottom of item_frame

    # Create horizontal and vertical scrollbars
    horizontal_scrollbar = Scrollbar(top_frame, orient=HORIZONTAL)
    vertical_scrollbar = Scrollbar(top_frame, orient=VERTICAL)

    item_treeview = ttk.Treeview(top_frame, columns=(
        'itemid', 'itemname', 'itemtype', 'itemcolor', 'itemsize', 'qty', 'price'), show='headings',
                                 yscrollcommand=vertical_scrollbar.set, xscrollcommand=horizontal_scrollbar.set)


    horizontal_scrollbar.pack(side=BOTTOM, fill=X, pady=(0, 0), padx=(0, 0))
    vertical_scrollbar.pack(side=RIGHT, fill=Y, pady=(0, 0), padx=(0, 0))
    horizontal_scrollbar.config(command=item_treeview.xview)
    vertical_scrollbar.config(command=item_treeview.yview)
    item_treeview.pack(fill=BOTH, expand=True, pady=(0, 0))

    item_treeview.heading('itemid', text='Item Id')
    item_treeview.heading('itemname', text='Item Name')
    item_treeview.heading('itemtype', text='Item Type')
    item_treeview.heading('itemcolor', text='Item Color')
    item_treeview.heading('itemsize', text='Item Size')
    item_treeview.heading('qty', text='Quantity')
    item_treeview.heading('price', text='Price')

    item_treeview.column('itemid', width=180)
    item_treeview.column('itemname', width=180)
    item_treeview.column('itemtype', width=180)
    item_treeview.column('itemcolor', width=180)
    item_treeview.column('itemsize', width=180)
    item_treeview.column('qty', width=180)
    item_treeview.column('price', width=170)
    fetch_item_data()

    item_treeview.bind("<ButtonRelease-1>",
                       lambda event: select_item_data(event, iid_entry, iname_combobox, itype_combobox, icolor_entry,
                                                      isize_combobox, iqty_entry, iprice_entry))