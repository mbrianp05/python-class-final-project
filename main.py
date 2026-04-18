import time
import customtkinter as ctk
import cv2
import tksvg
from PIL import Image

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        self.title("Reconocimiento de gestos")
        self.init_camera()
        self.init_scroll()
    
    def init_scroll(self):
        self.scrollbar = ctk.CTkScrollableFrame(self, width=200, height=530, orientation="vertical", label_text="Lista de Gestos")
        self.scrollbar.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        # Icono de prueba
        svg = tksvg.SvgImage(file="icon.svg", scaletoheight=50)

        # Mostrar los gestos disponibles
        for i in range(10):
            item = ctk.CTkButton(self.scrollbar, width=190, height=50, text="Gesto " + str(i+1), image=svg, fg_color="gray", corner_radius=50, compound="left")
            item.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
        # Para crear nuevos gestos
        plus = ctk.CTkButton(self.scrollbar, width=30, height=30, text="+", corner_radius=15)
        plus.grid(column=0, padx=5, pady=5)

    def init_camera(self):
        self.camera_frames = ctk.CTkLabel(self, text="")
        self.camera_frames.grid(row=0, column=1, padx=10, pady=10, sticky="wens")

        # Probar los backends (segundo parametro) - DONE
        self.cap = cv2.VideoCapture(0, cv2.CAP_ANY)
        time.sleep(0.6)

        if not self.cap.isOpened():
            print("ERROR - Not opened")

        self.show_frames()

    def show_frames(self):
        # Get the latest frame and convert into Image
        ret, frame = self.cap.read()
        if ret:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            self.camera_frames.configure(image=ctk.CTkImage(img,size=(500,500)))

        self.camera_frames.after(20, self.show_frames)

    def on_closing(self):
        self.cap.release()
        self.destroy()


app = App()
app.protocol("WM_DELETE_WINDOW", app.on_closing)
app.mainloop()