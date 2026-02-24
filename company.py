from tkinter import *
from tkinter import messagebox, END
from tkinter import ttk
import re
import pymysql
import os
from tkinter import filedialog
from reportlab.pdfgen import canvas
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

create_table_query = """
CREATE TABLE IF NOT EXISTS company (
    comid INT PRIMARY KEY,  -- Removed AUTO_INCREMENT
    comname VARCHAR(255) NOT NULL,
    comadd TEXT NOT NULL,
    comcontact VARCHAR(15) UNIQUE NOT NULL,
    comemail VARCHAR(255) UNIQUE NOT NULL,
    comcity VARCHAR(100) NOT NULL
);
"""

cursor.execute(create_table_query)
conn.commit()
print("Company table created successfully!")

# Close connection
cursor.close()
conn.close()

def add_company(comid_entry,comname_entry,comadd_text,comcontact_entry,comemail_entry,comcity_entry):
    conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
    cursor = conn.cursor()

    # Get data from entry fields
    comid = comid_entry.get().strip()
    comname = comname_entry.get().strip()
    comadd = comadd_text.get("1.0", END).strip()
    comcontact = comcontact_entry.get().strip()
    comemail = comemail_entry.get().strip()
    comcity = comcity_entry.get().strip()

    # ========== VALIDATIONS ========== #
    # 1. Check if any field is empty
    if not all([comid, comname, comadd, comcontact, comemail, comcity]):
        messagebox.showerror("Error", "All fields are required!")
        return

    # 2. Validate Company ID (Only digits)
    if not comid.isdigit():
        messagebox.showerror("Error", "Company ID should contain only numbers!")
        return

    # 3. Validate contact number (Only digits & exactly 10 digits)
    if not re.fullmatch(r"\d{10}", comcontact):
        messagebox.showerror("Error", "Contact number must be exactly 10 digits and contain only numbers!")
        return

    # 4. Validate email format
    if not re.fullmatch(r"[^@]+@[^@]+\.(com)$", comemail):
        messagebox.showerror("Error", "Invalid email format! Must contain '@' and end with '.com'")
        return


    # 6. Check if comid, contact number or email already exists
    cursor.execute("SELECT * FROM company WHERE comid = %s OR comcontact = %s OR comemail = %s", (comid, comcontact, comemail))
    existing_record = cursor.fetchone()

    if existing_record:
        messagebox.showerror("Error", "Company ID, Email, or Contact number already exists!")
        return

    # Insert into database
    try:
        query = """INSERT INTO company (comid, comname, comadd, comcontact, comemail, comcity) 
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (comid, comname, comadd, comcontact, comemail, comcity))
        conn.commit()
        messagebox.showinfo("Success", "Company added successfully!")
        fetch_company_data()# Refresh table data
        clear_fields()  # Clear fields after insertion
    except pymysql.IntegrityError:
        messagebox.showerror("Error", "Company ID, Email, or Contact number already exists!")
    finally:
        cursor.close()
        conn.close()


def update_company(comid, comname, comadd, comcontact, comemail, comcity):
    selected = company_treeview.selection()
    if not selected:
        messagebox.showerror('Error', 'No row is selected')
        return

    conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
    cursor = conn.cursor()

    try:
        # Check if company exists
        cursor.execute('SELECT * FROM company WHERE comid = %s', (comid,))
        current_data = cursor.fetchone()

        if not current_data:
            messagebox.showerror("Error", "Company not found!")
            return

        # Remove `comid` from fetched data since it's immutable
        current_data = current_data[1:]

        # Trim extra spaces
        comadd = comadd.strip()

        new_data = (comname, comadd, comcontact, comemail, comcity)

        # Check if there is any change in data
        if current_data == new_data:
            messagebox.showinfo('Information', 'No changes detected')
            return

        # Update company details
        cursor.execute(
            """UPDATE company SET comname=%s, comadd=%s, comcontact=%s, comemail=%s, comcity=%s WHERE comid=%s""",
            (comname, comadd, comcontact, comemail, comcity, comid)
        )
        conn.commit()

        fetch_company_data()  # Refresh data in Treeview
        messagebox.showinfo('Success', 'Company details updated successfully!')

    except Exception as e:
        messagebox.showerror('Error', f'Error occurred: {e}')

    finally:
        cursor.close()
        conn.close()


def delete_company():
    selected = company_treeview.selection()
    if not selected:
        messagebox.showerror('Error', 'No row is selected')
        return

    result = messagebox.askyesno('Confirm', 'Do you really want to delete the selected company?')
    if result:
        conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
        cursor = conn.cursor()

        try:
            # Get the selected company's ID
            content = company_treeview.item(selected)
            comid = content['values'][0]  # Assuming 'comid' is the first column

            cursor.execute('DELETE FROM company WHERE comid=%s', (comid,))
            conn.commit()

            # Refresh the TreeView after deletion
            fetch_company_data()
            messagebox.showinfo('Success', 'Company record deleted successfully!')

        except Exception as e:
            messagebox.showerror('Error', f'Error occurred: {e}')
        finally:
            cursor.close()
            conn.close()



def clear_fields(comid_entry,comname_entry,comadd_text,comcontact_entry,comemail_entry, comcity_combobox):
    comid_entry.delete(0, END)
    comname_entry.delete(0, END)
    comadd_text.delete("1.0", END)
    comcontact_entry.delete(0, END)
    comemail_entry.delete(0, END)
    comcity_combobox.set('')

import pymysql
from tkinter import messagebox

def fetch_company_data():
    try:
        # Establish database connection
        conn = pymysql.connect(host="localhost", user="root", password="1234", database="handloom")
        cursor = conn.cursor()

        # Execute query to fetch company data
        cursor.execute("SELECT * FROM company")
        records = cursor.fetchall()

        # Clear existing data in Treeview
        company_treeview.delete(*company_treeview.get_children())

        # Insert new data into Treeview
        for row in records:
            company_treeview.insert("", "end", values=row)

    except Exception as e:
        messagebox.showerror("Error", f"Error fetching data: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def select_company_data(event, comid_entry, comname_entry, comadd_text, comcontact_entry, comemail_entry,
                        comcity_entry):
    """Handles the selection of a company record from the Treeview and populates the form fields."""

    # Get selected item
    index = company_treeview.selection()
    if not index:
        return  # If no selection, return early

    content = company_treeview.item(index)
    row = content['values']

    # Clear existing data in fields
    clear_fields(comid_entry, comname_entry, comadd_text, comcontact_entry, comemail_entry, comcity_entry)

    # Populate fields with selected data
    comid_entry.insert(0, row[0])  # Company ID
    comname_entry.insert(0, row[1])  # Company Name
    comadd_text.insert(1.0, row[2])  # Address
    comcontact_entry.insert(0, row[3])  # Contact
    comemail_entry.insert(0, row[4])  # Email
    comcity_entry.insert(0, row[5])  # City

def search_company_data(search_combobox, search_entry):
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
            query = "SELECT * FROM company WHERE comid = %s"
            cursor.execute(query, (search_value,))
        elif search_criteria == "Name":
            query = "SELECT * FROM company WHERE comname LIKE %s"
            cursor.execute(query, ('%' + search_value + '%',))
        elif search_criteria == "All":
            query = "SELECT * FROM company"
            cursor.execute(query)

        records = cursor.fetchall()

        # Clear existing data in Treeview
        company_treeview.delete(*company_treeview.get_children())

        # Insert new data into Treeview
        for row in records:
            company_treeview.insert("", "end", values=row)

    except Exception as e:
        messagebox.showerror("Error", f"Error fetching data: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



# Function to search for company data by Id or Name
def search_company_data(search_combobox, search_entry):
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
            query = "SELECT * FROM company WHERE comid = %s"
            cursor.execute(query, (search_value,))
        elif search_criteria == "Name":
            query = "SELECT * FROM company WHERE comname LIKE %s"
            cursor.execute(query, ('%' + search_value + '%',))
        elif search_criteria == "All":
            query = "SELECT * FROM company"
            cursor.execute(query)

        records = cursor.fetchall()

        # Clear existing data in Treeview
        company_treeview.delete(*company_treeview.get_children())

        # Insert new data into Treeview
        for row in records:
            company_treeview.insert("", "end", values=row)

    except Exception as e:
        messagebox.showerror("Error", f"Error fetching data: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
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
        page_width = 800  # Custom width to increase space on the page
        page_height = 1100  # Standard height (you can adjust this as well)

        # Create a canvas object to generate the PDF
        pdf = canvas.Canvas(report_path, pagesize=(page_width, page_height))
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(300, 1050, "Company Report")

        # Set font for table headers and data
        pdf.setFont("Helvetica", 10)

        # Adjusted column widths with increased width for Address and City
        col_widths = [100, 100, 200, 100, 150, 100]  # Address and City columns increased

        # Draw table headers
        header = ["Company Id", "Company Name", "Address", "Contact", "Email", "City"]
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
            query = "SELECT * FROM company WHERE comid = %s"
            cursor.execute(query, (search_value,))
            report_name = f"Company_Report_{search_value}"  # Dynamic name for the report
        elif search_criteria == "Name":
            query = "SELECT * FROM company WHERE comname LIKE %s"
            cursor.execute(query, ('%' + search_value + '%',))
            report_name = f"Company_Report_{search_value}"  # Dynamic name for the report
        elif search_criteria == "All":
            query = "SELECT * FROM company"
            cursor.execute(query)
            report_name = "Company_Report_All"  # Generic name for all companies

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
from tkinter import filedialog
import os
import tkinter.messagebox as messagebox


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


def company_form(window):
    global back_image, company_treeview
    company_frame = Frame(window, width=1270, height=542,bg='#DFF2EB')
    company_frame.place(x=0, y=99)
    heading_label = Label(company_frame, text='Manage Company Detail', font=('times new roman', 18, 'bold'),fg='white',
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
                           border=2, command=lambda: search_company_data(search_combobox,
                                                                         search_entry))  # Use the function for searching
    search_button.grid(row=0, column=2, padx=20)

    show_button = Button(search_frame, text='Show All', font=('times new roman', 13), cursor='hand1', width=10,
                         bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,command=fetch_company_data)
    show_button.grid(row=0, column=3)

    back_image = PhotoImage(file='image\\back .png')
    back_button = Button(company_frame, image=back_image, border=0, cursor='hand2', bg='#DFF2EB',
                         activebackground='#DFF2EB', command=lambda: company_frame.place_forget())
    back_button.place(x=13, y=35)
    # -----------------------------------------------------------
    # Adjusted Top Frame and Treeview placement
    top_frame = Frame(company_frame, bg='#DFF2EB')
    top_frame.place(x=0, y=350, relwidth=1, height=190)  # Placed at the bottom of item_frame

    # Create horizontal and vertical scrollbars
    horizontal_scrollbar = Scrollbar(top_frame, orient=HORIZONTAL)
    vertical_scrollbar = Scrollbar(top_frame, orient=VERTICAL)

    company_treeview = ttk.Treeview(top_frame, columns=(
        'comid', 'comname', 'comadd', 'comcontact', 'comemail', 'comcity'), show='headings',yscrollcommand=vertical_scrollbar.set,xscrollcommand=horizontal_scrollbar.set)
    horizontal_scrollbar.pack(side=BOTTOM, fill=X, pady=(0, 0), padx=(0,0))
    vertical_scrollbar.pack(side=RIGHT, fill=Y, pady=(0, 0), padx=(0, 0))
    horizontal_scrollbar.config(command=company_treeview.xview)
    vertical_scrollbar.config(command=company_treeview.yview)
    company_treeview.pack(fill=BOTH, expand=True, pady=(0, 0))

    company_treeview.heading('comid', text='Company Id')
    company_treeview.heading('comname', text='Company Name')
    company_treeview.heading('comadd', text='Address')
    company_treeview.heading('comcontact', text='Contact')
    company_treeview.heading('comemail', text='Email')
    company_treeview.heading('comcity', text='City')

    company_treeview.column('comid',width=180)
    company_treeview.column('comname',width=180)
    company_treeview.column('comadd',width=180)
    company_treeview.column('comcontact',width=180)
    company_treeview.column('comemail',width=180)
    company_treeview.column('comcity',width=180)

    fetch_company_data()
    company_treeview.bind("<ButtonRelease-1>", lambda event: select_company_data(event, comid_entry, comname_entry,
                                                                                 comadd_text, comcontact_entry,
                                                                                 comemail_entry, comcity_combobox))

    detail_frame=Frame(company_frame,bg='#DFF2EB')
    detail_frame.place(x=290,y=90)

    comid_label=Label(detail_frame,text='Company Id',font=('times new roman', 13),bg='#DFF2EB',height=0,width=9)
    comid_label.grid(row=0,column=0,padx=15,pady=2,sticky='e')
    comid_entry=Entry(detail_frame, font=('times new roman', 13))
    comid_entry.grid(row=0,column=1,padx=5,pady=2)

    comname_label = Label(detail_frame, text='Company Name', font=('times new roman', 13), bg='#DFF2EB',height=2,width=12)
    comname_label.grid(row=1, column=0, padx=15, pady=2,sticky='e')
    comname_entry = Entry(detail_frame, font=('times new roman', 13))
    comname_entry.grid(row=1, column=1, padx=5, pady=2)

    comadd_label = Label(detail_frame, text='Address', font=('times new roman', 13), bg='#DFF2EB')
    comadd_label.grid(row=2, column=0, padx=15, pady=2, sticky='e')
    comadd_text = Text(detail_frame, width=22, height=4, font=('times new roman', 12))
    comadd_text.grid(row=2, column=1,padx=5,pady=10, rowspan=2)

    comcontact_label = Label(detail_frame, text='Contact', font=('times new roman', 13), bg='#DFF2EB')
    comcontact_label.grid(row=0, column=2, padx=15, pady=2,sticky='e')
    comcontact_entry = Entry(detail_frame, font=('times new roman', 13))
    comcontact_entry.grid(row=0, column=3, padx=5, pady=2)

    comemail_label = Label(detail_frame, text='Email', font=('times new roman', 13), bg='#DFF2EB')
    comemail_label.grid(row=1, column=2, padx=15, pady=2, sticky='e')
    comemail_entry = Entry(detail_frame, font=('times new roman', 13))
    comemail_entry.grid(row=1, column=3, padx=5, pady=2)

    comcity_label = Label(detail_frame, text='City', font=('times new roman', 13), bg='#DFF2EB')
    comcity_label.grid(row=2, column=2, padx=15, pady=2, sticky='e')
    city_options = ['Ahmedabad', 'Surat', 'Baroda', 'Pune', 'Navsari']
    comcity_combobox = ttk.Combobox(detail_frame, values=city_options, font=('times new roman', 13), width=18)
    comcity_combobox.set('Select city')
    comcity_combobox.grid(row=2, column=3, padx=5, pady=2)

    #-----------------------------------------------------------------------

    button_frame=Frame(company_frame,bg='#DFF2EB')
    button_frame.place(x=280,y=290)

    add_button = Button(button_frame, text='Add', font=('times new roman', 13), cursor='hand1', width=10,
                        bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,command=lambda :add_company(comid_entry,comname_entry,comadd_text,comcontact_entry,comemail_entry,comcity_combobox))  # Add this command

    add_button.grid(row=0, column=0, padx=10)

    update_button = Button(button_frame, text='Update', font=('times new roman', 13), cursor='hand1', width=10,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                           command=lambda: update_company(
                               comid_entry.get().strip(), comname_entry.get().strip(),
                               comadd_text.get("1.0", END).strip(), comcontact_entry.get().strip(),
                               comemail_entry.get().strip(), comcity_combobox.get().strip()))
    update_button.grid(row=0, column=1, padx=10)

    delete_button = Button(button_frame, text='Delete', font=('times new roman', 13), cursor='hand1', width=10,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                           command=delete_company)  # Now calls delete_company function
    delete_button.grid(row=0, column=2, padx=10)

    clear_button = Button(button_frame, text='Clear', font=('times new roman', 13), cursor='hand1', width=10,
                          bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,command=lambda :clear_fields(comid_entry,comname_entry,comadd_text,comcontact_entry,comemail_entry, comcity_combobox))
    clear_button.grid(row=0, column=3, padx=10)

    report_button = Button(button_frame, text='Report', font=('times new roman', 13), cursor='hand1', width=10,
                           bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                           command=lambda: on_report_button_click(search_combobox, search_entry))  # Updated function for report generation
    report_button.grid(row=0, column=4, padx=10)

    # Add the Fetch button
    fetch_button = Button(button_frame, text='View', font=('times new roman', 13), cursor='hand1', width=10,
                          bg='#2F2F2F', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=2,
                          command=open_pdf_report)  # Call open_pdf_report function
    fetch_button.grid(row=0, column=5, padx=10)





