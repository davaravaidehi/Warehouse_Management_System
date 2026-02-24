from tkinter import *
from tkinter import Label
from datetime import datetime
from tkinter import ttk, Label
from PIL import Image,ImageTk
from tkinter import messagebox
from tkinter import Label, Entry
from company import company_form
import qrcode
import pymysql
from acustomer import customer_form
from aitem import item_form
from apurchase import purchase_form
from apurchasereturn import purchase_return_form
from asales import sales_form
from asalesreturn import sales_return_form
from stock import stock_form
from bill import bill_form
from login import loginform

def page():

    def on_enter(x):
        x.configure(fg='#7AB2D3')  # hover color
    def on_leave(x):
        x.configure(fg='white')

    def confirm_logout():
        response = messagebox.askyesno("Logout", "Are you sure you want to log out?")
        if response:  # User clicked "Yes"
            window.quit()  # Close the dashboard window
            loginform(window)  # Call the login page function to open the login page
        else:  # User clicked "No"
            pass  # Do nothing, keep the dashboard open

    #--heading frame

    window=Tk()
    window.title('Dashboard')
    window.geometry("1270x670+0+0")
    window.resizable(0,0)
    window.config(bg="white")

    bg_Image = PhotoImage(file='image\\logo5.png')
    titleLabel = Label(window, image=bg_Image, text="       Inventory Management System",compound=LEFT,
                       font=('times new roman', 38, 'bold'), bg='black', fg='white', anchor='w', padx=70)
    titleLabel.place(x=0, y=0, relwidth=1)

    logoutButton = Button(window, text='Logout', font=('times new roman', 20, 'bold'), bg='#2F2F2F', fg='white',
                          activebackground='#2F2F2F', activeforeground='#7AB2D3', border=0, command=confirm_logout)
    logoutButton.place(x=1100, y=9.5)


    def update_time( ):
        

        # Get the current date and time
        current_time = datetime.now().strftime('%I:%M:%S %p')  # 12-hour format with AM/PM
        current_date = datetime.now().strftime('%d-%m-%Y')  # Date in format: dd-mm-yyyy

        # Update the text of the label
        subtitleLabel.config(text=f'Time: {current_time}   \t\t Welcome To Khodiyar Handloom \t\t\t Date: {current_date}')

        # Call this function every 1000 ms (1 second) to update the time continuously
        window.after(1000, update_time)

    # Create the label that will display the time and date
    subtitleLabel = Label(window, text='', font=('times new roman', 15, 'bold'), bg='#B9E5E8', fg='black')
    subtitleLabel.place(x=0, y=70, relwidth=1)

    # Call the function to start updating the time
    update_time()


    # ------------------ left frame ---------------------
    leftframe = Frame(window, bg='black')
    leftframe.place(x=0, y=99, width=252, height=795)

    # Open and resize the image
    image = Image.open("image\\fff.jpg")  # Replace with your image file path
    image = image.resize((1015, 550), Image.Resampling.LANCZOS)  # Resize the image to fit
    img = ImageTk.PhotoImage(image)  # Convert to Tkinter-compatible photo image

    # Create a label to display the image
    image_label = Label(window, image=img)
    image_label.place(x=250, y=97)  # Position the label (you can adjust coordinates)

    # Keep a reference to the image to avoid garbage collection
    image_label.image = img

    # .............. menu label ..........................

    menuLabel = Label(leftframe, text='Menu', font=('times new roman', 20, 'bold'), bg='#7AB2D3')
    menuLabel.pack(fill=X)

     

    company_icon = PhotoImage(file='image\\company1.png')
    company_button = Button(leftframe, image=company_icon, compound=LEFT, text='  Company', bd=0,
                             font=('times new roman', 20, 'bold'), bg='black', fg='white', activebackground='#2F2F2F',
                             activeforeground='#7AB2D3', border=0, anchor='w', padx=1, height=30,command=lambda :company_form(window))
    company_button.pack(fill=X, pady=10)

    customer_icon = PhotoImage(file='image\\customer.png')
    customer_button = Button(leftframe, image=customer_icon, compound=LEFT, text='  Customer', bd=0,
                             font=('times new roman', 20, 'bold'), bg='black', fg='white', activebackground='#2F2F2F',
                             activeforeground='#7AB2D3', border=0, anchor='w', padx=1, height=30,command=lambda :customer_form(window))
    customer_button.pack(fill=X, pady=10)

    product_icon = PhotoImage(file='image\\product2.png')
    product_button = Button(leftframe, image=product_icon, compound=LEFT, text='  Item',
                             font=('times new roman', 20, 'bold'), bg='black', fg='white', activebackground='#2F2F2F',
                             activeforeground='#7AB2D3', border=0, anchor='w', padx=1,height=30,command=lambda :item_form(window))
    product_button.pack(fill=X, pady=10)

    purchase_icon = PhotoImage(file='image\\purchase1.png')
    purchase_button = Button(leftframe, image=purchase_icon, compound=LEFT, text='  Purchase',
                             font=('times new roman', 20, 'bold'), bg='black', fg='white', activebackground='#2F2F2F',
                             activeforeground='#7AB2D3', border=0, anchor='w', padx=1, height=30,command=lambda :purchase_form(window))
    purchase_button.pack(fill=X, pady=10)

    purchase_return_icon = PhotoImage(file='image\\pur_ret.png')
    purchase_return_button = Button(leftframe, image=purchase_return_icon, compound=LEFT, text='  Purchase return',
                            font=('times new roman', 20, 'bold'), bg='black', fg='white', activebackground='#2F2F2F',
                            activeforeground='#7AB2D3', border=0, anchor='w', padx=1, height=30,command=lambda :purchase_return_form(window))
    purchase_return_button.pack(fill=X, pady=10)

    sales_icon = PhotoImage(file='image\\sales1.png')
    sales_button = Button(leftframe, image=sales_icon, compound=LEFT, text='  Sales',
                          font=('times new roman', 20, 'bold'),
                          bg='black', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=0,
                          anchor='w', padx=1, height=30,command=lambda :sales_form(window))
    sales_button.pack(fill=X, pady=10)

    sales_return_icon = PhotoImage(file='image\\pur_ret.png')
    sales_return_button = Button(leftframe, image=sales_return_icon, compound=LEFT, text='  Sales return',
                            font=('times new roman', 20, 'bold'), bg='black', fg='white', activebackground='#2F2F2F',
                            activeforeground='#7AB2D3', border=0, anchor='w', padx=1, height=30,command=lambda :sales_return_form(window))
    sales_return_button.pack(fill=X, pady=10)

    stock_icon = PhotoImage(file='image\\stock.png')
    stock_button = Button(leftframe, image=stock_icon, compound=LEFT, text='  Stock', bd=0,
                             font=('times new roman', 20, 'bold'), bg='black', fg='white', activebackground='#2F2F2F',
                             activeforeground='#7AB2D3', border=0, anchor='w', padx=1, height=30,command=lambda :stock_form(window))
    stock_button.pack(fill=X, pady=10)

    bill_icon = PhotoImage(file='image\\bill.png')
    bill_button = Button(leftframe, image=bill_icon, compound=LEFT, text='  Bill', bd=0,
                             font=('times new roman', 20, 'bold'), bg='black', fg='white', activebackground='#2F2F2F',
                             activeforeground='#7AB2D3', border=0, anchor='w', padx=1, height=30,command=lambda :bill_form(window))
    bill_button.pack(fill=X, pady=10)

    '''exit_icon = PhotoImage(file='image\\exit.png')
    exit_button = Button(leftframe, image=exit_icon, compound=LEFT, text='  Exit', bd=0, font=('times new roman', 20, 'bold'),
                         bg='black', fg='white', activebackground='#2F2F2F', activeforeground='#7AB2D3', border=0,
                         anchor='w', padx=1, height=30)
    exit_button.pack(fill=X, pady=10)'''

    buttons = [company_button, product_button, purchase_button, purchase_return_button, sales_button,stock_button,
               logoutButton]

    # button hover effect

    for btn1 in buttons:
        btn1.bind("<Enter>", lambda event, x=btn1: on_enter(x))

    for btn1 in buttons:
        btn1.bind("<Leave>", lambda event, x=btn1: on_leave(x))


    window.mainloop()
if __name__ == '__main__':
    page()
