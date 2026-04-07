import time

import customtkinter as ctk
import cv2
from PIL import Image


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("300x300")
        self.title("Reconocimiento de gestos")

        self.init_camera()

    def init_camera(self):
        self.camera_frames = ctk.CTkLabel(self, text="")
        self.camera_frames.grid(row=0, column=0, padx=10, pady=10, sticky="wens")

        # Probar los backends (segundo parametro)
        self.cap = cv2.VideoCapture(0, cv2.CAP_ANY)
        time.sleep(0.6)

        if not self.cap.isOpened():
            print("Not opened")

        self.show_frames()

    def show_frames(self):
        # Get the latest frame and convert into Image
        ret, frame = self.cap.read()
        if ret:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            self.camera_frames.configure(image=ctk.CTkImage(img,size=(200,200)))

        self.camera_frames.after(20, self.show_frames)

    def on_closing(self):
        self.cap.release()
        self.destroy()


app = App()
app.protocol("WM_DELETE_WINDOW", app.on_closing)
app.mainloop()
