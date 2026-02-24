from tkinter import *
from tkcalendar import DateEntry
from tkinter import messagebox, END
import sqlite3
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
create_sales_return_table_query = """
CREATE TABLE IF NOT EXISTS sales_return (
    salesretid INT PRIMARY KEY,
    salesretdate DATE NOT NULL,
    salesid INT NOT NULL,
    custname VARCHAR(255) NOT NULL,
    itemname VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    saquantity INT NOT NULL,        
    retquantity INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    sadiscount DECIMAL(10, 2) NOT NULL,
    sagst DECIMAL(10, 2) NOT NULL,
    totalamount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (salesid) REFERENCES sales(salesid)
);
"""

cursor.execute(create_sales_return_table_query)
conn.commit()
print("Sales Return table created successfully!")




def populate_salesid_combobox(sl_id_combobox):
    """Populates the sales ID combobox with available sales IDs."""
    cursor.execute("SELECT salesid FROM sales")
    sales_ids = cursor.fetchall()

    # Clear current combobox entries
    sl_id_combobox['values'] = [sales_id[0] for sales_id in sales_ids]

def on_sales_id_select(event, sl_id_combobox, slcnm_entry, slinm_entry, sl_price_entry, sl_qty_entry, sldis_entry):
    """Fills in customer name, item name, price, quantity, and discount when sales ID is selected."""
    salesid = sl_id_combobox.get()

    if salesid:
        # Query the sales table for details based on the selected sales ID
        cursor.execute("SELECT custname, itemname, price, saquantity, sadiscount FROM sales WHERE salesid = %s", (salesid,))
        sale_details = cursor.fetchone()

        if sale_details:
            # Extract details
            custname, itemname, price, saquantity, sadiscount = sale_details

            # Fill in the entry fields with the data
            slcnm_entry.delete(0, END)
            slcnm_entry.insert(0, custname)

            slinm_entry.delete(0, END)
            slinm_entry.insert(0, itemname)

            sl_price_entry.delete(0, END)
            sl_price_entry.insert(0, str(price))

            sl_qty_entry.delete(0, END)
            sl_qty_entry.insert(0, str(saquantity))

            sldis_entry.delete(0, END)
            sldis_entry.insert(0, str(sadiscount))
def update_amount_on_click(sl_price_entry, sl_qty_entry,  sl_ret_qty_entry ,sl_amt_entry, sldis_entry,slgst_entry,sl_total_amt_entry):
    try:
        # Extract values safely
        price = float(sl_price_entry.get() or 0)
        total_qty = int(sl_qty_entry.get() or 0)
        return_qty = int(sl_ret_qty_entry.get() or 0)
        discount_rate = float(sldis_entry.get() or 0)

        # Default GST to 15% if it's empty
        gst_rate = 15  # We set it to 15% directly (default value)

        # Calculate remaining quantity and total amount
        remaining_qty = max(total_qty - return_qty, 0)
        amount = price * remaining_qty  # Amount after return

        # Calculate discount amount based on the remaining amount
        discount_amount = (discount_rate * amount) / 100

        # Calculate GST amount as 15% of the amount
        gst_amount = (gst_rate * amount) / 100

        # Calculate the base total amount (Amount - Discount - GST)
        base_total_amount = amount - discount_amount + gst_amount

        # Update the Amount entry field with the calculated amount
        sl_amt_entry.delete(0, END)
        sl_amt_entry.insert(0, f"{amount:.2f}")

        # Update the Total Amount entry field with the base total amount (Amount - Discount - GST)
        sl_total_amt_entry.delete(0, END)
        sl_total_amt_entry.insert(0, f"{base_total_amount:.2f}")

        # Optionally, you can display the GST amount separately if needed:
        slgst_entry.delete(0, END)
        slgst_entry.insert(0, f"{gst_amount:.2f}")

    except ValueError:
        sl_amt_entry.delete(0, END)
        sl_amt_entry.insert(0, "Invalid Input")
        sl_total_amt_entry.delete(0, END)
        sl_total_amt_entry.insert(0, "Invalid Input")


def validate_form(s_ret_id_entry, s_ret_dt_entry, sl_id_combobox, slcnm_entry, slinm_entry, sl_price_entry,
                  sl_qty_entry, sl_ret_qty_entry, sl_amt_entry, sldis_entry, slgst_entry, sl_total_amt_entry):
    # Check if purchase return ID is entered
    if not s_ret_id_entry.get():
        messagebox.showerror("Validation Error", "Sales Return ID is required!")
        return False

    # Check if return date is selected
    if not s_ret_dt_entry.get_date():
        messagebox.showerror("Validation Error", "Sales Return date is required!")
        return False

    # Check if product ID is selected from the combo box
    if sl_id_combobox.get() == "Select Id":
        messagebox.showerror("Validation Error", "Please select a valid Sales ID!")
        return False

    # Check if company name is entered
    if not slcnm_entry.get():
        messagebox.showerror("Validation Error", "Customer name is required!")
        return False

    # Check if item name is entered
    if not slinm_entry.get():
        messagebox.showerror("Validation Error", "Item name is required!")
        return False

    # Check if price is a valid number
    try:
        price = float(sl_price_entry.get())
        if price <= 0:
            raise ValueError("Price must be greater than zero.")
    except ValueError:
        messagebox.showerror("Validation Error", "Price must be a valid number!")
        return False

    # Check if total quantity is a valid integer
    try:
        total_qty = int(sl_qty_entry.get())
        if total_qty <= 0:
            raise ValueError("Total quantity must be greater than zero.")
    except ValueError:
        messagebox.showerror("Validation Error", "Total quantity must be a valid number!")
        return False

    # Check if return quantity is a valid integer
    try:
        return_qty = int(sl_ret_qty_entry.get())
        if return_qty < 0 or return_qty > total_qty:
            raise ValueError("Return quantity must be a valid number and cannot exceed total quantity.")
    except ValueError:
        messagebox.showerror("Validation Error", "Return quantity must be a valid number!")
        return False

    # Check if discount is a valid number
    try:
        discount_rate = float(sldis_entry.get())
        if discount_rate < 0:
            raise ValueError("Discount cannot be negative.")
    except ValueError:
        messagebox.showerror("Validation Error", "Discount must be a valid number!")
        return False

    # If all checks pass, return True
    return True

import pymysql
from tkinter import messagebox

def add_sales_return_record(s_ret_id_entry, s_ret_dt_entry, sl_id_combobox, slcnm_entry, slinm_entry,
                             sl_price_entry, sl_qty_entry, sl_ret_qty_entry, sl_amt_entry, sldis_entry,
                             slgst_entry, sl_total_amt_entry):
    """Adds a new Sales Return record to the database."""
    if not validate_form(s_ret_id_entry, s_ret_dt_entry, sl_id_combobox, slcnm_entry, slinm_entry, sl_price_entry,
                         sl_qty_entry, sl_ret_qty_entry, sl_amt_entry, sldis_entry, slgst_entry, sl_total_amt_entry):
        return  # If validation fails, stop the function

    try:
        # Collecting values from the form
        sales_ret_id = int(s_ret_id_entry.get())
        sales_ret_date = s_ret_dt_entry.get_date()  # Assuming this is a date object
        sales_id = sl_id_combobox.get()
        customer_name = slcnm_entry.get()
        item_name = slinm_entry.get()
        price = float(sl_price_entry.get())
        total_qty = int(sl_qty_entry.get())
        return_qty = int(sl_ret_qty_entry.get())
        amount = float(sl_amt_entry.get())
        discount = float(sldis_entry.get())
        gst = float(slgst_entry.get())
        total_amount = float(sl_total_amt_entry.get())

        # Connect to the MySQL database
        conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
        cursor = conn.cursor()

        # Insert the sales return record into the sales_return table
        insert_query = """
        INSERT INTO sales_return (salesretid, salesretdate, salesid, custname, itemname, price, saquantity,
                                  retquantity, amount, sadiscount, sagst, totalamount)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(insert_query, (sales_ret_id, sales_ret_date, sales_id, customer_name, item_name, price,
                                      total_qty, return_qty, amount, discount, gst, total_amount))
        conn.commit()  # Commit the transaction
        populate_sales_return_treeview()
        # Show success message
        messagebox.showinfo("Success", "Sales return record added successfully!")
        clear_fields(s_ret_id_entry, s_ret_dt_entry, sl_id_combobox, slcnm_entry, slinm_entry, sl_price_entry,
                     sl_qty_entry, sl_ret_qty_entry, sl_amt_entry, sldis_entry, slgst_entry, sl_total_amt_entry)

    except Exception as e:
        # In case of an error, rollback the transaction
        conn.rollback()
        messagebox.showerror("Error", f"Error adding sales return record: {str(e)}")

    finally:
        # Close the database connection
        cursor.close()
        conn.close()


def clear_fields(s_ret_id_entry, s_ret_dt_entry, sl_id_combobox, slcnm_entry, slinm_entry, sl_price_entry,
                        sl_qty_entry, sl_ret_qty_entry, sl_amt_entry, sldis_entry, slgst_entry, sl_total_amt_entry):
    try:
        # Clear Purchase Return ID entry
        s_ret_id_entry.delete(0, END)

        # Clear Return Date (assuming it's a custom date widget)
        if hasattr(s_ret_dt_entry, 'set_date'):
            # Clear the date field properly, use None or a valid default value
            s_ret_dt_entry.set_date(None)  # Use None to clear the date
        else:
            print("Error: 'p_ret_dt_entry' does not have 'set_date' method.")

        # Clear Purchase ID (combobox)
        if hasattr(sl_id_combobox, 'set'):
            sl_id_combobox.set('')  # Reset the combobox selection
        else:
            print("Error: 'pr_id_combobox' does not have 'set' method.")
        slcnm_entry.delete(0, END)
        slinm_entry.delete(0, END)
        sl_price_entry.delete(0, END)
        sl_qty_entry.delete(0, END)
        sl_ret_qty_entry.delete(0, END)
        sl_amt_entry.delete(0, END)
        sldis_entry.delete(0, END)
        slgst_entry.delete(0, END)
        # Clear Total Amount entry
        sl_total_amt_entry.delete(0, END)

    except Exception as e:
        print(f"Error: {e}")



def update_sales_return_record(s_ret_id_entry, s_ret_dt_entry, sl_id_combobox, slcnm_entry, slinm_entry,
                                sl_price_entry, sl_qty_entry, sl_ret_qty_entry, sl_amt_entry, sldis_entry,
                                slgst_entry, sl_total_amt_entry):
    """Updates an existing Sales Return record in the database."""
    if not validate_form(s_ret_id_entry, s_ret_dt_entry, sl_id_combobox, slcnm_entry, slinm_entry, sl_price_entry,
                         sl_qty_entry, sl_ret_qty_entry, sl_amt_entry, sldis_entry, slgst_entry, sl_total_amt_entry):
        return  # If validation fails, stop the function

    try:
        # Collecting values from the form
        sales_ret_id = int(s_ret_id_entry.get())
        sales_ret_date = s_ret_dt_entry.get_date()  # Assuming this is a date object
        sales_id = sl_id_combobox.get()
        customer_name = slcnm_entry.get()
        item_name = slinm_entry.get()
        price = float(sl_price_entry.get())
        total_qty = int(sl_qty_entry.get())
        return_qty = int(sl_ret_qty_entry.get())
        amount = float(sl_amt_entry.get())
        discount = float(sldis_entry.get())
        gst = float(slgst_entry.get())
        total_amount = float(sl_total_amt_entry.get())

        # Connect to the MySQL database
        conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
        cursor = conn.cursor()

        # Check if the sales return record exists
        cursor.execute("SELECT * FROM sales_return WHERE salesretid = %s", (sales_ret_id,))
        existing_record = cursor.fetchone()

        if not existing_record:
            messagebox.showerror("Error", "Sales Return ID not found!")
            return

        # SQL query to update the sales return record
        update_query = """
        UPDATE sales_return
        SET salesretdate = %s, salesid = %s, custname = %s, itemname = %s, price = %s, saquantity = %s,
            retquantity = %s, amount = %s, sadiscount = %s, sagst = %s, totalamount = %s
        WHERE salesretid = %s
        """

        cursor.execute(update_query, (sales_ret_date, sales_id, customer_name, item_name, price, total_qty,
                                      return_qty, amount, discount, gst, total_amount, sales_ret_id))
        conn.commit()  # Commit the transaction
        populate_sales_return_treeview()
        # Show success message
        messagebox.showinfo("Success", "Sales return record updated successfully!")
        clear_fields(s_ret_id_entry, s_ret_dt_entry, sl_id_combobox, slcnm_entry, slinm_entry, sl_price_entry,
                     sl_qty_entry, sl_ret_qty_entry, sl_amt_entry, sldis_entry, slgst_entry, sl_total_amt_entry)

    except Exception as e:
        # In case of an error, rollback the transaction
        conn.rollback()
        messagebox.showerror("Error", f"Error updating sales return record: {str(e)}")

    finally:
        # Close the database connection
        cursor.close()
        conn.close()



def delete_sales_return(s_ret_id_entry, s_ret_dt_entry, sl_id_combobox, slcnm_entry, slinm_entry, sl_price_entry,
                     sl_qty_entry, sl_ret_qty_entry, sl_amt_entry, sldis_entry, slgst_entry, sl_total_amt_entry):
    try:
        # Get the Purchase Return ID from the entry field
        sales_return_id = int(s_ret_id_entry.get())

        # Confirm the deletion with the user
        confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete this record?")
        if not confirmation:
            return  # If user cancels, exit the function

        # Connect to the database
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="1234",
            database="handloom"
        )
        cursor = conn.cursor()

        # SQL query to delete the record from purchase_return table
        delete_query = "DELETE FROM sales_return WHERE salesretid = %s"

        cursor.execute(delete_query, (sales_return_id,))

        # Commit the transaction
        conn.commit()

        # Refresh the Treeview to reflect the changes
        populate_sales_return_treeview()

        # Success message
        messagebox.showinfo("Success", "Record deleted successfully!")
        clear_fields(s_ret_id_entry, s_ret_dt_entry, sl_id_combobox, slcnm_entry, slinm_entry, sl_price_entry,
                     sl_qty_entry, sl_ret_qty_entry, sl_amt_entry, sldis_entry, slgst_entry, sl_total_amt_entry)


    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", "Failed to delete Sales return record.")

    finally:
        # Close the connection
        cursor.close()
        conn.close()

def populate_sales_return_treeview():
    try:
        # Connect to MySQL
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="1234",
            database="handloom"
        )
        cursor = conn.cursor()

        # Query to fetch all records from purchase_return table
        cursor.execute("SELECT * FROM sales_return ORDER BY salesretid ASC")
        records = cursor.fetchall()

        # Clear existing data in Treeview
        for row in sales_return_treeview.get_children():
            sales_return_treeview.delete(row)

        # Insert each record into the Treeview
        for record in records:
            sales_return_treeview.insert('', 'end', values=record)

    except pymysql.Error as db_err:
        print(f"Database error: {db_err}")
        messagebox.showerror("Error", "Failed to load sales return data.")
    finally:
        cursor.close()
        conn.close()

from datetime import datetime  # Correct import

def on_treeview_select(event,s_ret_id_entry, s_ret_dt_entry, sl_id_combobox, slcnm_entry, slinm_entry, sl_price_entry,
                        sl_qty_entry, sl_ret_qty_entry, sl_amt_entry, sldis_entry, slgst_entry, sl_total_amt_entry):
    try:
        # Get the selected row item
        selected_item = sales_return_treeview.selection()

        if selected_item:
            # Get values of the selected row
            selected_values = sales_return_treeview.item(selected_item, 'values')
            print(f"Selected row values: {selected_values}")

            # Populate the form fields with values from the selected row
            # Purchase Return ID
            s_ret_id_entry.delete(0, END)
            s_ret_id_entry.insert(0, selected_values[0])

            # Return Date (assuming it's in the second column)
            return_date_str = selected_values[1]  # '2025-02-05'
            # Convert the string to a datetime object using strptime
            return_date = datetime.strptime(return_date_str, "%Y-%m-%d").date()  # Convert to datetime.date object
            s_ret_dt_entry.set_date(return_date)  # Pass the datetime object to the entry field

            # Purchase ID (third column)
            sl_id_combobox.set(selected_values[2])

            # Company Name (fourth column)
            slcnm_entry.delete(0, END)
            slcnm_entry.insert(0, selected_values[3])

            # Item Name (fifth column)
            slinm_entry.delete(0, END)
            slinm_entry.insert(0, selected_values[4])

            # Price (sixth column)
            sl_price_entry.delete(0, END)
            sl_price_entry.insert(0, str(selected_values[5]))

            # Quantity (seventh column)
            sl_qty_entry.delete(0, END)
            sl_qty_entry.insert(0, str(selected_values[6]))

            # Return Quantity (eighth column)
            sl_ret_qty_entry.delete(0, END)
            sl_ret_qty_entry.insert(0, str(selected_values[7]))

            # Amount (ninth column)
            sl_amt_entry.delete(0, END)
            sl_amt_entry.insert(0, str(selected_values[8]))

            # Discount (tenth column)
            sldis_entry.delete(0, END)
            sldis_entry.insert(0, str(selected_values[9]))

            # GST (eleventh column)
            slgst_entry.delete(0, END)
            slgst_entry.insert(0, str(selected_values[10]))

            # Total Amount (twelfth column)
            sl_total_amt_entry.delete(0, END)
            sl_total_amt_entry.insert(0, str(selected_values[11]))

    except Exception as e:
        print(f"Error: {e}")


def search_sales_return_data(search_combobox, search_entry):
    search_criteria = search_combobox.get().strip()
    search_value = search_entry.get().strip()

    if not search_value:
        messagebox.showerror("Error", "Please enter a value to search.")
        return

    conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
    cursor = conn.cursor()

    try:
        if search_criteria == "Id":
            query = "SELECT * FROM sales_return WHERE salesretid = %s"
            cursor.execute(query, (search_value,))
        elif search_criteria == "Name":
            query = "SELECT * FROM sales_return WHERE itemname LIKE %s"
            cursor.execute(query, ('%' + search_value + '%',))
        elif search_criteria == "All":
            query = "SELECT * FROM sales_return"
            cursor.execute(query)

        records = cursor.fetchall()

        # Clear existing data in Treeview
        sales_return_treeview.delete(*sales_return_treeview.get_children())

        for row in records:
            sales_return_treeview.insert("", "end", values=row)

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
        pdf.drawString(520, 1050, "Sales Return Report")

        # Set font for table headers and data
        pdf.setFont("Helvetica", 10)

        # Adjusted column widths with increased width for Address and City
        col_widths = [100, 100, 100, 100, 100, 100,100,100, 100, 100, 100, 100]  # Address and City columns increased

        # Draw table headers
        header = ["Sales Return Id", "Sales Return Date","Sales Id", "Customer Name","Item Name", "Price","Quantity", "Return Quantity","Amount","Discount","Gst","Total Amount"]
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
            query = "SELECT * FROM sales_return WHERE salesretid = %s"
            cursor.execute(query, (search_value,))
            report_name = f"Sales_Return_Report_{search_value}"  # Dynamic name for the report
        elif search_criteria == "Name":
            query = "SELECT * FROM sales_return WHERE itemname LIKE %s"
            cursor.execute(query, ('%' + search_value + '%',))
            report_name = f"Sales_Return_Report_{search_value}"  # Dynamic name for the report
        elif search_criteria == "All":
            query = "SELECT * FROM sales_return"
            cursor.execute(query)
            report_name = "Sales_Return_Report_All"  # Generic name for all companies

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



def sales_return_form(window):
    global back_image,sales_return_treeview
    item_frame = Frame(window, width=1270, height=542,bg='#DFF2EB')
    item_frame.place(x=0, y=99)
    heading_label = Label(item_frame, text='Manage Sales Return Detail', font=('times new roman', 18, 'bold'),fg='white',
                          bg='#7AB2D3')
    heading_label.place(x=0, y=0, relwidth='1')

    #---top frame
    top_frame = Frame(item_frame, bg='#DFF2EB')
    top_frame.place(x=0, y=40, relwidth=1, height=200)
    search_frame = Frame(top_frame, bg='#DFF2EB')
    search_frame.pack()

    search_combobox = ttk.Combobox(search_frame, values=('Id','Name', 'All'), font=('times new roman', 13),
                                   state='readonly')
    search_combobox.set('Search By')
    search_combobox.grid(row=0, column=0, padx=20)

    search_entry = Entry(search_frame, font=('times new roman', 13))
    search_entry.grid(row=0, column=1)

    search_button = Button(search_frame, text='Search', font=('times new roman', 13), cursor='hand1', width=10,
                           height=0,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,command=lambda: search_sales_return_data(search_combobox, search_entry))
    search_button.grid(row=0, column=2, padx=20)

    show_button = Button(search_frame, text='Show All', font=('times new roman', 13), cursor='hand1', width=10,
                         bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,command=populate_sales_return_treeview)
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
    s_ret_id_label = Label(detail_frame, text='Sales Return Id', font=('times new roman', 13), bg='#DFF2EB',
                           height=1)
    s_ret_id_label.grid(row=0, column=0, sticky='e', padx=15, pady=5)
    s_ret_id_entry = Entry(detail_frame, font=('times new roman', 12))
    s_ret_id_entry.grid(row=0, column=1, padx=5, pady=5)

    s_ret_dt_label = Label(detail_frame, text='Sales Return Date', font=('times new roman', 13), bg='#DFF2EB',
                           height=1)
    s_ret_dt_label.grid(row=1, column=0, sticky='e', padx=15, pady=5)
    s_ret_dt_entry = DateEntry(detail_frame, width=18, font=('times new roman', 12), state='readonly',
                               date_pattern='dd/mm/yy')
    s_ret_dt_entry.grid(row=1, column=1, padx=5, pady=5)

    sl_id_label = Label(detail_frame, text='Sales Id', font=('times new roman', 13), bg='#DFF2EB', height=1)
    sl_id_label.grid(row=2, column=0, sticky='e', padx=15, pady=5)
    sl_id_combobox = ttk.Combobox(detail_frame, width=18, font=('times new roman', 12), state='readonly')
    sl_id_combobox.set('Select Id')
    sl_id_combobox.grid(row=2, column=1, padx=5, pady=5)
    sl_id_combobox.bind("<<ComboboxSelected>>", lambda event:on_sales_id_select(event,sl_id_combobox,slcnm_entry,slinm_entry,sl_price_entry,sl_qty_entry,sldis_entry))



    # Similar adjustments for other labels and entries
    slcnm_label = Label(detail_frame, text='Customer Name', font=('times new roman', 13), bg='#DFF2EB', height=1)
    slcnm_label.grid(row=3, column=0, sticky='e', padx=15, pady=5)
    slcnm_entry = Entry(detail_frame, font=('times new roman', 12))
    slcnm_entry.grid(row=3, column=1, padx=5, pady=5)
    populate_salesid_combobox(sl_id_combobox)

    slinm_label = Label(detail_frame, text='Item Name', font=('times new roman', 13), bg='#DFF2EB', height=1)
    slinm_label.grid(row=0, column=2, sticky='e', padx=15, pady=5)
    slinm_entry = Entry(detail_frame, font=('times new roman', 12))
    slinm_entry.grid(row=0, column=3, padx=5, pady=5)

    sl_price_label = Label(detail_frame, text='Price', font=('times new roman', 13), bg='#DFF2EB', height=1)
    sl_price_label.grid(row=1, column=2, sticky='e', padx=15, pady=5)
    sl_price_entry = Entry(detail_frame, font=('times new roman', 12))
    sl_price_entry.grid(row=1, column=3, padx=5, pady=5)

    sl_qty_label = Label(detail_frame, text='Quantity', font=('times new roman', 13), bg='#DFF2EB', height=1)
    sl_qty_label.grid(row=2, column=2, sticky='e', padx=15, pady=5)
    sl_qty_entry = Entry(detail_frame, font=('times new roman', 12))
    sl_qty_entry.grid(row=2, column=3, padx=5, pady=5)

    sl_ret_qty_label = Label(detail_frame, text='Return Quantity', font=('times new roman', 13), bg='#DFF2EB',
                              height=1)
    sl_ret_qty_label.grid(row=3, column=2, sticky='e', padx=15, pady=5)
    sl_ret_qty_entry = Entry(detail_frame, font=('times new roman', 12))
    sl_ret_qty_entry.grid(row=3, column=3, padx=5, pady=5)

    sl_amt_label = Label(detail_frame, text='Amount', font=('times new roman', 13), bg='#DFF2EB', height=1)
    sl_amt_label.grid(row=0, column=4, sticky='e', padx=15, pady=5)
    sl_amt_entry = Entry(detail_frame, font=('times new roman', 12))
    sl_amt_entry.grid(row=0, column=5, padx=5, pady=5)

    # Bind the Amount entry field to update when clicked
    sl_amt_entry.bind("<Button-1>", lambda event: update_amount_on_click(
        sl_price_entry, sl_qty_entry,  sl_ret_qty_entry ,sl_amt_entry, sldis_entry,slgst_entry,sl_total_amt_entry
    ))

    sldis_label = Label(detail_frame, text='Discount', font=('times new roman', 13), bg='#DFF2EB', height=1)
    sldis_label.grid(row=1, column=4, sticky='e', padx=15, pady=5)
    sldis_entry = Entry(detail_frame, font=('times new roman', 12))
    sldis_entry.grid(row=1, column=5, padx=5, pady=5)

    slgst_label = Label(detail_frame, text='Gst', font=('times new roman', 13), bg='#DFF2EB', height=1)
    slgst_label.grid(row=2, column=4, sticky='e', padx=15, pady=5)
    slgst_entry = Entry(detail_frame, font=('times new roman', 12))
    slgst_entry.grid(row=2, column=5, padx=5, pady=5)

    sl_total_amt_label = Label(detail_frame, text='Total Amount', font=('times new roman', 13), bg='#DFF2EB', height=1)
    sl_total_amt_label.grid(row=3, column=4, sticky='e', padx=15, pady=5)
    sl_total_amt_entry = Entry(detail_frame, font=('times new roman', 12))
    sl_total_amt_entry.grid(row=3, column=5, padx=5, pady=5)

    button_frame = Frame(item_frame, bg='#DFF2EB')
    button_frame.place(x=280, y=280)

    add_button = Button(button_frame, text='Add', font=('times new roman', 13), cursor='hand1', width=10,
                        bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                        command=lambda: add_sales_return_record(
                            s_ret_id_entry, s_ret_dt_entry, sl_id_combobox, slcnm_entry, slinm_entry, sl_price_entry,
                            sl_qty_entry, sl_ret_qty_entry, sl_amt_entry, sldis_entry, slgst_entry, sl_total_amt_entry
                        ))
    add_button.grid(row=0, column=0, padx=10)

    update_button = Button(button_frame, text='Update', font=('times new roman', 13), cursor='hand1', width=10,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                           command=lambda: update_sales_return_record(
                               s_ret_id_entry, s_ret_dt_entry, sl_id_combobox, slcnm_entry, slinm_entry, sl_price_entry,
                               sl_qty_entry, sl_ret_qty_entry, sl_amt_entry, sldis_entry, slgst_entry,
                               sl_total_amt_entry))
    update_button.grid(row=0, column=1, padx=10)

    delete_button = Button(button_frame, text='Delete', font=('times new roman', 13), cursor='hand1', width=10,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                           command=lambda: delete_sales_return(s_ret_id_entry, s_ret_dt_entry, sl_id_combobox, slcnm_entry, slinm_entry, sl_price_entry,
                     sl_qty_entry, sl_ret_qty_entry, sl_amt_entry, sldis_entry, slgst_entry, sl_total_amt_entry))
    delete_button.grid(row=0, column=2, padx=10)

    clear_button = Button(button_frame, text='Clear', font=('times new roman', 13), cursor='hand1', width=10,
                          bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2 ,
                          command=lambda: clear_fields(s_ret_id_entry, s_ret_dt_entry, sl_id_combobox, slcnm_entry, slinm_entry, sl_price_entry,
                        sl_qty_entry, sl_ret_qty_entry, sl_amt_entry, sldis_entry, slgst_entry, sl_total_amt_entry))
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
    sales_return_treeview = ttk.Treeview(
        top_frame,
        columns=(
        'salrid','salrdt','salid', 'salcnm', 'salinm',  'salprice', 'salqty','salrqty', 'salamount','saldis','salgst', 'saltamt'),
        show='headings',
        yscrollcommand=vertical_scrollbar.set,
        xscrollcommand=horizontal_scrollbar.set
    )

    # Configure scrollbars
    horizontal_scrollbar.pack(side=BOTTOM, fill=X, pady=(0, 0), padx=(0,0))
    vertical_scrollbar.pack(side=RIGHT, fill=Y, pady=(0, 0), padx=(0, 0))
    horizontal_scrollbar.config(command=sales_return_treeview.xview)
    vertical_scrollbar.config(command=sales_return_treeview.yview)

    # Pack the Treeview
    sales_return_treeview.pack(fill=BOTH, expand=True, pady=(0, 0))

    # Define headings and columns
    sales_return_treeview.heading('salrid', text='Sales Return Id')
    sales_return_treeview.heading('salrdt', text='Sales Return Date')
    sales_return_treeview.heading('salid', text='Sales Id')
    sales_return_treeview.heading('salcnm', text='Customer Name')
    sales_return_treeview.heading('salinm', text='Item Name')
    sales_return_treeview.heading('salprice', text='Price')
    sales_return_treeview.heading('salqty', text='Quantity')
    sales_return_treeview.heading('salrqty', text='Return Quantity')
    sales_return_treeview.heading('salamount', text='Amount')
    sales_return_treeview.heading('saldis', text='Discount')
    sales_return_treeview.heading('salgst', text='Gst')
    sales_return_treeview.heading('saltamt', text='Total Amount')

    sales_return_treeview.column('salrid', width=180)
    sales_return_treeview.column('salrdt', width=180)
    sales_return_treeview.column('salid', width=180)
    sales_return_treeview.column('salcnm', width=180)
    sales_return_treeview.column('salinm', width=180)
    sales_return_treeview.column('salprice', width=180)
    sales_return_treeview.column('salqty', width=180)
    sales_return_treeview.column('salrqty', width=180)
    sales_return_treeview.column('salamount', width=170)
    sales_return_treeview.column('saldis', width=180)
    sales_return_treeview.column('salgst', width=180)
    sales_return_treeview.column('saltamt', width=180)
    populate_sales_return_treeview()
    sales_return_treeview.bind("<ButtonRelease-1>",
                                  lambda event: on_treeview_select(event,s_ret_id_entry, s_ret_dt_entry, sl_id_combobox, slcnm_entry, slinm_entry, sl_price_entry,
                        sl_qty_entry, sl_ret_qty_entry, sl_amt_entry, sldis_entry, slgst_entry, sl_total_amt_entry ))
