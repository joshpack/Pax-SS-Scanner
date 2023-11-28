import os
import shutil
import tkinter as tk
import requests
import unicodedata
import pyperclip
from tkinter import messagebox
from datetime import datetime
from PIL import Image, ImageTk
from dotenv import load_dotenv

load_dotenv()

class FileScannerApp:
    def __init__(self, source_directory, destination_directory, local_directory, imgur_client_id):
        self.source_directory = source_directory
        self.upload_directory = destination_directory
        self.local_directory = local_directory
        self.imgur_client_id = imgur_client_id
        self.uploaded = False
        self.saved = False
        self.root = tk.Tk()
        self.root.title("Pax SS Scanner")

        # Hide the main window
        self.root.withdraw()
        self.check_for_new_files()
        self.root.mainloop()

    def check_for_new_files(self):
        files = os.listdir(self.source_directory)

        for file in files:
            file_path = os.path.join(self.source_directory, file)

            if os.path.isfile(file_path):
                self.process_file(file_path)

        self.root.after(1000, self.check_for_new_files)

    def process_file(self, file_path):
        if not os.path.basename(file_path).startswith(".DS"):
            self.display_image(file_path)
                

    def msg_upload(self, file_path):
        answer = messagebox.askyesno("Upload File", f"Do you want to upload\n\n {os.path.basename(file_path)}\n\n to Imgur?")
        return answer
    
    def msg_save(self):
        answer = messagebox.askyesno("Save File", f"After the file is uploaded, do you want to save it as well?")
        return answer
    
    def upload_to_imgur(self, file_path):
        print(f"file_path: {file_path}")
        normalized_path = unicodedata.normalize("NFKD", file_path).encode("ASCII", "ignore").decode("utf-8")
        print(f"normalized_path: {normalized_path}")

        imgur_api_url = "https://api.imgur.com/3/upload"
        headers = {"Authorization": f"Client-ID {self.imgur_client_id}"}

        with open(file_path, "rb") as file:
            files = {"image": file}
            # send to imgur
            response = requests.post(imgur_api_url, headers=headers, files=files)

            if response.status_code == 200:
                self.uploaded = True
                imgur_url = response.json()["data"]["link"]
                print(f"Successful upload to Imgur: {imgur_url}")
                pyperclip.copy(imgur_url)
                return imgur_url
            else:
                self.uploaded = False
                print(f"Error uploading to Imgur")
                response.raise_for_status()

    def display_image(self, file_path):
        image = Image.open(file_path)

        tk_image = ImageTk.PhotoImage(image)

        image_window = tk.Toplevel(self.root)
        image_window.title("Image Preview")

        label = tk.Label(image_window, image=tk_image)
        label.photo = tk_image  # Keep a reference to the image to prevent it from being garbage collected
        label.pack()

        screen_width = image_window.winfo_screenwidth()
        screen_height = image_window.winfo_screenheight()

        window_width = image.width
        window_height = image.height + 80  # Increased to create room for the yes/no buttons

        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2 - 300 # Decreased to move the window up a bit

        image_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        question_label = tk.Label(image_window, text="Do you want to upload this image to Imgur?")
        question_label.pack()
        response_var = tk.IntVar()

        def upload_and_close():
            response_var.set(1)
            self.move_file_upload(file_path)
            image_window.destroy()

        def close_and_continue():
            response_var.set(0)
            self.move_file_save(file_path)
            image_window.destroy()

        image_window.after(10000, close_and_continue)

        yes_button = tk.Button(image_window, text="Yes", command=upload_and_close)
        yes_button.pack(padx=10)

        no_button = tk.Button(image_window, text="No", command=close_and_continue)
        no_button.pack(padx=10)
        image_window.wait_variable(response_var)

    def upload_confirmation(self):
        def close_ok_window():
            conf.destroy()

        conf = tk.Toplevel(self.root)
        conf.title("Upload Successful!")
        screen_width = conf.winfo_screenwidth()
        screen_height = conf.winfo_screenheight()

        window_width = 300
        window_height = 50

        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        conf.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        conf.after(5000, conf.destroy)
        
        Label = tk.Label(conf,text="Upload to Imgur successful.")
        Label.pack()
        ok_button = tk.Button(conf, text="Ok", command=close_ok_window)
        ok_button.pack(padx=10)

        

    def move_file_upload(self, file_path):
        current_year = datetime.now().year
        year_directory = os.path.join(self.upload_directory, str(current_year))

        if not os.path.exists(year_directory):
            os.makedirs(year_directory)

        current_month = datetime.now().strftime("%B")
        month_directory = os.path.join(year_directory, current_month)

        if not os.path.exists(month_directory):
            os.makedirs(month_directory)


        try:
            self.upload_to_imgur(file_path)
            shutil.move(file_path, os.path.join(month_directory, f"{os.path.basename(file_path)}"))            
            print(f"File uploaded & saved successfully: {os.path.basename(file_path)}")
            try:
                self.upload_confirmation()
            except Exception as b:
                print(f"error showing confirmation window: {b}")
        except Exception as e:
            print(f"error uploading or saving file: {e}")

    def move_file_save(self, file_path):
        current_year = datetime.now().year
        year_directory = os.path.join(self.local_directory, str(current_year))

        if not os.path.exists(year_directory):
            os.makedirs(year_directory)

        current_month = datetime.now().strftime("%B")
        month_directory = os.path.join(year_directory, current_month)

        if not os.path.exists(month_directory):
            os.makedirs(month_directory)

        try:
            shutil.move(file_path, os.path.join(month_directory, os.path.basename(file_path)))
            print(f"File saved but not uploaded. {os.path.basename(file_path)}")
        except:
            print("")


if __name__ == "__main__":
    # pulling from .env file
    source_directory = os.getenv('MONITOR_DIRECTORY')
    upload_directory = os.getenv('UPLOAD_DIRECTORY')
    local_directory = os.getenv('SAVE_DIRECTORY')

    imgur_client_id = os.getenv('IMGUR_CLIENT_ID')

    if not os.path.exists(source_directory):
        print("Source directory does not exist.")
    elif not os.path.exists(upload_directory):
        print("upload directory does not exist.")
    else:
        app = FileScannerApp(source_directory, upload_directory, local_directory, imgur_client_id)