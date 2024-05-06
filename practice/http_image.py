import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO

# Function to load and display the image
def load_and_display_image(url, container):
    try:
        # Get the image from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise exception if there is an error

        # Create a PIL image from the image data
        image_data = BytesIO(response.content)
        pil_image = Image.open(image_data)

        # 이미지의 크기를 조절합니다.
        pil_image.thumbnail((200, 200))

        # Convert the PIL image to a format that Tkinter can use
        tk_image = ImageTk.PhotoImage(pil_image)

       

        # Create a bordered frame for the image
        border_frame = ttk.Frame(container, borderwidth=2, relief="groove")
        border_frame.pack(fill='x', padx=10, pady=(10, 0))

        # Create a Tkinter label widget inside the border frame and set the image
        image_label = ttk.Label(border_frame, image=tk_image)
        image_label.image = tk_image  # Keep a reference to prevent garbage collection
        image_label.pack(fill='x')

        container.update_idletasks()  # Update the container's information
        width = border_frame.winfo_width()

        text_frame = ttk.Frame(container, borderwidth=2, relief="groove")
        text_frame.pack(fill='x', padx=10, pady=0)

        # Create a label widget for the text below the image
        text_label = ttk.Label(text_frame, text="Your text here\nasdasd\nadasd\n", width=width)
        text_label.pack(fill='x')

    except requests.RequestException as e:
        print(f"Error loading image: {e}")

# Main window creation
root = tk.Tk()
root.title("DeviceMart Product Image")

# Container frame for loading the image
image_frame = ttk.Frame(root)
image_frame.pack()

# Image URL
image_url = "https://www.devicemart.co.kr/data/collect_img/kind_0/goods/large/200802281050350.jpg"

# Load and display the image
load_and_display_image(image_url, image_frame)

# Run the window
root.mainloop()