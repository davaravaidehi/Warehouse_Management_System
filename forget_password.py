import pymysql
from tkinter import *
from PIL import Image, ImageTk
from tkinter import messagebox
import login  # Import the login.py file (assuming it's available)


def connect_to_db():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="1234",
        database="handloom"
    )
    return conn


def change_password(username, old_password, new_password):
    conn = connect_to_db()
    cursor = conn.cursor()

    # Check if the username and old password match a record
    cursor.execute("SELECT * FROM login WHERE username=%s AND password=%s", (username, old_password))
    record = cursor.fetchone()

    if record:
        # Update the password if credentials are correct
        cursor.execute("UPDATE login SET password=%s WHERE username=%s", (new_password, username))
        conn.commit()
        messagebox.showinfo("Success", "Password changed successfully!")

    else:
        messagebox.showerror("Error", "Incorrect username or password!")

    conn.close()


def passwordform(window):
    window.title('FORGET PASSWORD')
    window.geometry("1166x718")
    window.state("zoomed")
    window.resizable(0, 0)

    # Background Image
    bg_frame = Image.open("F:/vaidehi/image/l1.jpg")
    photo = ImageTk.PhotoImage(bg_frame)
    bg_panel = Label(window, image=photo)
    bg_panel.image = photo
    bg_panel.pack(fill='both', expand='yes')

    # Frame
    lg_frame = Frame(window, bg='#040405', width='890', height='560')
    lg_frame.place(x=200, y=70)

    # Side Image
    side_image = Image.open('F:/vaidehi/image/f_pass.png')
    photo = ImageTk.PhotoImage(side_image)
    side_img = Label(lg_frame, image=photo, bg='#040405')
    side_img.image = photo
    side_img.place(x=0, y=0, width=400, height=600)

    # Sign Image
    sign_image = Image.open("F:/vaidehi/image/fp.png")
    photo = ImageTk.PhotoImage(sign_image)
    sign_image_label = Label(lg_frame, image=photo, bg='#040405')
    sign_image_label.image = photo
    sign_image_label.place(x=540, y=0, height=200)

    # Username Label and Entry
    username_label = Label(lg_frame, text='Username', bg='#040405', font=('yu gothic ui', 13, 'bold'), fg='#4f4e4d')
    username_label.place(x=500, y=200)
    username_entry = Entry(lg_frame, highlightthickness=0, relief=FLAT, bg='#040405', fg='#6b6a69',
                           font=('yu gothic ui', 12, 'bold'))
    username_entry.place(x=530, y=233, width=220)
    username_line = Canvas(lg_frame, width=300, height=2.0, bg='#bdb9b1', highlightthickness=0)
    username_line.place(x=500, y=260)

    # User Icon
    usericon = Image.open("F:/vaidehi/image/us.png")
    photo = ImageTk.PhotoImage(usericon)
    user_icon = Label(lg_frame, image=photo, bg='#040405')
    user_icon.image = photo
    user_icon.place(x=495, y=225)

    # Password Label and Entry
    pas_label = Label(lg_frame, text='Password', bg='#040405', font=('yu gothic ui', 13, 'bold'), fg='#4f4e4d')
    pas_label.place(x=500, y=270)
    pas_entry = Entry(lg_frame, highlightthickness=0, relief=FLAT, bg='#040405', fg='#6b6a69',
                      font=('yu gothic ui', 12, 'bold'), show='*')
    pas_entry.place(x=530, y=303, width=220)
    pas_line = Canvas(lg_frame, width=300, height=2.0, bg='#bdb9b1', highlightthickness=0)
    pas_line.place(x=500, y=330)

    # Password Icon
    pasicon = Image.open("F:/vaidehi/image/p2.jpg")
    photo = ImageTk.PhotoImage(pasicon)
    pas_icon = Label(lg_frame, image=photo, bg='#040405')
    pas_icon.image = photo
    pas_icon.place(x=495, y=295)

    # New Password Label and Entry
    npass_label = Label(lg_frame, text='New Password', bg='#040405', font=('yu gothic ui', 13, 'bold'), fg='#4f4e4d')
    npass_label.place(x=500, y=340)
    npass_entry = Entry(lg_frame, highlightthickness=0, relief=FLAT, bg='#040405', fg='#6b6a69',
                        font=('yu gothic ui', 12, 'bold'), show='*')
    npass_entry.place(x=530, y=373, width=220)
    npass_line = Canvas(lg_frame, width=300, height=2.0, bg='#bdb9b1', highlightthickness=0)
    npass_line.place(x=500, y=400)

    # New Password Icon
    npassicon = Image.open("F:/vaidehi/image/p2.jpg")
    photo = ImageTk.PhotoImage(npassicon)
    npass_icon = Label(lg_frame, image=photo, bg='#040405')
    npass_icon.image = photo
    npass_icon.place(x=495, y=365)

    # Change Password Button
    lgn_button = Label(lg_frame, bg='white')
    lgn_button.place(x=520, y=430, height=40, width=260)

    def on_change_password():
        username = username_entry.get()
        old_password = pas_entry.get()
        new_password = npass_entry.get()

        if username and old_password and new_password:
            change_password(username, old_password, new_password)
        else:
            messagebox.showerror("Error", "All fields must be filled out.")

    login = Button(lgn_button, text="Change Password", font=('yu gothic ui', 13, 'bold'), width=25, bd=0, bg='#040405',
                   cursor='hand2', activebackground='#040405', fg='white', command=on_change_password)
    login.place(x=0, y=0)


# Function to run the application
def pg():
    window = Tk()
    passwordform(window)
    window.mainloop()


if __name__ == '__main__':
    pg()
