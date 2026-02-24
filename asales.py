from tkinter import *
from tkcalendar import DateEntry
from datetime import datetime
import pymysql
from tkinter import filedialog
import os
from reportlab.pdfgen import canvas
from tkinter import ttk, PhotoImage, Entry, Frame, Label, Button, Text, Scrollbar, HORIZONTAL, VERTICAL, BOTH, END



# Connect to MySQL
conn = pymysql.connect(
    host="localhost",      # Change if needed
    user="root",           # Your MySQL username
    password="1234",           # Your MySQL password
    database="handloom"    # Target database
)
cursor = conn.cursor()

create_sales_table_query = """
CREATE TABLE IF NOT EXISTS sales (
    salesid INT PRIMARY KEY,
    salesdate DATE NOT NULL,
    custid INT NOT NULL,
    custname VARCHAR(255) NOT NULL,
    itemid INT NOT NULL,
    itemname VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    saquantity INT NOT NULL,
    saamount DECIMAL(10, 2) NOT NULL,
    sagst DECIMAL(10, 2) NOT NULL,
    sadiscount DECIMAL(10, 2) NOT NULL,
    satotalamount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (custid) REFERENCES customer(custid),
    FOREIGN KEY (itemid) REFERENCES item(itemid)
);
"""

cursor.execute(create_sales_table_query)
conn.commit()
print("Sales table created successfully!")

def populate_customer_ids():
    # Open a new connection and cursor for the query
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="1234",
        database="handloom"
    )
    cursor = conn.cursor()

    # Query to fetch customer ids in ascending order
    cursor.execute("SELECT custid FROM customer ORDER BY custid ASC")

    # Fetching all customer ids
    customer_ids = cursor.fetchall()

    # Close the cursor and connection after use
    cursor.close()
    conn.close()

    # Return a list of customer ids
    return [str(row[0]) for row in customer_ids]  # return as a list of strings

# Function to auto-fill customer name based on selected customer ID
def on_customer_id_selected(event, cust_id_entry, cust_name_entry):
    # Get the selected customer ID
    selected_cust_id = cust_id_entry.get()

    if selected_cust_id:
        # Open a new connection and cursor for the query
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="1234",
            database="handloom"
        )
        cursor = conn.cursor()

        # Query to fetch customer name by custid
        cursor.execute("SELECT custname FROM customer WHERE custid = %s", (selected_cust_id,))

        # Fetch the customer name
        customer_name = cursor.fetchone()

        # If a customer name is found, fill the customer name entry
        if customer_name:
            cust_name_entry.delete(0, END)  # Clear existing text
            cust_name_entry.insert(0, customer_name[0])  # Insert the customer name

        # Close the cursor and connection after use
        cursor.close()
        conn.close()
def populate_item_ids():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="1234",
        database="handloom"
    )
    cursor = conn.cursor()

    # Query to fetch item ids in ascending order
    cursor.execute("SELECT itemid FROM item ORDER BY itemid ASC")
    item_ids = cursor.fetchall()

    cursor.close()
    conn.close()

    return [str(row[0]) for row in item_ids]  # return as a list of strings

# Function to auto-fill item name based on selected item ID
def populate_item_name(event, item_id_combobox, item_name_entry, item_price_entry):
    item_id = item_id_combobox.get()  # Get selected item ID

    if item_id:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="1234",
            database="handloom"
        )
        cursor = conn.cursor()

        # Query to fetch the item name and price based on the selected item ID
        cursor.execute("SELECT itemname, price FROM item WHERE itemid = %s", (item_id,))
        item_data = cursor.fetchone()

        if item_data:
            item_name, item_price = item_data
            # Fill the item name in the entry field
            item_name_entry.delete(0, END)
            item_name_entry.insert(0, item_name)

            # Fill the item price in the entry field
            item_price_entry.delete(0, END)
            item_price_entry.insert(0, str(item_price))

        cursor.close()
        conn.close()
from tkinter import messagebox
def on_amount_entry_click(s_price_entry, s_qty_entry, s_total_entry):
    try:
        # Get the price and quantity entered
        price = float(s_price_entry.get())
        quantity = int(s_qty_entry.get())

        # Calculate total amount (price * quantity)
        amount = price * quantity

        # Update the Amount entry field
        s_total_entry.delete(0, 'end')
        s_total_entry.insert(0, f"{amount:.2f}")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values for price and quantity.")
def on_gst_entry_click(s_total_entry, s_gst_entry):
    try:
        # Get the calculated amount
        amount = float(s_total_entry.get())

        # Calculate GST (15%)
        s_gst = amount * 0.15

        # Update the GST entry field
        s_gst_entry.delete(0, 'end')  # Clear existing value
        s_gst_entry.insert(0, str(s_gst))  # Insert calculated GST

    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid amount before calculating GST.")

def on_total_amount_entry_click(s_total_entry, s_gst_entry, s_dis_entry, s_total_amt_entry):
    try:
        # Get values from Amount, GST, and Discount fields
        amount = float(s_total_entry.get())
        gst = float(s_gst_entry.get())
        discount = float(s_dis_entry.get())

        # Convert discount percentage to a decimal
        discount_amount = (amount + gst) * (discount / 100)

        # Calculate total amount
        total_amount = (amount + gst) - discount_amount

        # Update the Total Amount entry field
        s_total_amt_entry.delete(0, 'end')  # Clear existing value
        s_total_amt_entry.insert(0, str(total_amount))  # Insert the calculated total amount

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numerical values for amount, GST, and discount.")

def add_sales_data(s_id_entry, s_date_entry, s_cust_id_combobox, s_cust_name_entry, s_item_id_combobox, s_item_nm_entry,
                   s_qty_entry, s_price_entry, s_total_entry, s_gst_entry, s_dis_entry, s_total_amt_entry):
    conn = None
    cursor = None
    try:
        # Retrieve values from the entry widgets
        sales_id = s_id_entry.get().strip()
        sales_date = s_date_entry.get_date() if s_date_entry.get_date() else None  # Ensure a valid date
        cust_id = s_cust_id_combobox.get().strip()
        cust_name = s_cust_name_entry.get().strip()
        item_id = s_item_id_combobox.get().strip()
        item_name = s_item_nm_entry.get().strip()

        # Validate numerical fields
        price = s_price_entry.get().strip()
        quantity = s_qty_entry.get().strip()
        total = s_total_entry.get().strip()
        gst = s_gst_entry.get().strip()
        discount = s_dis_entry.get().strip()
        total_amount = s_total_amt_entry.get().strip()

        if not sales_id or not sales_date:
            raise ValueError("Sales ID and Date are required.")
        if not cust_id or not cust_name:
            raise ValueError("Customer ID and Name are required.")
        if not item_id or not item_name:
            raise ValueError("Item ID and Name are required.")

        if not price or not quantity or not total or not gst or not discount or not total_amount:
            raise ValueError("Price, Quantity, Total, GST, Discount, and Total Amount are required.")

        # Convert price, quantity, total, gst, discount, and total_amount to appropriate types
        try:
            price = float(price)
        except ValueError:
            raise ValueError("Price must be a valid number.")

        try:
            quantity = int(quantity)
        except ValueError:
            raise ValueError("Quantity must be a valid integer.")

        try:
            total = float(total)
        except ValueError:
            raise ValueError("Total must be a valid number.")

        try:
            gst = float(gst)
        except ValueError:
            raise ValueError("GST must be a valid number.")

        try:
            discount = float(discount)
        except ValueError:
            raise ValueError("Discount must be a valid number.")

        try:
            total_amount = float(total_amount)
        except ValueError:
            raise ValueError("Total Amount must be a valid number.")

        # Connect to the database
        conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
        cursor = conn.cursor()

        # Check the available stock for the item
        stock_check_query = "SELECT qty FROM stock WHERE itemid = %s"
        cursor.execute(stock_check_query, (item_id,))
        stock_result = cursor.fetchone()

        if stock_result:
            available_stock = stock_result[0]
            if quantity > available_stock:
                raise ValueError(f"Insufficient stock. Available stock: {available_stock}")
        else:
            raise ValueError("Item not found in stock.")

        # Prepare the insert query
        insert_query = """
        INSERT INTO sales (salesid, salesdate, custid, custname, itemid, itemname, price, saquantity, saamount, sagst, 
                           sadiscount, satotalamount)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """  # 13 placeholders for 13 values

        # Execute the insert query
        cursor.execute(insert_query,
                       (sales_id, sales_date, cust_id, cust_name, item_id, item_name, price, quantity,
                        total, gst, discount, total_amount))

        # Commit the transaction
        conn.commit()

        # Update stock quantity after the sale
        update_stock_query = """
        UPDATE stock SET qty = qty - %s WHERE itemid = %s
        """
        cursor.execute(update_stock_query, (quantity, item_id))
        conn.commit()

        # Refresh the sales data and show a success message
        fetch_sales_data()
        messagebox.showinfo("Success", "Sales data added successfully!")

    except pymysql.MySQLError as e:
        messagebox.showerror("Database Error", f"Error: {e}")
    except ValueError as e:
        messagebox.showerror("Validation Error", f"Error: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        # Close cursor and connection if they were initialized
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def update_sales_data(s_id_entry, s_date_entry, s_cust_id_combobox, s_cust_name_entry, s_item_id_combobox,
                      s_item_nm_entry,
                      s_qty_entry, s_price_entry, s_total_entry, s_gst_entry, s_dis_entry, s_total_amt_entry):
    sales_id = s_id_entry.get().strip()
    sales_date = s_date_entry.get_date() if s_date_entry.get_date() else None  # Ensure a valid date
    cust_id = s_cust_id_combobox.get().strip()
    cust_name = s_cust_name_entry.get().strip()
    item_id = s_item_id_combobox.get().strip()
    item_name = s_item_nm_entry.get().strip()

    price = s_price_entry.get().strip()
    quantity = s_qty_entry.get().strip()
    total = s_total_entry.get().strip()
    gst = s_gst_entry.get().strip()
    discount = s_dis_entry.get().strip()
    total_amount = s_total_amt_entry.get().strip()

    if not sales_id or not sales_date:
        messagebox.showerror("Validation Error", "Sales ID and Date are required.")
        return
    if not cust_id or not cust_name:
        messagebox.showerror("Validation Error", "Customer ID and Name are required.")
        return
    if not item_id or not item_name:
        messagebox.showerror("Validation Error", "Item ID and Name are required.")
        return

    # Convert values to appropriate types
    try:
        price = float(price)
        quantity = int(quantity)
        total = float(total)
        gst = float(gst)
        discount = float(discount)
        total_amount = float(total_amount)
    except ValueError:
        messagebox.showerror("Validation Error", "Please ensure all numerical fields are correct.")
        return

    try:
        conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
        cursor = conn.cursor()

        # Check available stock for the item before updating the sale quantity
        stock_check_query = "SELECT qty FROM stock WHERE itemid = %s"
        cursor.execute(stock_check_query, (item_id,))
        stock_result = cursor.fetchone()

        if stock_result:
            available_stock = stock_result[0]
            if quantity > available_stock:
                messagebox.showerror("Validation Error", f"Insufficient stock. Available stock: {available_stock}")
                return
        else:
            messagebox.showerror("Error", "Item not found in stock.")
            return

        # Prepare the update query
        update_query = """
        UPDATE sales
        SET salesdate = %s, custid = %s, custname = %s, itemid = %s, itemname = %s, price = %s, saquantity = %s, 
            saamount = %s, sagst = %s, sadiscount = %s, satotalamount = %s WHERE salesid = %s
        """

        # Execute the update query
        cursor.execute(update_query, (
            sales_date, cust_id, cust_name, item_id, item_name, price, quantity, total, gst, discount, total_amount, sales_id))

        # Commit the transaction
        conn.commit()
        fetch_sales_data()

        if cursor.rowcount > 0:
            messagebox.showinfo("Success", "Sales data updated successfully!")
        else:
            messagebox.showerror("Error", "Sales data not found with the provided Sales ID.")

    except pymysql.MySQLError as e:
        messagebox.showerror("Database Error", f"Error: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

def delete_sales(s_id_entry):
    try:
        # Retrieve the sales ID from the entry widget
        sales_id = s_id_entry.get().strip()

        if not sales_id:
            raise ValueError("Sales ID is required to delete a record.")

        # Connect to the database
        conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
        cursor = conn.cursor()

        # Prepare the delete query
        delete_query = """
        DELETE FROM sales WHERE salesid = %s
        """

        # Execute the delete query
        cursor.execute(delete_query, (sales_id,))

        # Commit the transaction
        conn.commit()

        # Refresh the Treeview to reflect the deleted record
        fetch_sales_data()  # Assuming you have a function to fetch and refresh data in your UI

        messagebox.showinfo("Success", "Sales record deleted successfully!")


    except pymysql.MySQLError as e:
        messagebox.showerror("Database Error", f"Error: {e}")
    except ValueError as e:
        messagebox.showerror("Validation Error", f"Error: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()


# Function to clear all fields
def clear_all_fields(s_id_entry, s_date_entry, s_cust_id_combobox, s_cust_name_entry,
                     s_item_id_combobox, s_item_nm_entry, s_price_entry, s_qty_entry,
                     s_total_entry, s_gst_entry, s_dis_spinbox, s_total_amt_entry):
    s_id_entry.delete(0, END)  # Clear the sales ID entry
    s_date_entry.set_date(datetime.today().date())  # Set the date entry to today's date
    s_cust_id_combobox.set('Select Id')  # Reset customer ID combobox
    s_cust_name_entry.delete(0, END)  # Clear the customer name entry
    s_item_id_combobox.set('Select Id')  # Reset item ID combobox
    s_item_nm_entry.delete(0, END)  # Clear the item name entry
    s_price_entry.delete(0, END)  # Clear the price entry
    s_qty_entry.delete(0, END)  # Clear the quantity entry
    s_total_entry.delete(0, END)  # Clear the total entry
    s_gst_entry.delete(0, END)  # Clear the GST entry
    s_dis_spinbox.delete(0, END)  # Clear the discount Spinbox value
    s_dis_spinbox.insert(0, 0)  # Reset the discount Spinbox to 0
    s_total_amt_entry.delete(0, END)  # Clear the total amount entry

def fetch_sales_data():
    try:
        # Connect to the database
        conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
        cursor = conn.cursor()

        # Prepare the select query to fetch all sales data
        select_query = """
        SELECT salesid, salesdate, custid, custname, itemid, itemname, price, saquantity, saamount, sagst, sadiscount, satotalamount
        FROM sales
        """

        # Execute the select query
        cursor.execute(select_query)
        result = cursor.fetchall()

        # Clear existing data in the Treeview before inserting new data
        for row in sales_treeview.get_children():
            sales_treeview.delete(row)

        # Populate Treeview with fetched data
        for row in result:
            sales_treeview.insert("", "end", values=row)

    except pymysql.MySQLError as e:
        messagebox.showerror("Database Error", f"Error: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

def on_treeview_select(event, s_id_entry, s_date_entry, s_cust_id_combobox, s_cust_name_entry,
                       s_item_id_combobox, s_item_name_entry, s_price_entry, s_qty_entry,
                       s_amt_entry, s_gst_entry, s_dis_spinbox, s_total_amt_entry):
    selected_item = sales_treeview.selection()

    if selected_item:
        selected_data = sales_treeview.item(selected_item[0])["values"]

        if len(selected_data) < 12:  # Adjusted to 14 fields
            print("Warning: Selected row does not have enough data.")
            return

        s_id_entry.delete(0, END)
        s_id_entry.insert(0, selected_data[0])

        try:
            original_date = selected_data[1]
            valid_date = datetime.strptime(original_date, "%Y-%m-%d").date()
            s_date_entry.set_date(valid_date)
        except ValueError:
            print(f"Invalid date format: {selected_data[1]}")
            s_date_entry.set_date(datetime.today().date())

        s_cust_id_combobox.set(selected_data[2])
        s_cust_name_entry.delete(0, END)
        s_cust_name_entry.insert(0, selected_data[3])

        s_item_id_combobox.set(selected_data[4])
        s_item_name_entry.delete(0, END)
        s_item_name_entry.insert(0, selected_data[5])

        s_price_entry.delete(0, END)
        s_price_entry.insert(0, selected_data[6])

        s_qty_entry.delete(0, END)
        s_qty_entry.insert(0, selected_data[7])

        s_amt_entry.delete(0, END)
        s_amt_entry.insert(0, selected_data[8])

        s_gst_entry.delete(0, END)
        s_gst_entry.insert(0, selected_data[9])

        # Set the discount value using the Spinbox
        s_dis_spinbox.delete(0, END)  # Reset the current value in the Spinbox
        s_dis_spinbox.insert(0, selected_data[10])  # Set the new value for the discount

        s_total_amt_entry.delete(0, END)
        s_total_amt_entry.insert(0, selected_data[11])

def search_sales_data(search_combobox, search_entry):
    search_criteria = search_combobox.get().strip()
    search_value = search_entry.get().strip()

    if not search_value:
        messagebox.showerror("Error", "Please enter a value to search.")
        return

    conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
    cursor = conn.cursor()

    try:
        if search_criteria == "Id":
            query = "SELECT * FROM sales WHERE salesid = %s"
            cursor.execute(query, (search_value,))
        elif search_criteria == "Name":
            query = "SELECT * FROM sales WHERE itemname LIKE %s"
            cursor.execute(query, ('%' + search_value + '%',))
        elif search_criteria == "All":
            query = "SELECT * FROM sales"
            cursor.execute(query)

        records = cursor.fetchall()

        # Clear existing data in Treeview
        sales_treeview.delete(*sales_treeview.get_children())

        for row in records:
            sales_treeview.insert("", "end", values=row)

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
        page_width = 1200  # Custom width to increase space on the page
        page_height = 1100  # Standard height (you can adjust this as well)

        # Create a canvas object to generate the PDF
        pdf = canvas.Canvas(report_path, pagesize=(page_width, page_height))
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(550, 1050, "Sales Report")

        # Set font for table headers and data
        pdf.setFont("Helvetica", 10)

        # Adjusted column widths with increased width for Address and City
        col_widths = [100, 100, 100, 100, 100, 100,100,100, 100, 100, 100, 100]  # Address and City columns increased

        # Draw table headers
        header = ["Sales Id", "Sales Date","Customer Id", "Customer Name", "Item Id","Item Name", "Price","Quantity", "Amount","Gst","Discount","Total Amount"]
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
            query = "SELECT * FROM sales WHERE salesid = %s"
            cursor.execute(query, (search_value,))
            report_name = f"Sales_Report_{search_value}"  # Dynamic name for the report
        elif search_criteria == "Name":
            query = "SELECT * FROM sales WHERE itemname LIKE %s"
            cursor.execute(query, ('%' + search_value + '%',))
            report_name = f"Sales_Report_{search_value}"  # Dynamic name for the report
        elif search_criteria == "All":
            query = "SELECT * FROM sales"
            cursor.execute(query)
            report_name = "Sales_Report_All"  # Generic name for all companies

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




def sales_form(window):
    global back_image,sales_treeview
    item_frame = Frame(window, width=1270, height=542,bg='#DFF2EB')
    item_frame.place(x=0, y=99)
    heading_label = Label(item_frame, text='Manage Sales Detail', font=('times new roman', 18, 'bold'),fg='white',
                          bg='#7AB2D3')
    heading_label.place(x=0, y=0, relwidth='1')

    #---top frame
    top_frame = Frame(item_frame, bg='#DFF2EB')
    top_frame.place(x=0, y=40, relwidth=1, height=200)
    search_frame = Frame(top_frame, bg='#DFF2EB')
    search_frame.pack()

    search_combobox = ttk.Combobox(search_frame, values=('Id', 'Name','All'), font=('times new roman', 13),
                                   state='readonly')
    search_combobox.set('Search By')
    search_combobox.grid(row=0, column=0, padx=20)

    search_entry = Entry(search_frame, font=('times new roman', 13))
    search_entry.grid(row=0, column=1)

    search_button = Button(search_frame, text='Search', font=('times new roman', 13), cursor='hand1', width=10,
                           height=0,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,command=lambda: search_sales_data(search_combobox, search_entry))
    search_button.grid(row=0, column=2, padx=20)

    show_button = Button(search_frame, text='Show All', font=('times new roman', 13), cursor='hand1', width=10,
                         bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,command=fetch_sales_data)
    show_button.grid(row=0, column=3)

    back_image = PhotoImage(file='image\\back .png')
    back_button = Button(item_frame, image=back_image, border=0, cursor='hand2', bg='#DFF2EB',
                         activebackground='#DFF2EB', command=lambda: item_frame.place_forget())
    back_button.place(x=13, y=35)

    detail_frame = Frame(item_frame, bg='#DFF2EB')
    detail_frame.place(x=150, y=110)

    # Configure the columns for consistent spacing and alignment
    for col in range(6):
        detail_frame.grid_columnconfigure(col, weight=1)

    # Set the labels and entries with proper alignment
    s_id_label = Label(detail_frame, text='Sales Id', font=('times new roman', 13), bg='#DFF2EB',
                           height=1)
    s_id_label.grid(row=0, column=0, sticky='e', padx=15, pady=5)
    s_id_entry = Entry(detail_frame, font=('times new roman', 12))
    s_id_entry.grid(row=0, column=1, padx=5, pady=5)

    s_date_label = Label(detail_frame, text='Sales Date', font=('times new roman', 13), bg='#DFF2EB', height=1)
    s_date_label.grid(row=1, column=0, sticky='e', padx=15, pady=5)
    s_date_entry = DateEntry(detail_frame, width=18, font=('times new roman', 12), state='readonly',
                                    date_pattern='dd/mm/yy')
    s_date_entry.grid(row=1, column=1, padx=5, pady=5)


    s_cust_id_label = Label(detail_frame, text='Customer Id', font=('times new roman', 13), bg='#DFF2EB', height=1)
    s_cust_id_label.grid(row=2, column=0, sticky='e', padx=15, pady=5)
    s_cust_id_combobox = ttk.Combobox(detail_frame, width=18,values=populate_customer_ids(),
                                      font=('times new roman', 12), state='readonly')
    s_cust_id_combobox.set('Select Id')
    s_cust_id_combobox.grid(row=2, column=1, padx=15, pady=5)

    s_cust_name_label = Label(detail_frame, text='Customer Name', font=('times new roman', 13), bg='#DFF2EB', height=1)
    s_cust_name_label.grid(row=3, column=0, sticky='e', padx=15, pady=5)
    s_cust_name_entry = Entry(detail_frame, font=('times new roman', 12))
    s_cust_name_entry.grid(row=3, column=1, padx=5, pady=5)

    s_cust_id_combobox.bind("<<ComboboxSelected>>",
                            lambda event: on_customer_id_selected(event, s_cust_id_combobox, s_cust_name_entry))

    s_item_id_label = Label(detail_frame, text='Item Id', font=('times new roman', 13), bg='#DFF2EB',
                            height=1)
    s_item_id_label.grid(row=0, column=2, sticky='e', padx=15, pady=5)
    s_item_id_combobox = ttk.Combobox(detail_frame, width=18,values=populate_item_ids(),
                                      font=('times new roman', 12), state='readonly')
    s_item_id_combobox.set('Select Id')
    s_item_id_combobox.grid(row=0, column=3, padx=15, pady=5)

    s_item_nm_label = Label(detail_frame, text='Item Name', font=('times new roman', 13), bg='#DFF2EB', height=1)
    s_item_nm_label.grid(row=1, column=2, sticky='e', padx=15, pady=5)
    s_item_nm_entry = Entry(detail_frame, font=('times new roman', 12))
    s_item_nm_entry.grid(row=1, column=3, padx=5, pady=5)

    s_price_label = Label(detail_frame, text='Price', font=('times new roman', 13), bg='#DFF2EB', height=1)
    s_price_label.grid(row=2, column=2, sticky='e', padx=15, pady=5)
    s_price_entry = Entry(detail_frame, font=('times new roman', 12))
    s_price_entry.grid(row=2, column=3, padx=5, pady=5)

    s_item_id_combobox.bind("<<ComboboxSelected>>",
                          lambda event: populate_item_name(event, s_item_id_combobox, s_item_nm_entry, s_price_entry))

    s_qty_label = Label(detail_frame, text='Quantity', font=('times new roman', 13), bg='#DFF2EB',height=1)
    s_qty_label.grid(row=3, column=2, sticky='e', padx=15, pady=5)
    s_qty_entry = Entry(detail_frame, font=('times new roman', 12))
    s_qty_entry.grid(row=3, column=3, padx=5, pady=5)

    s_total_label = Label(detail_frame, text='Amount', font=('times new roman', 13), bg='#DFF2EB',height=1)
    s_total_label.grid(row=0, column=4, sticky='e', padx=15, pady=5)
    s_total_entry = Entry(detail_frame, font=('times new roman', 12))
    s_total_entry.grid(row=0, column=5, padx=5, pady=5)
    s_total_entry.bind("<Button-1>", lambda event: on_amount_entry_click(s_price_entry, s_qty_entry, s_total_entry))

    s_gst_label = Label(detail_frame, text='Gst', font=('times new roman', 13), bg='#DFF2EB', height=1)
    s_gst_label.grid(row=1, column=4, sticky='e', padx=15, pady=5)
    s_gst_entry = Entry(detail_frame, font=('times new roman', 12))
    s_gst_entry.grid(row=1, column=5, padx=5, pady=5)
    s_gst_entry.bind("<Button-1>", lambda event: on_gst_entry_click(s_total_entry, s_gst_entry))

    # Label for Discount
    s_dis_label = Label(detail_frame, text='Discount', font=('times new roman', 13), bg='#DFF2EB', height=1)
    s_dis_label.grid(row=2, column=4, sticky='e', padx=15, pady=5)

    # Spinbox for Discount (with range 0-100)
    s_dis_spinbox = Spinbox(detail_frame, from_=0, to=100, font=('times new roman', 12), width=19)
    s_dis_spinbox.grid(row=2, column=5, padx=5, pady=5)

    s_total_amt_label = Label(detail_frame, text='Total Amount', font=('times new roman', 13), bg='#DFF2EB', height=1)
    s_total_amt_label.grid(row=3, column=4, sticky='e', padx=15, pady=5)
    s_total_amt_entry = Entry(detail_frame, font=('times new roman', 12))
    s_total_amt_entry.grid(row=3, column=5, padx=5, pady=5)
    s_total_amt_entry.bind("<Button-1>", lambda event: on_total_amount_entry_click(s_total_entry, s_gst_entry, s_dis_spinbox,
                                                                                  s_total_amt_entry))


    button_frame = Frame(item_frame, bg='#DFF2EB')
    button_frame.place(x=280, y=280)

    add_button = Button(button_frame, text='Add', font=('times new roman', 13), cursor='hand1', width=10,
                        bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                        command=lambda: add_sales_data(s_id_entry, s_date_entry, s_cust_id_combobox, s_cust_name_entry,s_item_id_combobox,s_item_nm_entry,
                                                       s_qty_entry, s_price_entry, s_total_entry, s_gst_entry,
                                                       s_dis_spinbox, s_total_amt_entry))
    add_button.grid(row=0, column=0, padx=10)

    update_button = Button(button_frame, text='Update', font=('times new roman', 13), cursor='hand1', width=10,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                           command=lambda: update_sales_data(s_id_entry, s_date_entry, s_cust_id_combobox,
                                                             s_cust_name_entry,
                                                             s_item_id_combobox, s_item_nm_entry, s_qty_entry,
                                                             s_price_entry,
                                                             s_total_entry, s_gst_entry, s_dis_spinbox, s_total_amt_entry))
    update_button.grid(row=0, column=1, padx=10)

    delete_button = Button(button_frame, text='Delete', font=('times new roman', 13), cursor='hand1', width=10,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,command=lambda :delete_sales(s_id_entry))
    delete_button.grid(row=0, column=2, padx=10)

    clear_button = Button(button_frame, text='Clear', font=('times new roman', 13), cursor='hand1', width=10,
                          bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                          command=lambda: clear_all_fields(s_id_entry, s_date_entry, s_cust_id_combobox,
                                                           s_cust_name_entry,
                                                           s_item_id_combobox, s_item_nm_entry, s_price_entry,
                                                           s_qty_entry,
                                                           s_total_entry, s_gst_entry, s_dis_spinbox, s_total_amt_entry))
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

    # Adjusted Top Frame and Treeview placement
    top_frame = Frame(item_frame, bg='#DFF2EB')
    top_frame.place(x=0, y=350,relwidth=1, height=190)  # Placed at the bottom of item_frame

    # Create horizontal and vertical scrollbars
    horizontal_scrollbar = Scrollbar(top_frame, orient=HORIZONTAL)
    vertical_scrollbar = Scrollbar(top_frame, orient=VERTICAL)

    # Create Treeview
    sales_treeview = ttk.Treeview(
        top_frame,
        columns=(
        'sid', 'sdt', 'scid', 'scnm', 'siid', 'snm', 'sprice', 'sqty', 'samount', 'sgst', 'sdis', 'stamt'),
        show='headings',
        yscrollcommand=vertical_scrollbar.set,
        xscrollcommand=horizontal_scrollbar.set
    )

    # Configure scrollbars
    horizontal_scrollbar.pack(side=BOTTOM, fill=X, pady=(0, 0), padx=(0,0))
    vertical_scrollbar.pack(side=RIGHT, fill=Y, pady=(0, 0), padx=(0, 0))
    horizontal_scrollbar.config(command=sales_treeview.xview)
    vertical_scrollbar.config(command=sales_treeview.yview)

    # Pack the Treeview
    sales_treeview.pack(fill=BOTH, expand=True, pady=(0, 0))

    # Define headings and columns
    sales_treeview.heading('sid', text='Sales Id')
    sales_treeview.heading('sdt', text='Sales Date')
    sales_treeview.heading('scid', text='Customer Id')
    sales_treeview.heading('scnm', text='Customer Name')
    sales_treeview.heading('siid', text='Item Id')
    sales_treeview.heading('snm', text='Item Name')
    sales_treeview.heading('sprice', text='Price')
    sales_treeview.heading('sqty', text='Quantity')
    sales_treeview.heading('samount', text='Amount')
    sales_treeview.heading('sgst', text='Gst')
    sales_treeview.heading('sdis', text='Discount')
    sales_treeview.heading('stamt', text='Total Amount')
    fetch_sales_data()

    sales_treeview.bind("<ButtonRelease-1>", lambda event: on_treeview_select(
        event, s_id_entry, s_date_entry, s_cust_id_combobox, s_cust_name_entry,
        s_item_id_combobox, s_item_nm_entry, s_price_entry, s_qty_entry,
        s_total_entry, s_gst_entry, s_dis_spinbox, s_total_amt_entry))

    sales_treeview.column('sid', width=180)
    sales_treeview.column('sdt', width=180)
    sales_treeview.column('scid', width=180)
    sales_treeview.column('scnm', width=180)
    sales_treeview.column('siid', width=180)
    sales_treeview.column('snm', width=180)
    sales_treeview.column('sprice', width=180)
    sales_treeview.column('sqty', width=180)
    sales_treeview.column('samount', width=170)
    sales_treeview.column('sgst', width=180)
    sales_treeview.column('pdis', width=180)
    sales_treeview.column('stamt', width=180)
