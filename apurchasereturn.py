from tkinter import *
from tkinter import ttk, Label
from PIL import Image,ImageTk
from tkcalendar import DateEntry
from datetime import datetime
import tkinter as tk
import datetime
from tkinter import messagebox, END
from tkinter import Label, Entry
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

create_table_query = """
CREATE TABLE IF NOT EXISTS purchase_return (
    purreturnid INT PRIMARY KEY, -- Removed AUTO_INCREMENT
    purretdate  DATE NOT NULL,
    purchaseid INT NOT NULL,
    comname VARCHAR(255) NOT NULL,
    itemname VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    puqty INT NOT NULL,
    return_quantity INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    pudiscount DECIMAL(5, 2) NOT NULL,
    pugst DECIMAL(5, 2) NOT NULL,
    net_amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (purchaseid) REFERENCES purchase(purchaseid) ON DELETE CASCADE
);


"""

cursor.execute(create_table_query)

conn.commit()
print("Purchase return table created successfully!")

# Close connection
cursor.close()
conn.close()
def populate_purchase_ids(pr_id_combobox):
    # Open a new connection to the database
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="1234",
        database="handloom"
    )
    cursor = conn.cursor()

    # Query to fetch all purchase IDs
    cursor.execute("SELECT purchaseid FROM purchase ORDER BY purchaseid ASC")
    purchase_ids = cursor.fetchall()

    # Insert the purchase IDs into the combobox
    purchase_ids_list = [str(row[0]) for row in purchase_ids]  # Convert tuples to strings
    pr_id_combobox['values'] = purchase_ids_list  # Populate combobox with purchase IDs


    # Close the cursor and connection after use
    cursor.close()
    conn.close()


def fetch_purchase_details(pr_id_combobox, pcnm_entry, pinm_entry, pr_price_entry, pr_qty_entry, prdis_entry):
    purchase_id = pr_id_combobox.get()  # Get selected Purchase ID
    print(f"Selected Purchase ID: {purchase_id}")  # Debugging step

    if purchase_id:
        try:
            # Database Connection
            conn = pymysql.connect(
                host="localhost",
                user="root",
                password="1234",
                database="handloom"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT comname, itemname, price, puqty, pudiscount
                FROM purchase
                WHERE purchaseid = %s
            """, (purchase_id,))

            purchase_data = cursor.fetchone()
            print(f"Fetched Data: {purchase_data}")  # Debugging

            if purchase_data:
                try:
                    # Update Other Fields
                    pcnm_entry.delete(0, END)
                    pcnm_entry.insert(0, purchase_data[0])  # Company name

                    pinm_entry.delete(0, END)
                    pinm_entry.insert(0, purchase_data[1])  # Item name

                    pr_price_entry.delete(0, END)
                    pr_price_entry.insert(0, str(purchase_data[2]))  # Price

                    pr_qty_entry.delete(0, END)
                    pr_qty_entry.insert(0, str(purchase_data[3]))  # Quantity

                    prdis_entry.delete(0, END)
                    prdis_entry.insert(0, str(purchase_data[4]))  # Discount

                except Exception as e:
                    print(f"Error updating fields: {e}")

            else:
                print(f"No data found for Purchase ID {purchase_id}")

        except pymysql.Error as db_err:
            print(f"Database error: {db_err}")

        finally:
            cursor.close()
            conn.close()

def update_amount_on_click(pr_price_entry, pr_qty_entry, pur_ret_qty_entry, prdis_entry, prgst_entry, pr_amt_entry, pr_total_amt_entry):
    try:
        # Extract values safely
        price = float(pr_price_entry.get() or 0)
        total_qty = int(pr_qty_entry.get() or 0)
        return_qty = int(pur_ret_qty_entry.get() or 0)
        discount_rate = float(prdis_entry.get() or 0)

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
        pr_amt_entry.delete(0, END)
        pr_amt_entry.insert(0, f"{amount:.2f}")

        # Update the Total Amount entry field with the base total amount (Amount - Discount - GST)
        pr_total_amt_entry.delete(0, END)
        pr_total_amt_entry.insert(0, f"{base_total_amount:.2f}")

        # Optionally, you can display the GST amount separately if needed:
        prgst_entry.delete(0, END)
        prgst_entry.insert(0, f"{gst_amount:.2f}")

    except ValueError:
        pr_amt_entry.delete(0, END)
        pr_amt_entry.insert(0, "Invalid Input")
        pr_total_amt_entry.delete(0, END)
        pr_total_amt_entry.insert(0, "Invalid Input")

def validate_form(p_ret_id_entry, p_ret_dt_entry, pr_id_combobox, pcnm_entry, pinm_entry, pr_price_entry,
                  pr_qty_entry, pur_ret_qty_entry, pr_amt_entry, prdis_entry, prgst_entry, pr_total_amt_entry):
    # Check if purchase return ID is entered
    if not p_ret_id_entry.get():
        messagebox.showerror("Validation Error", "Purchase Return ID is required!")
        return False

    # Check if return date is selected
    if not p_ret_dt_entry.get_date():
        messagebox.showerror("Validation Error", "Return date is required!")
        return False

    # Check if product ID is selected from the combo box
    if pr_id_combobox.get() == "Select Id":
        messagebox.showerror("Validation Error", "Please select a valid Purchase ID!")
        return False

    # Check if company name is entered
    if not pcnm_entry.get():
        messagebox.showerror("Validation Error", "Company name is required!")
        return False

    # Check if item name is entered
    if not pinm_entry.get():
        messagebox.showerror("Validation Error", "Item name is required!")
        return False

    # Check if price is a valid number
    try:
        price = float(pr_price_entry.get())
        if price <= 0:
            raise ValueError("Price must be greater than zero.")
    except ValueError:
        messagebox.showerror("Validation Error", "Price must be a valid number!")
        return False

    # Check if total quantity is a valid integer
    try:
        total_qty = int(pr_qty_entry.get())
        if total_qty <= 0:
            raise ValueError("Total quantity must be greater than zero.")
    except ValueError:
        messagebox.showerror("Validation Error", "Total quantity must be a valid number!")
        return False

    # Check if return quantity is a valid integer
    try:
        return_qty = int(pur_ret_qty_entry.get())
        if return_qty < 0 or return_qty > total_qty:
            raise ValueError("Return quantity must be a valid number and cannot exceed total quantity.")
    except ValueError:
        messagebox.showerror("Validation Error", "Return quantity must be a valid number!")
        return False

    # Check if discount is a valid number
    try:
        discount_rate = float(prdis_entry.get())
        if discount_rate < 0:
            raise ValueError("Discount cannot be negative.")
    except ValueError:
        messagebox.showerror("Validation Error", "Discount must be a valid number!")
        return False

    # If all checks pass, return True
    return True

def add_purchase_return_record(p_ret_id_entry, p_ret_dt_entry, pr_id_combobox, pcnm_entry, pinm_entry,
                                pr_price_entry, pr_qty_entry, pur_ret_qty_entry, pr_amt_entry, prdis_entry,
                                prgst_entry, pr_total_amt_entry):
    # Validate the form data before inserting
    if not validate_form(p_ret_id_entry, p_ret_dt_entry, pr_id_combobox, pcnm_entry, pinm_entry,
                         pr_price_entry, pr_qty_entry, pur_ret_qty_entry, pr_amt_entry, prdis_entry, prgst_entry, pr_total_amt_entry):
        return  # Return if validation fails

    # Retrieve data from the form entries
    purreturnid = int(p_ret_id_entry.get())  # Purchase Return ID
    purretdate = p_ret_dt_entry.get_date()  # Purchase Return Date
    purchaseid = int(pr_id_combobox.get())  # Purchase ID
    comname = pcnm_entry.get()  # Company Name
    itemname = pinm_entry.get()  # Item Name
    price = float(pr_price_entry.get())  # Price
    puqty = int(pr_qty_entry.get())  # Quantity
    return_quantity = int(pur_ret_qty_entry.get())  # Return Quantity
    amount = float(pr_amt_entry.get())  # Amount
    discount = float(prdis_entry.get())  # Discount
    gst = float(prgst_entry.get())  # GST
    total_amount = float(pr_total_amt_entry.get())  # Total Amount

    try:
        # Establish MySQL connection
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="1234",
            database="handloom"
        )
        cursor = conn.cursor()

        # Insert query
        insert_query = """
        INSERT INTO purchase_return (purreturnid, purretdate, purchaseid, comname, itemname, price, puqty, 
                                     return_quantity, total_amount, pudiscount, pugst, net_amount)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (purreturnid, purretdate, purchaseid, comname, itemname, price, puqty, return_quantity, amount, discount, gst, total_amount)

        cursor.execute(insert_query, values)

        conn.commit()  # Commit the changes
        populate_purchase_return_treeview()
        messagebox.showinfo("Success", "Record added successfully!")  # Show success message

        # Optionally clear the form after success
        clear_form(p_ret_id_entry, p_ret_dt_entry, pr_id_combobox, pcnm_entry, pinm_entry,
                   pr_price_entry, pr_qty_entry, pur_ret_qty_entry, pr_amt_entry, prdis_entry, prgst_entry, pr_total_amt_entry)

    except pymysql.MySQLError as e:
        messagebox.showerror("Error", f"An error occurred while adding the record: {e}")

    finally:
        cursor.close()
        conn.close()
def delete_purchase_return(p_ret_id_entry,p_ret_dt_entry, pr_id_combobox, pcnm_entry, pinm_entry,
                   pr_price_entry, pr_qty_entry, pur_ret_qty_entry, pr_amt_entry, prdis_entry, prgst_entry,
                   pr_total_amt_entry):
    try:
        # Get the Purchase Return ID from the entry field
        purchase_return_id = int(p_ret_id_entry.get())

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
        delete_query = "DELETE FROM purchase_return WHERE purreturnid = %s"

        cursor.execute(delete_query, (purchase_return_id,))

        # Commit the transaction
        conn.commit()

        # Success message
        messagebox.showinfo("Success", "Record deleted successfully!")
        populate_purchase_return_treeview()
        clear_form(p_ret_id_entry, p_ret_dt_entry, pr_id_combobox, pcnm_entry, pinm_entry,
                   pr_price_entry, pr_qty_entry, pur_ret_qty_entry, pr_amt_entry, prdis_entry, prgst_entry,
                   pr_total_amt_entry)


    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", "Failed to delete purchase return record.")

    finally:
        # Close the connection
        cursor.close()
        conn.close()


def clear_form(p_ret_id_entry, p_ret_dt_entry, pr_id_combobox, pcnm_entry, pinm_entry,
               pr_price_entry, pr_qty_entry, pur_ret_qty_entry, pr_amt_entry, prdis_entry, prgst_entry,
               pr_total_amt_entry):
    p_ret_id_entry.delete(0, END)

    # Use None or today's date to reset the date field
    p_ret_dt_entry.set_date(None)  # or p_ret_dt_entry.set_date(date.today())

    pr_id_combobox.set('Select Id')
    pcnm_entry.delete(0, END)
    pinm_entry.delete(0, END)
    pr_price_entry.delete(0, END)
    pr_qty_entry.delete(0, END)
    pur_ret_qty_entry.delete(0, END)
    pr_amt_entry.delete(0, END)
    prdis_entry.delete(0, END)
    prgst_entry.delete(0, END)
    pr_total_amt_entry.delete(0, END)

def update_purchase_return_record(p_ret_id_entry, p_ret_dt_entry, pr_id_combobox, pcnm_entry, pinm_entry,
                                   pr_price_entry, pr_qty_entry, pur_ret_qty_entry, pr_amt_entry, prdis_entry,
                                   prgst_entry, pr_total_amt_entry):
    # Validate the form data before updating
    if not validate_form(p_ret_id_entry, p_ret_dt_entry, pr_id_combobox, pcnm_entry, pinm_entry,
                         pr_price_entry, pr_qty_entry, pur_ret_qty_entry, pr_amt_entry, prdis_entry, prgst_entry, pr_total_amt_entry):
        return  # Return if validation fails

    # Retrieve data from the form entries
    purreturnid = int(p_ret_id_entry.get())  # Purchase Return ID
    purretdate = p_ret_dt_entry.get_date()  # Purchase Return Date
    purchaseid = int(pr_id_combobox.get())  # Purchase ID
    comname = pcnm_entry.get()  # Company Name
    itemname = pinm_entry.get()  # Item Name
    price = float(pr_price_entry.get())  # Price
    puqty = int(pr_qty_entry.get())  # Quantity
    return_quantity = int(pur_ret_qty_entry.get())  # Return Quantity
    amount = float(pr_amt_entry.get())  # Amount
    discount = float(prdis_entry.get())  # Discount
    gst = float(prgst_entry.get())  # GST
    total_amount = float(pr_total_amt_entry.get())  # Total Amount

    try:
        # Establish MySQL connection
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="1234",
            database="handloom"
        )
        cursor = conn.cursor()

        # Update query
        update_query = """
        UPDATE purchase_return
        SET purretdate = %s, purchaseid = %s, comname = %s, itemname = %s, price = %s, puqty = %s, 
            return_quantity = %s, total_amount = %s, pudiscount = %s, pugst = %s, net_amount = %s
        WHERE purreturnid = %s
        """

        values = (purretdate, purchaseid, comname, itemname, price, puqty, return_quantity, amount, discount, gst, total_amount, purreturnid)

        cursor.execute(update_query, values)
        conn.commit()  # Commit the changes

        populate_purchase_return_treeview()

        messagebox.showinfo("Success", "Record updated successfully!")  # Show success message
        # Refresh the Treeview to reflect the changes

        # Optionally clear the form after success
        clear_form(p_ret_id_entry, p_ret_dt_entry, pr_id_combobox, pcnm_entry, pinm_entry,
                   pr_price_entry, pr_qty_entry, pur_ret_qty_entry, pr_amt_entry, prdis_entry, prgst_entry, pr_total_amt_entry)

    except pymysql.MySQLError as e:
        messagebox.showerror("Error", f"An error occurred while updating the record: {e}")

    finally:
        cursor.close()
        conn.close()

def populate_purchase_return_treeview():
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
        cursor.execute("SELECT * FROM purchase_return ORDER BY purreturnid ASC")
        records = cursor.fetchall()

        # Clear existing data in Treeview
        for row in purchase_return_treeview.get_children():
            purchase_return_treeview.delete(row)

        # Insert each record into the Treeview
        for record in records:
            purchase_return_treeview.insert('', 'end', values=record)

    except pymysql.Error as db_err:
        print(f"Database error: {db_err}")
        messagebox.showerror("Error", "Failed to load purchase return data.")
    finally:
        cursor.close()
        conn.close()

from datetime import datetime
def on_treeview_select(event,p_ret_id_entry, p_ret_dt_entry, pr_id_combobox, pcnm_entry, pinm_entry,
                       pr_price_entry,pr_qty_entry, pur_ret_qty_entry, pr_amt_entry, prdis_entry, prgst_entry, pr_total_amt_entry):
    try:
        # Get the selected row item
        selected_item = purchase_return_treeview.selection()

        if selected_item:
            # Get values of the selected row
            selected_values = purchase_return_treeview.item(selected_item, 'values')
            print(f"Selected row values: {selected_values}")
            # Purchase Return ID
            p_ret_id_entry.delete(0, END)
            p_ret_id_entry.insert(0, selected_values[0])

            # Return Date (assuming it's in the second column)
            return_date_str = selected_values[1]  # '2025-02-05'
            # Convert the string to a datetime object using strptime
            return_date = datetime.strptime(return_date_str, "%Y-%m-%d").date()  # Convert to datetime.date object
            p_ret_dt_entry.set_date(return_date)  # Pass the datetime object to the entry field

            # Purchase ID (third column)
            pr_id_combobox.set(selected_values[2])

            # Company Name (fourth column)
            pcnm_entry.delete(0, END)
            pcnm_entry.insert(0, selected_values[3])

            # Item Name (fifth column)
            pinm_entry.delete(0, END)
            pinm_entry.insert(0, selected_values[4])

            # Price (sixth column)
            pr_price_entry.delete(0, END)
            pr_price_entry.insert(0, str(selected_values[5]))

            # Quantity (seventh column)
            pr_qty_entry.delete(0, END)
            pr_qty_entry.insert(0, str(selected_values[6]))

            # Return Quantity (eighth column)
            pur_ret_qty_entry.delete(0, END)
            pur_ret_qty_entry.insert(0, str(selected_values[7]))

            # Amount (ninth column)
            pr_amt_entry.delete(0, END)
            pr_amt_entry.insert(0, str(selected_values[8]))

            # Discount (tenth column)
            prdis_entry.delete(0, END)
            prdis_entry.insert(0, str(selected_values[9]))

            # GST (eleventh column)
            prgst_entry.delete(0, END)
            prgst_entry.insert(0, str(selected_values[10]))

            # Total Amount (twelfth column)
            pr_total_amt_entry.delete(0, END)
            pr_total_amt_entry.insert(0, str(selected_values[11]))

    except Exception as e:
        print(f"Error: {e}")

def search_purchase_return_data(search_combobox, search_entry):
    search_criteria = search_combobox.get().strip()
    search_value = search_entry.get().strip()

    if not search_value:
        messagebox.showerror("Error", "Please enter a value to search.")
        return

    conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
    cursor = conn.cursor()

    try:
        if search_criteria == "Id":
            query = "SELECT * FROM purchase_return WHERE purreturnid = %s"
            cursor.execute(query, (search_value,))
        elif search_criteria == "Name":
            query = "SELECT * FROM purchase_return WHERE itemname LIKE %s"
            cursor.execute(query, ('%' + search_value + '%',))
        elif search_criteria == "All":
            query = "SELECT * FROM purchase_return"
            cursor.execute(query)

        records = cursor.fetchall()

        # Clear existing data in Treeview
        purchase_return_treeview.delete(*purchase_return_treeview.get_children())

        for row in records:
            purchase_return_treeview.insert("", "end", values=row)

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
        pdf.drawString(520, 1050, "Purchase Return Report")

        # Set font for table headers and data
        pdf.setFont("Helvetica", 10)

        # Adjusted column widths with increased width for Address and City
        col_widths = [100, 100, 100, 100, 100, 100,100,100, 100, 100, 100, 100]  # Address and City columns increased

        # Draw table headers
        header = ["Purchase Return Id", "Purchase Return Date","Purchase Id", "Company Name","Item Name", "Price","Quantity", "Return Quantity","Amount","Discount","Gst","Total Amount"]
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
            query = "SELECT * FROM purchase_return WHERE purreturnid = %s"
            cursor.execute(query, (search_value,))
            report_name = f"Purchase_Return_Report_{search_value}"  # Dynamic name for the report
        elif search_criteria == "Name":
            query = "SELECT * FROM purchase_return WHERE itemname LIKE %s"
            cursor.execute(query, ('%' + search_value + '%',))
            report_name = f"Purchase_Return_Report_{search_value}"  # Dynamic name for the report
        elif search_criteria == "All":
            query = "SELECT * FROM purchase_return"
            cursor.execute(query)
            report_name = "Purchase_Return_Report_All"  # Generic name for all companies

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




def purchase_return_form(window):
    global back_image, purchase_return_treeview
    item_frame = Frame(window, width=1270, height=542, bg='#DFF2EB')
    item_frame.place(x=0, y=99)
    heading_label = Label(item_frame, text='Manage Purchase Return Detail', font=('times new roman', 18, 'bold'), fg='white', bg='#7AB2D3')
    heading_label.place(x=0, y=0, relwidth='1')

    #---top frame
    top_frame = Frame(item_frame, bg='#DFF2EB')
    top_frame.place(x=0, y=40, relwidth=1, height=200)
    search_frame = Frame(top_frame, bg='#DFF2EB')
    search_frame.pack()

    search_combobox = ttk.Combobox(search_frame, values=('Id','Name','All'), font=('times new roman', 13), state='readonly')
    search_combobox.set('Search By')
    search_combobox.grid(row=0, column=0, padx=20)

    search_entry = Entry(search_frame, font=('times new roman', 13))
    search_entry.grid(row=0, column=1)

    search_button = Button(search_frame, text='Search', font=('times new roman', 13), cursor='hand1', width=10,
                           height=0, bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3',
                           border=2, command=lambda: search_purchase_return_data(search_combobox, search_entry))
    search_button.grid(row=0, column=2, padx=20)

    show_button = Button(search_frame, text='Show All', font=('times new roman', 13), cursor='hand1', width=10,
                         bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                         command=populate_purchase_return_treeview)
    show_button.grid(row=0, column=3)
    back_image = PhotoImage(file='image\\back .png')
    back_button = Button(item_frame, image=back_image, border=0, cursor='hand2', bg='#DFF2EB', activebackground='#DFF2EB', command=lambda: item_frame.place_forget())
    back_button.place(x=13, y=35)

    detail_frame = Frame(item_frame, bg='#DFF2EB')
    detail_frame.place(x=150, y=110)

    # Configure the columns for consistent spacing and alignment
    for col in range(6):
        detail_frame.grid_columnconfigure(col, weight=1)

    # Set the labels and entries with proper alignment
    p_ret_id_label = Label(detail_frame, text='Purchase Return Id', font=('times new roman', 13), bg='#DFF2EB', height=1)
    p_ret_id_label.grid(row=0, column=0, sticky='e', padx=15, pady=5)
    p_ret_id_entry = Entry(detail_frame, font=('times new roman', 12))
    p_ret_id_entry.grid(row=0, column=1, padx=5, pady=5)

    p_ret_dt_label = Label(detail_frame, text='Purchase Return Date', font=('times new roman', 13), bg='#DFF2EB', height=1)
    p_ret_dt_label.grid(row=1, column=0, sticky='e', padx=15, pady=5)
    p_ret_dt_entry = DateEntry(detail_frame, width=18, font=('times new roman', 12), state='readonly', date_pattern='dd/mm/yy')
    p_ret_dt_entry.grid(row=1, column=1, padx=5, pady=5)

    pr_id_label = Label(detail_frame, text='Purchase Id', font=('times new roman', 13), bg='#DFF2EB', height=1)
    pr_id_label.grid(row=2, column=0, sticky='e', padx=15, pady=5)
    pr_id_combobox = ttk.Combobox(detail_frame, width=18, font=('times new roman', 12), state='readonly')
    pr_id_combobox.set('Select Id')
    pr_id_combobox.grid(row=2, column=1, padx=5, pady=5)
    # Populate the Purchase Ids into the combobox
    populate_purchase_ids(pr_id_combobox)
    # Ensure these entries are created before binding
    pr_id_combobox.bind("<<ComboboxSelected>>", lambda event: fetch_purchase_details(
        pr_id_combobox, pcnm_entry, pinm_entry, pr_price_entry, pr_qty_entry,prdis_entry
    ))



    pcnm_label = Label(detail_frame, text='Company Name', font=('times new roman', 13), bg='#DFF2EB', height=1)
    pcnm_label.grid(row=3, column=0, sticky='e', padx=15, pady=5)
    pcnm_entry = Entry(detail_frame, font=('times new roman', 12))
    pcnm_entry.grid(row=3, column=1, padx=5, pady=5)

    pinm_label = Label(detail_frame, text='Item Name', font=('times new roman', 13), bg='#DFF2EB', height=1)
    pinm_label.grid(row=0, column=2, sticky='e', padx=15, pady=5)
    pinm_entry = Entry(detail_frame, font=('times new roman', 12))
    pinm_entry.grid(row=0, column=3, padx=5, pady=5)

    pr_price_label = Label(detail_frame, text='Price', font=('times new roman', 13), bg='#DFF2EB', height=1)
    pr_price_label.grid(row=1, column=2, sticky='e', padx=15, pady=5)
    pr_price_entry = Entry(detail_frame, font=('times new roman', 12))
    pr_price_entry.grid(row=1, column=3, padx=5, pady=5)

    pr_qty_label = Label(detail_frame, text='Quantity', font=('times new roman', 13), bg='#DFF2EB', height=1)
    pr_qty_label.grid(row=2, column=2, sticky='e', padx=15, pady=5)
    pr_qty_entry = Entry(detail_frame, font=('times new roman', 12))
    pr_qty_entry.grid(row=2, column=3, padx=5, pady=5)


    pur_ret_qty_label = Label(detail_frame, text='Return Quantity', font=('times new roman', 13), bg='#DFF2EB',
                              height=1)
    pur_ret_qty_label.grid(row=3, column=2, sticky='e', padx=15, pady=5)
    pur_ret_qty_entry = Entry(detail_frame, font=('times new roman', 12))
    pur_ret_qty_entry.grid(row=3, column=3, padx=5, pady=5)

    pr_amt_label = Label(detail_frame, text='Amount', font=('times new roman', 13), bg='#DFF2EB', height=1)
    pr_amt_label.grid(row=0, column=4, sticky='e', padx=15, pady=5)
    pr_amt_entry = Entry(detail_frame, font=('times new roman', 12))
    pr_amt_entry.grid(row=0, column=5, padx=5, pady=5)

    # Bind the Amount entry field to update when clicked
    pr_amt_entry.bind("<Button-1>", lambda event: update_amount_on_click(
        pr_price_entry, pr_qty_entry, pur_ret_qty_entry, prdis_entry, prgst_entry, pr_amt_entry, pr_total_amt_entry
    ))

    prdis_label = Label(detail_frame, text='Discount', font=('times new roman', 13), bg='#DFF2EB', height=1)
    prdis_label.grid(row=1, column=4, sticky='e', padx=15, pady=5)
    prdis_entry = Entry(detail_frame, font=('times new roman', 12))
    prdis_entry.grid(row=1, column=5, padx=5, pady=5)

    prgst_label = Label(detail_frame, text='Gst', font=('times new roman', 13), bg='#DFF2EB', height=1)
    prgst_label.grid(row=2, column=4, sticky='e', padx=15, pady=5)
    prgst_entry = Entry(detail_frame, font=('times new roman', 12))
    prgst_entry.grid(row=2, column=5, padx=5, pady=5)

    pr_total_amt_label = Label(detail_frame, text='Total Amount', font=('times new roman', 13), bg='#DFF2EB', height=1)
    pr_total_amt_label.grid(row=3, column=4, sticky='e', padx=15, pady=5)
    pr_total_amt_entry = Entry(detail_frame, font=('times new roman', 12))
    pr_total_amt_entry.grid(row=3, column=5, padx=5, pady=5)



    button_frame = Frame(item_frame, bg='#DFF2EB')
    button_frame.place(x=280, y=280)

    add_button = Button(button_frame, text='Add', font=('times new roman', 13), cursor='hand1', width=10,
                        bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                        command=lambda: add_purchase_return_record(p_ret_id_entry, p_ret_dt_entry, pr_id_combobox,
                                                                   pcnm_entry, pinm_entry, pr_price_entry, pr_qty_entry,
                                                                   pur_ret_qty_entry, pr_amt_entry, prdis_entry,
                                                                   prgst_entry, pr_total_amt_entry))  # Add action
    add_button.grid(row=0, column=0, padx=10)

    update_button = Button(button_frame, text='Update', font=('times new roman', 13), cursor='hand1', width=10,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2
                           ,command=lambda:update_purchase_return_record(p_ret_id_entry, p_ret_dt_entry, pr_id_combobox,
                                                                   pcnm_entry, pinm_entry, pr_price_entry, pr_qty_entry,
                                                                   pur_ret_qty_entry, pr_amt_entry, prdis_entry,
                                                                   prgst_entry, pr_total_amt_entry) )
    update_button.grid(row=0, column=1, padx=10)

    delete_button = Button(button_frame, text='Delete', font=('times new roman', 13), cursor='hand1', width=10,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                           command=lambda :delete_purchase_return(p_ret_id_entry, p_ret_dt_entry, pr_id_combobox,
                                                                     pcnm_entry, pinm_entry, pr_price_entry,
                                                                     pr_qty_entry,
                                                                     pur_ret_qty_entry, pr_amt_entry, prdis_entry,
                                                                     prgst_entry, pr_total_amt_entry))
    delete_button.grid(row=0, column=2, padx=10)

    clear_button = Button(button_frame, text="Clear",font=('times new roman', 13), cursor='hand1', width=10,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                          command=lambda:clear_form(p_ret_id_entry, p_ret_dt_entry, pr_id_combobox,
                                                                     pcnm_entry, pinm_entry, pr_price_entry,
                                                                     pr_qty_entry,
                                                                     pur_ret_qty_entry, pr_amt_entry, prdis_entry,
                                                                     prgst_entry, pr_total_amt_entry)
                          )
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
    purchase_return_treeview = ttk.Treeview(
        top_frame,
        columns=(
        'prrid',  'prrdt','prid', 'prcnm','prinm',  'prprice', 'prqty', 'prrqty', 'prtotal', 'prdis', 'prgst',
        'prtamt'),
        show='headings',
        yscrollcommand=vertical_scrollbar.set,
        xscrollcommand=horizontal_scrollbar.set
    )

    # Configure scrollbars
    horizontal_scrollbar.pack(side=BOTTOM, fill=X, pady=(0, 0), padx=(0,0))
    vertical_scrollbar.pack(side=RIGHT, fill=Y, pady=(0, 0), padx=(0, 0))
    horizontal_scrollbar.config(command=purchase_return_treeview.xview)
    vertical_scrollbar.config(command=purchase_return_treeview.yview)

    # Pack the Treeview
    purchase_return_treeview.pack(fill=BOTH, expand=True, pady=(0, 0))

    # Define headings and columns
    purchase_return_treeview.heading('prrid', text='Purchase Return Id')
    purchase_return_treeview.heading('prrdt', text='Purchase Return Date')
    purchase_return_treeview.heading('prid', text='Purchase Id')
    purchase_return_treeview.heading('prcnm', text='Company Name')
    purchase_return_treeview.heading('prinm', text='Item Name')
    purchase_return_treeview.heading('prprice', text='Price')
    purchase_return_treeview.heading('prqty', text='Quantity')
    purchase_return_treeview.heading('prrqty', text='Return Quantity')
    purchase_return_treeview.heading('prtotal', text='Amount')
    purchase_return_treeview.heading('prdis', text='Discount')
    purchase_return_treeview.heading('prgst', text='Gst')
    purchase_return_treeview.heading('prtamt', text='Total Amount')

    purchase_return_treeview.column('prrid', width=180)
    purchase_return_treeview.column('prrdt', width=180)
    purchase_return_treeview.column('prid', width=180)
    purchase_return_treeview.column('prcnm', width=180)
    purchase_return_treeview.column('prinm', width=180)
    purchase_return_treeview.column('prprice', width=180)
    purchase_return_treeview.column('prqty', width=180)
    purchase_return_treeview.column('prrqty', width=180)
    purchase_return_treeview.column('prtotal', width=170)
    purchase_return_treeview.column('prdis', width=180)
    purchase_return_treeview.column('prgst', width=180)
    purchase_return_treeview.column('prtamt', width=180)
    populate_purchase_return_treeview()
    purchase_return_treeview.bind("<ButtonRelease-1>",
                                  lambda event: on_treeview_select(event, p_ret_id_entry,
                                                                   p_ret_dt_entry,
                                                                   pr_id_combobox, pcnm_entry, pinm_entry,
                                                                   pr_price_entry, pr_qty_entry,
                                                                   pur_ret_qty_entry, pr_amt_entry, prdis_entry,
                                                                   prgst_entry, pr_total_amt_entry))
