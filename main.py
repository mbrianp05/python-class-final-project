import customtkinter as ctk
import tksvg


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        self.title("Reconocimiento de gestos")
        self.init_fonts()
        self.configure_layout()
        self.init_scroll()
        self.init_camera()

    def configure_layout(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

    def init_fonts(self):
        self.header_font = ctk.CTkFont(size=22, weight="bold")
        self.bold_font = ctk.CTkFont(weight="bold", size=17)

    def init_scroll(self):
        self.sidebar_panel = ctk.CTkFrame(self, fg_color="transparent", width=200)
        self.sidebar_panel.grid(column=0, row=0, sticky="ns")

        self.header_label = ctk.CTkLabel(
            self.sidebar_panel,
            height=60,
            text="Lista de Gestos",
            font=self.header_font,
            fg_color="transparent",
        )
        self.header_label.grid(row=0, column=0, sticky="we")

        self.sidebar_panel.rowconfigure(1, weight=1)
        self.scrollbar = ctk.CTkScrollableFrame(
            self.sidebar_panel,
            orientation="vertical",
            fg_color="transparent",
        )
        self.scrollbar.grid(row=1, column=0, padx=0, pady=0, sticky="ns")

        # Icono de prueba
        svg = tksvg.SvgImage(file="icons/generic-gesture.svg", scaletoheight=25)

        # Mostrar los gestos disponibles
        # Esto esta forzado aqui de momento en el futuro seria
        # iterar una lista con todos los gestos guardados
        for i in range(10):
            item = ctk.CTkLabel(
                self.scrollbar,
                height=50,
                text="  Gesto " + str(i + 1),
                image=svg,  # type: ignore
                fg_color="transparent",
                corner_radius=50,
                compound="left",
                font=self.bold_font,
            )
            item.grid(row=i, column=0, padx=0, pady=0, sticky="ew")

        # Para crear nuevos gestos
        plus = ctk.CTkButton(
            self.sidebar_panel,
            font=self.bold_font,
            height=30,
            text="+",
            corner_radius=15,
        )
        plus.grid(column=0, row=2, padx=5, sticky="we", pady=5)

    def init_camera(self):
        self.camera_frames = ctk.CTkLabel(self, text="")
        self.camera_frames.grid(row=0, column=1, sticky="nswe")

        # Probar los backends (segundo parametro) - DONE
        # self.cap = cv2.VideoCapture(0, cv2.CAP_ANY)
        # time.sleep(0.6)

        # if not self.cap.isOpened():
        #     print("ERROR - Not opened")

        # self.show_frames()

    def show_frames(self):
        # # Get the latest frame and convert into Image
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


if __name__ == "main":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
