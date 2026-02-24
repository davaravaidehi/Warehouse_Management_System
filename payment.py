import tkinter as tk
from tkinter import messagebox
import qrcode
from PIL import Image, ImageTk
import webbrowser

def generate_qr_code(upiid):
    # Generate QR code for UPI ID
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(upiid)
    qr.make(fit=True)

    # Create an image from the QR code
    img = qr.make_image(fill='black', back_color='white')

    # Convert the image to Tkinter format
    img_tk = ImageTk.PhotoImage(img)

    # Display the QR code image in the Tkinter window
    label.config(image=img_tk)
    label.image = img_tk  # Keep a reference to the image to avoid garbage collection

    # Update the link label to show the UPI ID
    link_label.config(text=f"UPI ID: {upiid}")
    link_label.bind("<Button-1>", lambda e: open_upi_link(upiid))

def open_upi_link(upiid):
    # Function to open the UPI link in a web browser (can be customized for UPI payment)
    webbrowser.open(f"upi://pay?pa={upiid}")

# Set up the main window
root = tk.Tk()
root.title("QR Code Generator")

# Define UPI ID
upi_id = "khodiyarhandloom@aksbi"

# Create a label for the heading
heading_label = tk.Label(root, text="KHODIYAR HANDLOOM", font=("Helvetica", 18, "bold"))
heading_label.pack(pady=10)

# Create a label to display the QR code
label = tk.Label(root)
label.pack(pady=20)

# Create a label below the QR code to show the UPI ID as a clickable link
link_label = tk.Label(root, text="", fg="blue", cursor="hand2")
link_label.pack(pady=10)

# Automatically generate the QR code for the predefined UPI ID when the program starts
generate_qr_code(upi_id)

# Start the Tkinter event loop
root.mainloop()
