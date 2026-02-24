import random
import string
from tkinter import *
from tkinter import ttk, Label
from tkinter import messagebox, END
from PIL import Image, ImageTk, ImageDraw, ImageFont
import pymysql
import forget_password





# Connect to MySQL
conn = pymysql.connect(
    host="localhost",      # Change if needed
    user="root",           # Your MySQL username
    password="1234",       # Your MySQL password
    database="handloom"    # Target database
)

# Create a cursor
cursor = conn.cursor()

create_table_query = """
CREATE TABLE IF NOT EXISTS login (
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);
"""

cursor.execute(create_table_query)
conn.commit()
print("login table created successfully!")


class loginform:
    def __init__(self, window):
        self.window = window
        self.window.title('LOGIN FORM')
        self.window.geometry("1166x718")
        self.window.state("zoomed")
        self.window.resizable(0, 0)

        self.bg_frame = Image.open("F:/Warehouse_Management_System/image/l1.jpg")
        photo = ImageTk.PhotoImage(self.bg_frame)
        self.bg_panel = Label(self.window, image=photo)
        self.bg_panel.image = photo
        self.bg_panel.pack(fill='both', expand='yes')

        # --betwn frame
        self.lgn_frame = Frame(self.window, bg='#040405', width='890', height='560')
        self.lgn_frame.place(x=200, y=70)

        # --sign in
        self.sign_image = Image.open("F:/Warehouse_Management_System/image/s1.png")
        photo = ImageTk.PhotoImage(self.sign_image)
        self.sign_image_label = Label(self.lgn_frame, image=photo, bg='#040405')
        self.sign_image_label.image = photo
        self.sign_image_label.place(x=490, y=0, height=200)

        self.sign_in = Label(self.lgn_frame, text='ADMIN', bg='#040405', fg='white',
                             font=('yu gothic ui', 13, 'bold'))
        self.sign_in.place(x=600, y=175)

        # --username
        self.username_label = Label(self.lgn_frame, text='Username', bg='#040405', font=('yu gothic ui', 13, 'bold'),
                                    fg='#4f4e4d')
        self.username_label.place(x=500, y=200)
        self.username_entry = Entry(self.lgn_frame, highlightthickness=0, relief=FLAT, bg='#040405', fg='#6b6a69',
                                     font=('yu gothic ui', 12, 'bold'))
        self.username_entry.place(x=530, y=233, width=220)
        self.username_line = Canvas(self.lgn_frame, width=300, height=2.0, bg='#bdb9b1', highlightthickness=0)
        self.username_line.place(x=500, y=260)

        # --usericon
        self.usericon = Image.open("F:/Warehouse_Management_System/image/us.png")
        photo = ImageTk.PhotoImage(self.usericon)
        self.user_icon = Label(self.lgn_frame, image=photo, bg='#040405')
        self.user_icon.image = photo
        self.user_icon.place(x=495, y=225)

        # --password
        self.pass_label = Label(self.lgn_frame, text='Password', bg='#040405', font=('yu gothic ui', 13, 'bold'),
                                fg='#4f4e4d')
        self.pass_label.place(x=500, y=270)
        self.pass_entry = Entry(self.lgn_frame, highlightthickness=0, relief=FLAT, bg='#040405', fg='#6b6a69',
                                font=('yu gothic ui', 12, 'bold'), show='*')
        self.pass_entry.place(x=530, y=303, width=220)
        self.pass_line = Canvas(self.lgn_frame, width=300, height=2.0, bg='#bdb9b1', highlightthickness=0)
        self.pass_line.place(x=500, y=330)

        # --password icon
        self.passicon = Image.open("F:/Warehouse_Management_System/image/p2.jpg")
        photo = ImageTk.PhotoImage(self.passicon)
        self.pass_icon = Label(self.lgn_frame, image=photo, bg='#040405')
        self.pass_icon.image = photo
        self.pass_icon.place(x=495, y=295)

        # --show/hide button for password visibility
        self.show_img = Image.open("F:/Warehouse_Management_System/image/show.jpg")
        self.show_img = ImageTk.PhotoImage(self.show_img)
        self.show_btn = Button(self.lgn_frame, image=self.show_img, bg='#040405', bd=0, command=self.toggle_password)
        self.show_btn.place(x=760, y=295)

        # --captcha generation and display
        self.captcha_text = self.generate_captcha()  # Generate a random captcha
        self.captcha_image = self.create_captcha_image(self.captcha_text)  # Create image for captcha text
        self.captcha_image_tk = ImageTk.PhotoImage(self.captcha_image)

        self.captcha_label = Label(self.lgn_frame, text='Captcha', bg='#040405', font=('yu gothic ui', 13, 'bold'),
                                    fg='#4f4e4d')
        self.captcha_label.place(x=500, y=340)

        self.captcha_display = Label(self.lgn_frame, image=self.captcha_image_tk, bg='#040405')
        self.captcha_display.image = self.captcha_image_tk
        self.captcha_display.place(x=500, y=370)

        self.captcha_entry = Entry(self.lgn_frame, highlightthickness=0, relief=FLAT, bg='white', fg='#6b6a69',
                                   font=('yu gothic ui', 12, 'bold'))
        self.captcha_entry.place(x=600, y=373, width=200)
        self.captcha_line = Canvas(self.lgn_frame, width=300, height=2.0, bg='#bdb9b1', highlightthickness=0)
        self.captcha_line.place(x=500, y=400)

        # --login button
        self.lgn_button = Label(self.lgn_frame, bg='white')
        self.lgn_button.place(x=520, y=420, height=40, width=260)
        self.login = Button(self.lgn_button, text="LOGIN", font=('yu gothic ui', 13, 'bold'), width=25, bd=0,
                            bg='#040405', cursor='hand2', activebackground='#040405', fg='white', command=self.login_action)
        self.login.place(x=0, y=0)

        # --forget password
        self.forgot_btn = Button(self.lgn_frame, text='Forgot Password?', font=('yu gothic ui', 13, 'bold underline'),
                                 fg='red', width=25, bd=0, bg='#040405', cursor='hand2', activebackground='#040405',
                                 command=self.open_forgot_password_form)
        self.forgot_btn.place(x=520, y=460)



        # --left side image
        self.side_image = Image.open('F:/Warehouse_Management_System/image/v3.jpg')
        photo = ImageTk.PhotoImage(self.side_image)
        self.side_img = Label(self.lgn_frame, image=photo, bg='#040405')
        self.side_img.image = photo
        self.side_img.place(x=0, y=0, width=400, height=600)

        # --captcha refresh button
        self.refresh = Image.open("F:/Warehouse_Management_System/image/captcha1.png")
        self.refresh = ImageTk.PhotoImage(self.refresh)
        self.refresh_btn = Button(self.lgn_frame, image=self.refresh, bg='#040405', cursor='hand2', activebackground='#040405', bd=0, command=self.refresh_captcha)
        self.refresh_btn.place(x=570, y=347)

    def generate_captcha(self):
        # Generate a random captcha string
        length = 6
        characters = string.ascii_letters + string.digits
        captcha = ''.join(random.choice(characters) for i in range(length))
        return captcha

    def create_captcha_image(self, captcha_text):
        # Create an image with the captcha text
        width = 80
        height = 26
        captcha_image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(captcha_image)
        font_path = "F:/Warehouse_Management_System/fonts/arialbd.ttf"  # Replace with the actual path to a bold font file
        try:
            font = ImageFont.truetype(font_path, size=15)  # Set size as required
        except IOError:
            # If font is not found, fall back to default font
            font = ImageFont.load_default()
            print("Bold font file not found, using default font.")

        draw.text((10, 5), captcha_text, font=font, fill=(0, 0, 0))
        return captcha_image

    def refresh_captcha(self):
        # Regenerate and display a new captcha image
        self.captcha_text = self.generate_captcha()  # Generate new captcha text
        self.captcha_image = self.create_captcha_image(self.captcha_text)  # Create a new image for the captcha
        self.captcha_image_tk = ImageTk.PhotoImage(self.captcha_image)
        self.captcha_display.configure(image=self.captcha_image_tk)  # Update the captcha display with new image
        self.captcha_display.image = self.captcha_image_tk  # Keep reference to the image

    def login_action(self):
        username = self.username_entry.get()
        password = self.pass_entry.get()
        entered_captcha = self.captcha_entry.get()

        if not username or not password or not entered_captcha:
            messagebox.showerror("Error", "All fields are required!")
            return

        # Check captcha
        if entered_captcha != self.captcha_text:
            messagebox.showerror("Error", "Invalid Captcha! Please try again.")
            self.refresh_captcha()  # Refresh captcha after incorrect attempt
            return

        try:
            cursor.execute("SELECT * FROM login WHERE username=%s AND password=%s", (username, password))
            result = cursor.fetchone()

            if result:
                # Show success message with Yes/No option
                response = messagebox.askyesno("Login Successful", "Would you like to continue?")
                if response:  # If Yes is clicked
                    self.window.destroy()  # Close the login window
                    self.open_dashboard()  # Open the dashboard
                else:  # If No is clicked
                    messagebox.showinfo("Action", "You chose not to continue.")
            else:
                messagebox.showerror("Error", "Invalid Username or Password!")

        except pymysql.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")

    def open_dashboard(self):
        import dashboard  # Import your dashboard module
        dashboard.page()  # Call the page function from dashboard.py to open the dashboard window

    def toggle_password(self):
        # Get current state of password field
        current_state = self.pass_entry.cget('show')

        # If the password is currently hidden (using '*'), show it
        if current_state == '*':
            self.pass_entry.config(show='')  # Show the password
            self.show_img = Image.open("F:/Warehouse_Management_System/image/hide.png")  # Change icon to 'hide'
            self.show_img = ImageTk.PhotoImage(self.show_img)
            self.show_btn.config(image=self.show_img)  # Update button icon
        else:
            self.pass_entry.config(show='*')  # Hide the password
            self.show_img = Image.open("F:/Warehouse_Management_System/image/show.jpg")  # Change icon to 'show'
            self.show_img = ImageTk.PhotoImage(self.show_img)
            self.show_btn.config(image=self.show_img)  # Update button icon

    def open_forgot_password_form(self):
            # This method will be triggered when the forgot password button is clicked
            self.window.destroy()  # Close the current login window
            import forget_password

            forget_password.pg()


def page():
    window = Tk()
    loginform(window)
    window.mainloop()


if __name__ == '__main__':
    page()
