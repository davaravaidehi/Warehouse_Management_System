from tkinter import *
from tkcalendar import DateEntry
from datetime import datetime
from tkinter import Spinbox
import pymysql
from tkinter import filedialog
import os
import tkinter.messagebox as messagebox
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

create_table_query = """
CREATE TABLE IF NOT EXISTS purchase (
    purchaseid INT PRIMARY KEY,  -- Removed AUTO_INCREMENT
    purchasedate DATE NOT NULL,  
    comid INT NOT NULL,  -- References company table
    comname VARCHAR(255) NOT NULL,  
    itemid INT NOT NULL,  -- References item table
    itemname VARCHAR(255) NOT NULL,  
    price DECIMAL(10, 2) NOT NULL,  
    puqty INT NOT NULL,  
    puamount DECIMAL(10, 2) NOT NULL,  
    pugst DECIMAL(5, 2) NOT NULL,  
    pudiscount DECIMAL(5, 2) NOT NULL,  
    putotal_amount DECIMAL(10, 2) NOT NULL,    
    FOREIGN KEY (comid) REFERENCES company(comid) ON DELETE CASCADE,  
    FOREIGN KEY (itemid) REFERENCES item(itemid) ON DELETE CASCADE  
);

"""

cursor.execute(create_table_query)
conn.commit()
print("Purchase table created successfully!")

# Close connection
cursor.close()
conn.close()
def populate_company_ids():
    # Open a new connection and cursor for the query
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="1234",
        database="handloom"
    )
    cursor = conn.cursor()

    # Query to fetch company ids in ascending order
    cursor.execute("SELECT comid FROM company ORDER BY comid ASC")  # Add ORDER BY for ascending order

    # Fetching all company ids
    company_ids = cursor.fetchall()

    # Close the cursor and connection after use
    cursor.close()
    conn.close()

    # Return a list of company ids
    return [str(row[0]) for row in company_ids]  # return as a list of strings

def populate_company_name(event, pcom_id_combobox, pcom_nm_entry):
    company_id = pcom_id_combobox.get()  # Get selected company ID

    if company_id:
        # Open a new connection to the database
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="1234",
            database="handloom"
        )
        cursor = conn.cursor()

        # Query to fetch the company name based on the selected company ID
        cursor.execute("SELECT comname FROM company WHERE comid = %s", (company_id,))
        company_name = cursor.fetchone()

        if company_name:
            # Fill the company name in the entry field
            pcom_nm_entry.delete(0, END)
            pcom_nm_entry.insert(0, company_name[0])  # Company name is the first element in the tuple

        # Close the cursor and connection after use
        cursor.close()
        conn.close()
def populate_item_ids():
    # Open a new connection and cursor for the query
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="1234",
        database="handloom"
    )
    cursor = conn.cursor()

    # Query to fetch item ids in ascending order
    cursor.execute("SELECT itemid FROM item ORDER BY itemid ASC")  # Add ORDER BY for ascending order

    # Fetching all item ids
    item_ids = cursor.fetchall()

    # Close the cursor and connection after use
    cursor.close()
    conn.close()

    # Return a list of item ids
    return [str(row[0]) for row in item_ids]  # return as a list of strings

def populate_item_name(event, pitem_id_combobox, pitem_nm_entry, pitem_price_entry):
    item_id = pitem_id_combobox.get()  # Get selected item ID

    if item_id:
        # Open a new connection to the database
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
            item_name, item_price = item_data  # Unpack the tuple into item name and price
            # Fill the item name in the entry field
            pitem_nm_entry.delete(0, END)
            pitem_nm_entry.insert(0, item_name)  # Item name is the first element in the tuple

            # Fill the item price in the entry field
            pitem_price_entry.delete(0, END)
            pitem_price_entry.insert(0, str(item_price))  # Item price is the second element in the tuple

        # Close the cursor and connection after use
        cursor.close()
        conn.close()


def on_amount_entry_click(pprice_entry, pqty_entry, pamt_entry):
    try:
        # Get values from price and quantity fields
        price = float(pprice_entry.get())
        qty = int(pqty_entry.get())

        # Calculate amount
        amount = price * qty

        # Update the amount entry field
        pamt_entry.delete(0, 'end')  # Clear existing value
        pamt_entry.insert(0, str(amount))  # Insert calculated amount

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numerical values for price and quantity.")


def on_gst_entry_click(pamt_entry, pgst_entry):
    try:
        # Get the calculated amount
        amount = float(pamt_entry.get())

        # Calculate GST (15%)
        gst = amount * 0.15

        # Update the GST entry field
        pgst_entry.delete(0, 'end')  # Clear existing value
        pgst_entry.insert(0, str(gst))  # Insert calculated GST

    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid amount before calculating GST.")

def on_total_amount_entry_click(pamt_entry, pgst_entry, pdis_entry, ptotal_amt_entry):
    try:
        # Get values from Amount, GST, and Discount fields
        amount = float(pamt_entry.get())
        gst = float(pgst_entry.get())
        discount = float(pdis_entry.get())

        # Convert discount percentage to a decimal
        discount_amount = (amount + gst) * (discount / 100)

        # Calculate total amount
        total_amount = (amount + gst) - discount_amount

        # Update the Total Amount entry field
        ptotal_amt_entry.delete(0, 'end')  # Clear existing value
        ptotal_amt_entry.insert(0, str(total_amount))  # Insert the calculated total amount

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numerical values for amount, GST, and discount.")



def add_purchase(p_id_entry, pdt_entry, pcom_id_combobox, pcom_nm_entry, pitem_id_combobox, pitem_nm_entry,
                 pprice_entry, pqty_entry, pamt_entry, pgst_entry, pdis_entry, ptotal_amt_entry):
    try:
        # Retrieve values from the entry widgets
        purchase_id = p_id_entry.get().strip()
        purchase_date = pdt_entry.get_date() if pdt_entry.get_date() else None  # Ensure a valid date
        company_id = pcom_id_combobox.get().strip()
        company_name = pcom_nm_entry.get().strip()
        item_id = pitem_id_combobox.get().strip()
        item_name = pitem_nm_entry.get().strip()

        # Validate numerical fields
        price = pprice_entry.get().strip()
        quantity = pqty_entry.get().strip()
        amount = pamt_entry.get().strip()
        gst = pgst_entry.get().strip()
        discount = pdis_entry.get().strip()
        total_amount = ptotal_amt_entry.get().strip()

        if not purchase_id or not purchase_date:
            raise ValueError("Purchase ID and Date are required.")
        if not company_id or not company_name:
            raise ValueError("Company ID and Name are required.")
        if not item_id or not item_name:
            raise ValueError("Item ID and Name are required.")

        if not price or not quantity or not amount or not gst or not discount or not total_amount:
            raise ValueError("Price, Quantity, Amount, GST, Discount, and Total Amount are required.")

        try:
            price = float(price)
        except ValueError:
            raise ValueError("Price must be a valid number.")

        try:
            quantity = int(quantity)
        except ValueError:
            raise ValueError("Quantity must be a valid integer.")

        # Validate Quantity (ensure it's less than or equal to 100)
        if quantity > 100:
            raise ValueError("Quantity should not be more than 100.")

        try:
            amount = float(amount)
        except ValueError:
            raise ValueError("Amount must be a valid number.")

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

        # Prepare the insert query
        insert_query = """
        INSERT INTO purchase (purchaseid, purchasedate, comid, comname, itemid, itemname, price, puqty, puamount, 
                              pugst, pudiscount, putotal_amount)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """  # Fixed: 14 placeholders for 14 values

        # Execute the insert query
        cursor.execute(insert_query,
                       (purchase_id, purchase_date, company_id, company_name, item_id, item_name, price, quantity,
                        amount, gst, discount, total_amount))

        # Commit the transaction
        conn.commit()
        fetch_data()
        messagebox.showinfo("Success", "Purchase added successfully!")

    except pymysql.MySQLError as e:
        messagebox.showerror("Database Error", f"Error: {e}")
    except ValueError as e:
        messagebox.showerror("Validation Error", f"Error: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

def update_purchase(p_id_entry, pdt_entry, pcom_id_combobox, pcom_nm_entry, pitem_id_combobox, pitem_nm_entry,
                    pprice_entry, pqty_entry, pamt_entry, pgst_entry, pdis_entry, ptotal_amt_entry):
    try:
        # Retrieve values from the entry widgets
        purchase_id = p_id_entry.get().strip()
        purchase_date = pdt_entry.get_date() if pdt_entry.get_date() else None
        company_id = pcom_id_combobox.get().strip()
        company_name = pcom_nm_entry.get().strip()
        item_id = pitem_id_combobox.get().strip()
        item_name = pitem_nm_entry.get().strip()

        # Validate numerical fields
        price = pprice_entry.get().strip()
        quantity = pqty_entry.get().strip()
        amount = pamt_entry.get().strip()
        gst = pgst_entry.get().strip()
        discount = pdis_entry.get().strip()
        total_amount = ptotal_amt_entry.get().strip()

        if not purchase_id or not purchase_date:
            raise ValueError("Purchase ID and Date are required.")
        if not company_id or not company_name:
            raise ValueError("Company ID and Name are required.")
        if not item_id or not item_name:
            raise ValueError("Item ID and Name are required.")

        if not price or not quantity or not amount or not gst or not discount or not total_amount:
            raise ValueError("Price, Quantity, Amount, GST, Discount, and Total Amount are required.")

        try:
            price = float(price)
        except ValueError:
            raise ValueError("Price must be a valid number.")

        try:
            quantity = int(quantity)
        except ValueError:
            raise ValueError("Quantity must be a valid integer.")

        # Validate Quantity (ensure it's less than or equal to 100)
        if quantity > 100:
            raise ValueError("Quantity should not be more than 100.")

        try:
            amount = float(amount)
        except ValueError:
            raise ValueError("Amount must be a valid number.")

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

        # Prepare the update query
        update_query = """
        UPDATE purchase
        SET purchasedate = %s, comid = %s, comname = %s, itemid = %s, itemname = %s, price = %s, puqty = %s,
            puamount = %s, pugst = %s, pudiscount = %s, putotal_amount = %s WHERE purchaseid = %s
        """

        # Execute the update query
        cursor.execute(update_query,
                       (purchase_date, company_id, company_name, item_id, item_name, price, quantity,
                        amount, gst, discount, total_amount, purchase_id))

        # Commit the transaction
        conn.commit()
        fetch_data()  # Refresh the Treeview with updated data
        messagebox.showinfo("Success", "Purchase updated successfully!")

    except pymysql.MySQLError as e:
        messagebox.showerror("Database Error", f"Error: {e}")
    except ValueError as e:
        messagebox.showerror("Validation Error", f"Error: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

def delete_purchase(p_id_entry):
    try:
        # Retrieve the purchase ID from the entry widget
        purchase_id = p_id_entry.get().strip()

        if not purchase_id:
            raise ValueError("Purchase ID is required to delete a record.")

        # Connect to the database
        conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
        cursor = conn.cursor()

        # Prepare the delete query
        delete_query = """
        DELETE FROM purchase WHERE purchaseid = %s
        """

        # Execute the delete query
        cursor.execute(delete_query, (purchase_id,))

        # Commit the transaction
        conn.commit()

        # Refresh the Treeview to reflect the deleted record
        fetch_data()

        messagebox.showinfo("Success", "Purchase deleted successfully!")

    except pymysql.MySQLError as e:
        messagebox.showerror("Database Error", f"Error: {e}")
    except ValueError as e:
        messagebox.showerror("Validation Error", f"Error: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()


def clear_form(p_id_entry, pdt_entry, pcom_id_combobox, pcom_nm_entry, pitem_id_combobox, pitem_nm_entry,
               pprice_entry, pqty_entry, pamt_entry, pgst_entry, pdis_spinbox, ptotal_amt_entry):
    # Clear all entry fields
    p_id_entry.delete(0, END)
    pcom_nm_entry.delete(0, END)
    pitem_nm_entry.delete(0, END)
    pprice_entry.delete(0, END)
    pqty_entry.delete(0, END)
    pamt_entry.delete(0, END)
    pgst_entry.delete(0, END)

    # Reset the Spinbox for discount
    pdis_spinbox.delete(0, END)  # Delete the current value in the Spinbox
    pdis_spinbox.insert(0, 0)  # Reset the Spinbox to 0

    ptotal_amt_entry.delete(0, END)

    # Clear the date field (DateEntry widget)
    if hasattr(pdt_entry, 'set_date'):
        pdt_entry.set_date(datetime.today().date())  # Reset the date to today (or you can set it to None if needed)
    else:
        pdt_entry.delete(0, END)  # For regular Entry widgets, clear the content

    # Clear Company ID and Item ID comboboxes
    pcom_id_combobox.set('Select Id')  # Reset the Company ID combobox
    pitem_id_combobox.set('Select Id')  # Reset the Item ID combobox


def fetch_data():
    try:
        # Connect to the database
        conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
        cursor = conn.cursor()

        # Prepare the select query to fetch all purchase data
        select_query = """
        SELECT purchaseid, purchasedate, comid, comname, itemid, itemname, price, puqty, puamount, pugst, pudiscount, putotal_amount
        FROM purchase
        """

        # Execute the select query
        cursor.execute(select_query)
        result = cursor.fetchall()

        # Clear existing data in the Treeview before inserting new data
        for row in purchase_treeview.get_children():
            purchase_treeview.delete(row)

        # Populate Treeview with fetched data
        for row in result:
            purchase_treeview.insert("", "end", values=row)

    except pymysql.MySQLError as e:
        messagebox.showerror("Database Error", f"Error: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

from datetime import datetime

def on_treeview_select(event, p_id_entry, pdt_entry, pcom_id_combobox, pcom_nm_entry,
                       pitem_id_combobox, pitem_nm_entry, pprice_entry, pqty_entry,
                       pamt_entry, pgst_entry, pdis_spinbox, ptotal_amt_entry):
    selected_item = purchase_treeview.selection()

    if selected_item:
        selected_data = purchase_treeview.item(selected_item[0])["values"]

        if len(selected_data) < 12:  # Ensure you have enough columns
            print("Warning: Selected row does not have enough data.")
            return

        # Fill in each entry widget with the data from the selected row
        p_id_entry.delete(0, END)
        p_id_entry.insert(0, selected_data[0])

        try:
            # Handle the date field properly
            original_date = selected_data[1]
            valid_date = datetime.strptime(original_date, "%Y-%m-%d").date()
            if hasattr(pdt_entry, 'set_date'):
                pdt_entry.set_date(valid_date)  # For DateEntry widgets
            else:
                pdt_entry.delete(0, END)
                pdt_entry.insert(0, valid_date)  # For regular Entry widgets
        except ValueError:
            print(f"Invalid date format: {selected_data[1]}")
            pdt_entry.set_date(datetime.today().date())  # Or set to today's date

        # Set the other fields similarly
        pcom_id_combobox.set(selected_data[2])
        pcom_nm_entry.delete(0, END)
        pcom_nm_entry.insert(0, selected_data[3])

        pitem_id_combobox.set(selected_data[4])
        pitem_nm_entry.delete(0, END)
        pitem_nm_entry.insert(0, selected_data[5])

        pprice_entry.delete(0, END)
        pprice_entry.insert(0, selected_data[6])

        pqty_entry.delete(0, END)
        pqty_entry.insert(0, selected_data[7])

        pamt_entry.delete(0, END)
        pamt_entry.insert(0, selected_data[8])

        pgst_entry.delete(0, END)
        pgst_entry.insert(0, selected_data[9])

        # Correctly set the Spinbox for discount
        pdis_spinbox.delete(0, END)  # Delete the current value in the Spinbox
        pdis_spinbox.insert(0, selected_data[10])  # Insert the new discount value

        ptotal_amt_entry.delete(0, END)
        ptotal_amt_entry.insert(0, selected_data[11])

def search_purchase_data(search_combobox, search_entry):
    search_criteria = search_combobox.get().strip()
    search_value = search_entry.get().strip()

    if not search_value:
        messagebox.showerror("Error", "Please enter a value to search.")
        return

    conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
    cursor = conn.cursor()

    try:
        if search_criteria == "Id":
            query = "SELECT * FROM purchase WHERE purchaseid = %s"
            cursor.execute(query, (search_value,))
        elif search_criteria == "Name":
            query = "SELECT * FROM purchase WHERE itemname LIKE %s"
            cursor.execute(query, ('%' + search_value + '%',))
        elif search_criteria == "All":
            query = "SELECT * FROM purchase"
            cursor.execute(query)

        records = cursor.fetchall()

        # Clear existing data in Treeview
        purchase_treeview.delete(*purchase_treeview.get_children())

        for row in records:
            purchase_treeview.insert("", "end", values=row)

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
        pdf.drawString(540, 1050, "Purchase Report")

        # Set font for table headers and data
        pdf.setFont("Helvetica", 10)

        # Adjusted column widths with increased width for Address and City
        col_widths = [100, 100, 100, 100, 100, 100,100,100, 100, 100, 100, 100]  # Address and City columns increased

        # Draw table headers
        header = ["Purchase Id", "Purchase Date","Company Id", "Company Name", "Item Id","Item Name", "Price","Quantity", "Amount","Gst","Discount","Total Amount"]
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
            query = "SELECT * FROM purchase WHERE purchaseid = %s"
            cursor.execute(query, (search_value,))
            report_name = f"Purchase_Report_{search_value}"  # Dynamic name for the report
        elif search_criteria == "Name":
            query = "SELECT * FROM purchase WHERE itemname LIKE %s"
            cursor.execute(query, ('%' + search_value + '%',))
            report_name = f"Purchase_Report_{search_value}"  # Dynamic name for the report
        elif search_criteria == "All":
            query = "SELECT * FROM purchase"
            cursor.execute(query)
            report_name = "Purchase_Report_All"  # Generic name for all companies

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




def purchase_form(window):
    global back_image,purchase_treeview
    item_frame = Frame(window, width=1270, height=542,bg='#DFF2EB')
    item_frame.place(x=0, y=99)
    heading_label = Label(item_frame, text='Manage Purchase Detail', font=('times new roman', 18, 'bold'),fg='white',
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
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,command=lambda: search_purchase_data(search_combobox, search_entry))
    search_button.grid(row=0, column=2, padx=20)

    show_button = Button(search_frame, text='Show All', font=('times new roman', 13), cursor='hand1', width=10,
                         bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,command=fetch_data)
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
    p_id_label = Label(detail_frame, text='Purchase Id', font=('times new roman', 13), bg='#DFF2EB', height=1)
    p_id_label.grid(row=0, column=0, sticky='e', padx=15, pady=5)
    p_id_entry = Entry(detail_frame, font=('times new roman', 12))
    p_id_entry.grid(row=0, column=1, padx=5, pady=5)

    pdt_label = Label(detail_frame, text='Purchase Date', font=('times new roman', 13), bg='#DFF2EB', height=1)
    pdt_label.grid(row=1, column=0, sticky='e', padx=15, pady=5)
    pdt_entry = DateEntry(detail_frame, width=18, font=('times new roman', 12), state='readonly',date_pattern='dd/mm/yy')
    pdt_entry.grid(row=1, column=1, padx=5, pady=5)

    pcom_id_label = Label(detail_frame, text='Company Id', font=('times new roman', 13), bg='#DFF2EB',height=1)
    pcom_id_label.grid(row=2, column=0, sticky='e', padx=15, pady=5)
    # Create the combobox for company id
    pcom_id_combobox = ttk.Combobox(detail_frame, width=18, values=populate_company_ids(),
                                    font=('times new roman', 12), state='readonly')
    pcom_id_combobox.set('Select Id')
    pcom_id_combobox.grid(row=2, column=1, padx=5, pady=5)

    # Bind the event to the function
    pcom_id_combobox.bind("<<ComboboxSelected>>",
                          lambda event: populate_company_name(event, pcom_id_combobox, pcom_nm_entry))

    pcom_nm_label = Label(detail_frame, text='Company Name', font=('times new roman', 13), bg='#DFF2EB', height=1)
    pcom_nm_label.grid(row=3, column=0, sticky='e', padx=15, pady=5)
    pcom_nm_entry = Entry(detail_frame, font=('times new roman', 12))
    pcom_nm_entry.grid(row=3, column=1, padx=5, pady=5)

    pitem_id_label = Label(detail_frame, text='Item Id', font=('times new roman', 13), bg='#DFF2EB', height=1)
    pitem_id_label.grid(row=0, column=2, sticky='e', padx=15, pady=5)
    pitem_id_combobox = ttk.Combobox(detail_frame, width=18, values=populate_item_ids(),
                                     font=('times new roman', 12), state='readonly')
    pitem_id_combobox.set('Select Id')
    pitem_id_combobox.grid(row=0, column=3, padx=5, pady=5)

    # Bind the event to the function
    pitem_id_combobox.bind("<<ComboboxSelected>>",
                           lambda event: populate_item_name(event, pitem_id_combobox, pitem_nm_entry,
                                                            pprice_entry))

    pitem_nm_label = Label(detail_frame, text='Item Name', font=('times new roman', 13), bg='#DFF2EB', height=1)
    pitem_nm_label.grid(row=1, column=2, sticky='e', padx=15, pady=5)
    pitem_nm_entry = Entry(detail_frame, font=('times new roman', 12))
    pitem_nm_entry.grid(row=1, column=3, padx=5, pady=5)

    pprice_label = Label(detail_frame, text='Price', font=('times new roman', 13), bg='#DFF2EB', height=1)
    pprice_label.grid(row=2, column=2, sticky='e', padx=15, pady=5)
    pprice_entry = Entry(detail_frame, font=('times new roman', 12))
    pprice_entry.grid(row=2, column=3, padx=5, pady=5)
    # Bind the calculate_amount function to the price and quantity entry fields


    pqty_label = Label(detail_frame, text='Quantity', font=('times new roman', 13), bg='#DFF2EB', height=1)
    pqty_label.grid(row=3, column=2, sticky='e', padx=15, pady=5)
    pqty_entry = Entry(detail_frame, font=('times new roman', 12))
    pqty_entry.grid(row=3, column=3, padx=5, pady=5)

    pamt_label = Label(detail_frame, text='Amount', font=('times new roman', 13), bg='#DFF2EB', height=1)
    pamt_label.grid(row=0, column=4, sticky='e', padx=15, pady=5)
    pamt_entry = Entry(detail_frame, font=('times new roman', 12))
    pamt_entry.grid(row=0, column=5, padx=5, pady=5)
    pamt_entry.bind("<Button-1>", lambda event: on_amount_entry_click(pprice_entry, pqty_entry, pamt_entry))

    pgst_label = Label(detail_frame, text='Gst', font=('times new roman', 13), bg='#DFF2EB', height=1)
    pgst_label.grid(row=1, column=4, sticky='e', padx=15, pady=5)
    pgst_entry = Entry(detail_frame, font=('times new roman', 12))
    pgst_entry.grid(row=1, column=5, padx=5, pady=5)
    pgst_entry.bind("<Button-1>", lambda event: on_gst_entry_click(pamt_entry, pgst_entry))


    pdis_label = Label(detail_frame, text='Discount', font=('times new roman', 13), bg='#DFF2EB', height=1)
    pdis_label.grid(row=2, column=4, sticky='e', padx=15, pady=5)

    # Use a Spinbox for discount with a range from 0 to 100
    pdis_spinbox = Spinbox(detail_frame, from_=0, to=100, font=('times new roman', 12), width=19)
    pdis_spinbox.grid(row=2, column=5, padx=5, pady=5)

    ptotal_amt_label = Label(detail_frame, text='Total Amount', font=('times new roman', 13), bg='#DFF2EB', height=1)
    ptotal_amt_label.grid(row=3, column=4, sticky='e', padx=15, pady=5)
    ptotal_amt_entry = Entry(detail_frame, font=('times new roman', 12))
    ptotal_amt_entry.grid(row=3, column=5, padx=5, pady=5)
    ptotal_amt_entry.bind("<Button-1>", lambda event: on_total_amount_entry_click(pamt_entry, pgst_entry, pdis_spinbox,
                                                                                  ptotal_amt_entry))


    button_frame = Frame(item_frame, bg='#DFF2EB')
    button_frame.place(x=280, y=280)

    add_button = Button(button_frame, text='Add', font=('times new roman', 13), cursor='hand1', width=10,
                        bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,command=lambda :add_purchase(p_id_entry,pdt_entry,pcom_id_combobox,pcom_nm_entry,pitem_id_combobox,pitem_nm_entry,pprice_entry,pqty_entry,pamt_entry,pgst_entry,pdis_spinbox,ptotal_amt_entry))
    add_button.grid(row=0, column=0, padx=10)
    update_button = Button(button_frame, text='Update', font=('times new roman', 13), cursor='hand1', width=10,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,command=lambda :update_purchase(p_id_entry, pdt_entry, pcom_id_combobox, pcom_nm_entry, pitem_id_combobox, pitem_nm_entry,
                    pprice_entry, pqty_entry, pamt_entry, pgst_entry, pdis_spinbox, ptotal_amt_entry))
    update_button.grid(row=0, column=1, padx=10)

    # Assuming you are using Tkinter and the button is created like this:
    delete_button = Button(button_frame, text="Delete ", font=('times new roman', 13), cursor='hand1', width=10,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2, command=lambda: delete_purchase(p_id_entry))
    delete_button.grid(row=0, column=2, pady=10)  # Adjust the row/column according to your layout

    clear_button = Button(button_frame, text='Clear', font=('times new roman', 13), cursor='hand1', width=10,
                          bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                          command=lambda: clear_form(p_id_entry, pdt_entry, pcom_id_combobox, pcom_nm_entry,
                                                     pitem_id_combobox, pitem_nm_entry, pprice_entry, pqty_entry,
                                                     pamt_entry, pgst_entry, pdis_spinbox, ptotal_amt_entry))
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
    top_frame.place(x=0, y=350, relwidth=1, height=190)  # Placed at the bottom of item_frame

    # Create horizontal and vertical scrollbars
    horizontal_scrollbar = Scrollbar(top_frame, orient=HORIZONTAL)
    vertical_scrollbar = Scrollbar(top_frame, orient=VERTICAL)

    # Create Treeview
    purchase_treeview = ttk.Treeview(
        top_frame,
        columns=(
            'purid', 'purdt', 'pcomid', 'pcomnm', 'pitemid', 'pitemname','pprice', 'pqty', 'ptotal', 'pgst','pdis','ptamt'),
        show='headings',
        yscrollcommand=vertical_scrollbar.set,
        xscrollcommand=horizontal_scrollbar.set
    )

    # Configure scrollbars
    horizontal_scrollbar.pack(side=BOTTOM, fill=X, pady=(0, 0), padx=(0, 0))
    vertical_scrollbar.pack(side=RIGHT, fill=Y, pady=(0, 0), padx=(0, 0))
    horizontal_scrollbar.config(command=purchase_treeview.xview)
    vertical_scrollbar.config(command=purchase_treeview.yview)

    # Pack the Treeview
    purchase_treeview.pack(fill=BOTH, expand=True, pady=(0, 0))

    # Define headings and columns
    purchase_treeview.heading('purid', text='Purchase Id')
    purchase_treeview.heading('purdt', text='Purchase Date')
    purchase_treeview.heading('pcomid', text='Company Id')
    purchase_treeview.heading('pcomnm', text='Company Name')
    purchase_treeview.heading('pitemid', text='Item Id')
    purchase_treeview.heading('pitemname', text='Item Name')
    purchase_treeview.heading('pprice', text='Price')
    purchase_treeview.heading('pqty', text='Quantity')
    purchase_treeview.heading('ptotal', text='Amount')
    purchase_treeview.heading('pgst', text='Gst')
    purchase_treeview.heading('pdis', text='Discount')
    purchase_treeview.heading('ptamt', text='Total Amount')

    fetch_data()
    # **Bind TreeView Click Event**
    purchase_treeview.bind("<<TreeviewSelect>>", lambda event: on_treeview_select(
        event, p_id_entry, pdt_entry, pcom_id_combobox, pcom_nm_entry,
        pitem_id_combobox, pitem_nm_entry, pprice_entry, pqty_entry,
        pamt_entry, pgst_entry, pdis_spinbox, ptotal_amt_entry))

    purchase_treeview.column('purid', width=180)
    purchase_treeview.column('purdt', width=180)
    purchase_treeview.column('pcomid', width=180)
    purchase_treeview.column('pcomnm', width=180)
    purchase_treeview.column('pitemid', width=180)
    purchase_treeview.column('pitemname', width=180)
    purchase_treeview.column('pprice', width=180)
    purchase_treeview.column('pqty', width=180)
    purchase_treeview.column('ptotal', width=180)
    purchase_treeview.column('pgst', width=180)
    purchase_treeview.column('pdis', width=180)
    purchase_treeview.column('ptamt', width=180)


