from tkinter import *
import re
import pymysql
from reportlab.pdfgen import canvas
from tkinter import ttk, PhotoImage, Entry, Frame, Label, Button, Text, Scrollbar, HORIZONTAL, VERTICAL, BOTH, END
from tkinter import filedialog
import os
import tkinter.messagebox as messagebox



# Connect to MySQL
conn = pymysql.connect(
    host="localhost",      # Change if needed
    user="root",           # Your MySQL username
    password="1234",           # Your MySQL password
    database="handloom"    # Target database
)

# Create a cursor
cursor = conn.cursor()

create_table_query = """
CREATE TABLE IF NOT EXISTS customer (
    custid INT PRIMARY KEY,  
    custname VARCHAR(255) NOT NULL,
    contact VARCHAR(15) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    custcity VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    pincode VARCHAR(10) NOT NULL
);
"""

cursor.execute(create_table_query)
conn.commit()
print("Customer table created successfully!")

def add_customer(custid_entry, custname_entry, custcontact_text, custemail_entry, custaddress_entry, custcity_entry,
                 custpincode_entry):
    conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
    cursor = conn.cursor()

    # Get data from entry fields
    custid = custid_entry.get().strip()
    custname = custname_entry.get().strip()
    custcontact = custcontact_text.get().strip()
    custemail = custemail_entry.get().strip()
    custaddress = custaddress_entry.get("1.0", END).strip()
    custcity = custcity_entry.get().strip()
    custpincode = custpincode_entry.get().strip()

    # ========== VALIDATIONS ========== #
    # 1. Check if any field is empty
    if not all([custid, custname, custcontact, custemail, custaddress, custcity, custpincode]):
        messagebox.showerror("Error", "All fields are required!")
        return

    # 2. Validate Customer ID (Only digits)
    if not custid.isdigit():
        messagebox.showerror("Error", "Customer ID should contain only numbers!")
        return

    # 3. Validate contact number (Only digits & exactly 10 digits)
    if not re.fullmatch(r"\d{10}", custcontact):
        messagebox.showerror("Error", "Contact number must be exactly 10 digits and contain only numbers!")
        return

    # 4. Validate email format
    if not re.fullmatch(r"[^@]+@[^@]+\.(com)$", custemail):
        messagebox.showerror("Error", "Invalid email format! Must contain '@' and end with '.com'")
        return

    # 5. Validate pincode (exactly 6 digits)
    if not re.fullmatch(r"\d{6}", custpincode):
        messagebox.showerror("Error", "Pincode must be exactly 6 digits!")
        return

    # 7. Check if custid, contact number, or email already exists
    cursor.execute("SELECT * FROM customer WHERE custid = %s OR contact = %s OR email = %s",
                   (custid, custcontact, custemail))
    existing_record = cursor.fetchone()

    if existing_record:
        messagebox.showerror("Error", "Customer ID, Email, or Contact number already exists!")
        return

    # Insert into database
    try:
        query = """INSERT INTO customer (custid, custname, contact, email, custcity, address, pincode) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (custid, custname, custcontact, custemail, custcity, custaddress, custpincode))
        conn.commit()
        messagebox.showinfo("Success", "Customer added successfully!")

        fetch_customer_data()
        clear_fields(custid_entry, custname_entry, custcontact_text, custemail_entry, custaddress_entry, custcity_entry,
                     custpincode_entry)
    except pymysql.IntegrityError:
        messagebox.showerror("Error", "Customer ID, Email, or Contact number already exists!")
    finally:
        cursor.close()
        conn.close()


def update_customer(custid, custname, custcontact, custemail, custaddress, custcity, custpincode):
    selected = customer_treeview.selection()
    if not selected:
        messagebox.showerror('Error', 'No row is selected')
        return

    conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
    cursor = conn.cursor()

    try:
        # Check if customer exists
        cursor.execute('SELECT * FROM customer WHERE custid = %s', (custid,))
        current_data = cursor.fetchone()

        if not current_data:
            messagebox.showerror("Error", "Customer not found!")
            return

        # Remove `custid` from fetched data since it's immutable
        current_data = current_data[1:]

        # Trim extra spaces
        custaddress = custaddress.strip()

        new_data = (custname, custcontact, custemail, custcity, custaddress, custpincode)

        # Check if there is any change in data
        if current_data == new_data:
            messagebox.showinfo('Information', 'No changes detected')
            return

        # Update customer details
        cursor.execute(
            """UPDATE customer SET custname=%s, contact=%s, email=%s, custcity=%s, address=%s, 
               pincode=%s  WHERE custid=%s""",
            (custname, custcontact, custemail, custcity, custaddress, custpincode, custid))
        conn.commit()
        fetch_customer_data()
        messagebox.showinfo('Success', 'Customer details updated successfully!')

    except Exception as e:
        messagebox.showerror('Error', f'Error occurred: {e}')

    finally:
        cursor.close()
        conn.close()


def delete_customer(custid_entry, custname_entry, custcontact_text, custemail_entry, custaddress_entry,
                         custcity_entry, custpincode_entry):
    selected = customer_treeview.selection()
    if not selected:
        messagebox.showerror('Error', 'No row is selected')
        return

    result = messagebox.askyesno('Confirm', 'Do you really want to delete the selected customer?')
    if result:
        conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
        cursor = conn.cursor()

        try:
            # Get the selected customer's ID
            content = customer_treeview.item(selected)
            custid = content['values'][0]  # Assuming 'custid' is the first column

            cursor.execute('DELETE FROM customer WHERE custid=%s', (custid,))
            conn.commit()

            # Refresh the TreeView after deletion
            fetch_customer_data()
            messagebox.showinfo('Success', 'Customer record deleted successfully!')
            clear_fields(custid_entry, custname_entry, custcontact_text, custemail_entry, custaddress_entry,
                         custcity_entry, custpincode_entry)

        except Exception as e:
            messagebox.showerror('Error', f'Error occurred: {e}')
        finally:
            cursor.close()
            conn.close()

def clear_fields(custid_entry,custname_entry,custcontact_text,custemail_entry,custaddress_entry,custcity_entry,custpincode_entry):
    custid_entry.delete(0, END)
    custname_entry.delete(0, END)
    custcontact_text.delete(0, END)
    custemail_entry.delete(0, END)
    custaddress_entry.delete(1.0, END)
    custcity_entry.delete(0, END)
    custpincode_entry.delete(0, END)


def select_customer_data(event, custid_entry, custname_entry, custcontact_text, custemail_entry,
                         custaddress_entry, custcity_entry, custpincode_entry):
    """Handles the selection of a customer record from the Treeview and populates the form fields."""

    # Get selected item
    index = customer_treeview.selection()
    if not index:
        return  # If no selection, return early

    content = customer_treeview.item(index)
    row = content['values']

    # Clear existing data in fields
    clear_fields(custid_entry, custname_entry, custcontact_text, custemail_entry, custaddress_entry,
                 custcity_entry, custpincode_entry)

    # Populate fields with selected data
    custid_entry.insert(0, row[0])  # Customer ID
    custname_entry.insert(0, row[1])  # Customer Name
    custcontact_text.insert(0, row[2])  # Contact
    custemail_entry.insert(0, row[3])  # Email
    custaddress_entry.insert(1.0, row[5])  # Address
    custcity_entry.insert(0, row[4])  # City
    custpincode_entry.insert(0, row[6])  # Pincode



def fetch_customer_data():
    try:
        # Establish database connection
        conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
        cursor = conn.cursor()

        # Execute query to fetch company data
        cursor.execute("SELECT * FROM customer")
        records = cursor.fetchall()

        # Clear existing data in Treeview
        customer_treeview.delete(*customer_treeview.get_children())

        # Insert new data into Treeview
        for row in records:
            customer_treeview.insert("", "end", values=row)

    except Exception as e:
        messagebox.showerror("Error", f"Error fetching data: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def search_customer_data(search_combobox, search_entry):
    search_criteria = search_combobox.get().strip()
    search_value = search_entry.get().strip()

    if not search_value:
        messagebox.showerror("Error", "Please enter a value to search.")
        return

    conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
    cursor = conn.cursor()

    try:
        if search_criteria == "Id":
            query = "SELECT * FROM customer WHERE custid = %s"
            cursor.execute(query, (search_value,))
        elif search_criteria == "Name":
            query = "SELECT * FROM customer WHERE custname LIKE %s"
            cursor.execute(query, ('%' + search_value + '%',))
        elif search_criteria == "All":
            query = "SELECT * FROM customer"
            cursor.execute(query)

        records = cursor.fetchall()

        # Clear existing data in Treeview
        customer_treeview.delete(*customer_treeview.get_children())

        for row in records:
            customer_treeview.insert("", "end", values=row)

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
        pdf.drawString(270, 1050, "Customer Report")

        # Set font for table headers and data
        pdf.setFont("Helvetica", 10)

        # Adjusted column widths with increased width for Address and City
        col_widths = [100, 100, 100, 100, 100, 100,100]  # Address and City columns increased

        # Draw table headers
        header = ["Customer Id", "Customer Name","Contact No", "Email", "City", "Address", "Pincode"]
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
            query = "SELECT * FROM customer WHERE custid = %s"
            cursor.execute(query, (search_value,))
            report_name = f"Customer_Report_{search_value}"  # Dynamic name for the report
        elif search_criteria == "Name":
            query = "SELECT * FROM customer WHERE custname LIKE %s"
            cursor.execute(query, ('%' + search_value + '%',))
            report_name = f"Customer_Report_{search_value}"  # Dynamic name for the report
        elif search_criteria == "All":
            query = "SELECT * FROM customer"
            cursor.execute(query)
            report_name = "Customer_Report_All"  # Generic name for all companies

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




def customer_form(window):
    global back_image,customer_treeview
    customer_frame = Frame(window, width=1270, height=542,bg='#DFF2EB')
    customer_frame.place(x=0, y=99)
    heading_label = Label(customer_frame, text='Manage Customer Detail', font=('times new roman', 18, 'bold'),fg='white',
                          bg='#7AB2D3')
    heading_label.place(x=0, y=0, relwidth='1')


    # -----------------------------------------
    top_frame = Frame(customer_frame, bg='#DFF2EB')
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
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                           command=lambda: search_customer_data(search_combobox, search_entry))
    search_button.grid(row=0, column=2, padx=20)

    show_button = Button(search_frame, text='Show All', font=('times new roman', 13), cursor='hand1', width=10,
                         bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,command=fetch_customer_data)
    show_button.grid(row=0, column=3)

    back_image = PhotoImage(file='image\\back .png')
    back_button = Button(customer_frame, image=back_image, border=0, cursor='hand2', bg='#DFF2EB',
                         activebackground='#DFF2EB', command=lambda: customer_frame.place_forget())
    back_button.place(x=13, y=35)

    # -----------------------------------------------------------

    top_frame = Frame(customer_frame, bg='#DFF2EB')
    top_frame.place(x=0, y=350, relwidth=1, height=190)  # Placed at the bottom of item_frame

    horizontal_scrollbar = Scrollbar(top_frame, orient=HORIZONTAL)
    vertical_scrollbar = Scrollbar(top_frame, orient=VERTICAL)

    customer_treeview = ttk.Treeview(top_frame, columns=(
        'custid', 'custname', 'contact', 'email','custcity', 'address', 'pincode'), show='headings',
                                    yscrollcommand=vertical_scrollbar.set, xscrollcommand=horizontal_scrollbar.set)
    horizontal_scrollbar.pack(side=BOTTOM, fill=X, pady=(0, 0), padx=(0, 0))
    vertical_scrollbar.pack(side=RIGHT, fill=Y, pady=(0, 0), padx=(0, 0))
    horizontal_scrollbar.config(command=customer_treeview.xview)
    vertical_scrollbar.config(command=customer_treeview.yview)
    customer_treeview.pack(fill=BOTH, expand=True, pady=(0, 0))

    customer_treeview.heading('custid', text='Customer Id')
    customer_treeview.heading('custname', text='Customer Name')
    customer_treeview.heading('contact', text='Contact No')
    customer_treeview.heading('email', text='Email Id')
    customer_treeview.heading('custcity', text='City')
    customer_treeview.heading('address', text='Address')
    customer_treeview.heading('pincode', text='pincode')


    customer_treeview.column('custid', width=180)
    customer_treeview.column('custname', width=180)
    customer_treeview.column('contact', width=180)
    customer_treeview.column('email', width=180)
    customer_treeview.column('custcity', width=180)
    customer_treeview.column('address', width=180)
    customer_treeview.column('pincode', width=180)


    # Fetch data when the form is first created
    fetch_customer_data()  # Load customer data
    customer_treeview.bind("<ButtonRelease-1>", lambda event: select_customer_data(event,
                                                                                   custid_entry, custname_entry,
                                                                                   custcontact_text, custemail_entry,
                                                                                   custaddress_entry,
                                                                                   custcity_entry, custpincode_entry))

    detail_frame=Frame(customer_frame,bg='#DFF2EB')
    detail_frame.place(x=300,y=90)

    custid_label=Label(detail_frame,text='Customer Id',font=('times new roman', 13),bg='#DFF2EB',height=0,width=9)
    custid_label.grid(row=0,column=0,padx=15,pady=2,sticky='e')
    custid_entry=Entry(detail_frame, font=('times new roman', 13))
    custid_entry.grid(row=0,column=1,padx=5,pady=2)

    custname_label = Label(detail_frame, text='Customer Name', font=('times new roman', 13), bg='#DFF2EB',height=2,width=12)
    custname_label.grid(row=1, column=0, padx=15, pady=2,sticky='e')
    custname_entry = Entry(detail_frame, font=('times new roman', 13))
    custname_entry.grid(row=1, column=1, padx=5, pady=2)

    custcontact_label = Label(detail_frame, text='Contact No', font=('times new roman', 13), bg='#DFF2EB')
    custcontact_label.grid(row=2, column=0, padx=15, pady=2, sticky='e')
    custcontact_text = Entry(detail_frame, font=('times new roman', 13))
    custcontact_text.grid(row=2, column=1,pady=2, padx=2)

    custemail_label = Label(detail_frame, text='Email Id', font=('times new roman', 13), bg='#DFF2EB')
    custemail_label.grid(row=3, column=0, padx=15, pady=2,sticky='e')
    custemail_entry = Entry(detail_frame, font=('times new roman', 13))
    custemail_entry.grid(row=3, column=1, padx=5, pady=2)

    custaddress_label = Label(detail_frame, text='Address', font=('times new roman', 13), bg='#DFF2EB')
    custaddress_label.grid(row=1, column=2, padx=15, pady=2, sticky='e')
    custaddress_entry = Text(detail_frame, width=22, height=4, font=('times new roman', 12))
    custaddress_entry.grid(row=1, column=3, padx=5, pady=2,rowspan=2)

    custcity_label = Label(detail_frame, text='City', font=('times new roman', 13), bg='#DFF2EB')
    custcity_label.grid(row=0, column=2, padx=15, pady=20, sticky='e')
    custcity_entry = Entry(detail_frame, font=('times new roman', 13))
    custcity_entry.grid(row=0, column=3, padx=5, pady=20)

    custpincode_label = Label(detail_frame, text='Pincode', font=('times new roman', 13), bg='#DFF2EB')
    custpincode_label.grid(row=3, column=2, padx=15, pady=2, sticky='e')
    custpincode_entry = Entry(detail_frame, font=('times new roman', 13))
    custpincode_entry.grid(row=3, column=3, padx=5, pady=2)



    #-----------------------------------------------------------------------

    button_frame=Frame(customer_frame,bg='#DFF2EB')
    button_frame.place(x=280,y=295)

    add_button = Button(button_frame, text='Add', font=('times new roman', 13), cursor='hand1', width=10,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,command=lambda :add_customer(custid_entry, custname_entry, custcontact_text, custemail_entry, custaddress_entry, custcity_entry,
                 custpincode_entry))
    add_button.grid(row=0, column=0, padx=10)

    update_button = Button(button_frame, text='Update', font=('times new roman', 13), cursor='hand1', width=10,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                           command=lambda: update_customer(
                               custid_entry.get(), custname_entry.get(),custcontact_text.get(), custemail_entry.get(),custaddress_entry.get("1.0", END),
                               custcity_entry.get(), custpincode_entry.get()))
    update_button.grid(row=0, column=1, padx=10)

    delete_button = Button(button_frame, text='Delete', font=('times new roman', 13), cursor='hand1', width=10,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                           command=lambda :delete_customer(custid_entry, custname_entry, custcontact_text, custemail_entry, custaddress_entry,
                         custcity_entry, custpincode_entry))
    delete_button.grid(row=0, column=2, padx=10)

    clear_button = Button(button_frame, text='Clear', font=('times new roman', 13), cursor='hand1', width=10,
                          bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                          command=lambda: clear_fields(custid_entry, custname_entry, custcontact_text, custemail_entry,
                                                       custaddress_entry, custcity_entry, custpincode_entry))  # Properly call clear_fields on button click
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


