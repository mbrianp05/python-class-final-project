import customtkinter as ctk

from sidebar import Sidebar


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        self.title("Reconocimiento de gestos")
        self.configure_layout()
        self.init_scroll()
        self.init_camera()

    def configure_layout(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

    def init_scroll(self):
        self.sidebar = Sidebar(self)
        self.sidebar.grid(column=0, row=0, sticky="ns")

    def init_camera(self):
        self.camera_frames = ctk.CTkLabel(self, text="")
        self.camera_frames.grid(row=0, column=1, sticky="nswe")

        # self.cap = cv2.VideoCapture(0, cv2.CAP_ANY)
        # time.sleep(0.6)

        # if not self.cap.isOpened():
        #     print("ERROR - Not opened")

        # self.show_frames()

    def show_frames(self):
        # ret, frame = self.cap.read()
        # if ret:
        #     cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #     img = Image.fromarray(cv2image)
        #     self.camera_frames.configure(image=ctk.CTkImage(img, size=(500, 500)))

        # self.camera_frames.after(20, self.show_frames)

        pass

    def on_closing(self):
        # self.cap.release()
        # self.destroy()
        pass


if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
