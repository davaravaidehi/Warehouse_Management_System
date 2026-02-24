import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import time
from login import page  # Import the login page function

# Function to handle GIF animation
def animate_gif(label, gif_frames, delay, index=0):
    frame = gif_frames[index]
    label.config(image=frame)
    index = (index + 1) % len(gif_frames)
    label.after(delay, animate_gif, label, gif_frames, delay, index)

def create_splash_screen(gif_path):
    # Create the main Tkinter window
    root = tk.Tk()
    root.overrideredirect(True)  # Remove window decorations
    root.geometry("400x400+430+130")  # Adjust to your desired splash screen size

    # Load the GIF using Pillow
    gif = Image.open(gif_path)
    gif_frames = [ImageTk.PhotoImage(frame.copy().convert("RGBA")) for frame in ImageSequence.Iterator(gif)]
    delay = gif.info['duration']  # Duration between frames in ms

    # Add a Label widget to display the GIF
    label = tk.Label(root, bg="black")
    label.pack(expand=True, fill="both")

    # Start the GIF animation
    animate_gif(label, gif_frames, delay)

    # Close splash screen after a specific duration (e.g., 5 seconds)
    def close_splash_and_open_login():
        root.destroy()  # Close the splash screen
        page()  # Open the login screen

    root.after(5000, close_splash_and_open_login)

    root.mainloop()

# Path to the uploaded GIF
gif_path = "F:/Warehouse_Management_System/image/kk.gif"

create_splash_screen(gif_path)
