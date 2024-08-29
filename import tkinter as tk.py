import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import numpy as np

class ThermalCameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interfaz Táctil - Cámara Térmica")
        self.root.geometry("380x180")  # Tamaño de la ventana según especificación
        
        # Inicializar el mapa de colores por defecto
        self.color_map = "JET"
        
        self.createWidgets()

        # Vincular el evento de cierre de la ventana al método de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def createWidgets(self):
        # Crear marco principal
        self.mainFrame = tk.Frame(self.root, bg="white")
        self.mainFrame.pack(fill="both", expand=True)

        # Configurar las columnas del grid en el Frame principal con proporciones absolutas
        self.mainFrame.grid_columnconfigure(0, weight=1)  # Columna izquierda
        self.mainFrame.grid_columnconfigure(1, weight=12)  # Columna central
        self.mainFrame.grid_columnconfigure(2, weight=3)  # Columna derecha
        self.mainFrame.grid_rowconfigure(0, weight=1)     # Fila única

        # Crear marcos de segundo nivel
        self.optionsFrame = tk.Frame(self.mainFrame)  # Marco de opciones
        self.cameraFrame = tk.Frame(self.mainFrame)    # Marco para visualizar video la Cámara
        self.parametersFrame = tk.Frame(self.mainFrame)  # Crear marco de parámetros

        # Colocando los marcos en el grid con proporciones relativas
        self.optionsFrame.grid(row=0, column=0, sticky="nsew")
        self.cameraFrame.grid(row=0, column=1, sticky="nsew")
        self.parametersFrame.grid(row=0, column=2, sticky="nsew")

        # Crear marco Captura de Frames
        self.captureFrame = tk.Frame(self.optionsFrame)
        self.shutdownFrame = tk.Frame(self.optionsFrame)

        # Configurar las filas del grid en el Frame opciones
        self.optionsFrame.grid_rowconfigure(0, weight=1)  # Fila Superior
        self.optionsFrame.grid_rowconfigure(1, weight=1)  # Fila Inferior
        self.optionsFrame.grid_columnconfigure(0, weight=1)

        # Colocando los marcos en el grid
        self.shutdownFrame.grid(row=0, column=0, sticky="nsew")
        self.captureFrame.grid(row=1, column=0, sticky="nsew")

        # Creando el botón de apagado con tamaño relativo
        self.shutdownButton = tk.Button(self.shutdownFrame, text="OFF")
        self.shutdownButton.place(relx=0, rely=0, relwidth=0.5, relheight=0.5)  # Botón ocupa 50% del ancho y 50% del alto del shutdownFrame

        # Creando los botones de captura de frames
        self.recordButton = tk.Button(self.captureFrame, text="Record")
        self.shotButton = tk.Button(self.captureFrame, text="Shot")

        # Crear un marco contenedor para los botones en el captureFrame
        self.buttonFrame = tk.Frame(self.captureFrame)
        self.buttonFrame.pack(fill="both", expand=True)

        self.recordButton.pack(side="top", fill="both", expand=True)
        self.shotButton.pack(side="bottom", fill="both", expand=True)

        # Label para mostrar las imágenes de la cámara térmica
        self.video_label = tk.Label(self.cameraFrame)
        self.video_label.place(relx=0, rely=0, relwidth=1, relheight=1)  # Utilizar place para evitar que el Label cambie el tamaño del Frame

        # Crear un menú desplegable para seleccionar el mapa de colores con tamaño fijo
        self.color_map_var = tk.StringVar(value="JET")
        self.color_map_menu = ttk.OptionMenu(
            self.optionsFrame, 
            self.color_map_var, 
            "JET", 
            "JET", 
            "HOT", 
            "COOL", 
            "PLASMA", 
            "TURBO", 
            "GRAYS", 
            "ORIGINAL", 
            command=self.change_color_map
        )
        self.color_map_menu.config(width=1)  # Establecer un ancho fijo para el OptionMenu
        self.color_map_menu.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        # Inicializar la captura de video
        self.cap = cv2.VideoCapture(0)  # Asegúrate de que el índice 0 es correcto para tu cámara térmica

        # Comenzar la actualización del frame
        self.update_frame()

    def update_frame(self):
        # Captura el frame de la cámara térmica
        ret, frame = self.cap.read()
        
        if ret:
            # Obtener la mitad inferior de la imagen
            height, width = frame.shape[:2]
            frame = frame[height // 2:, :]  # Tomar la mitad inferior de la imagen

            if self.color_map == "ORIGINAL":
                # Mostrar la imagen original
                color_mapped_frame = frame
            elif self.color_map == "GRAYS":
                # Convertir la imagen a escala de grises
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                color_mapped_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB)
            else:
                # Aplicar el mapa de colores seleccionado a la imagen en escala de grises
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                color_map_dict = {
                    "JET": cv2.COLORMAP_JET,
                    "HOT": cv2.COLORMAP_HOT,
                    "COOL": cv2.COLORMAP_COOL,
                    "PLASMA": cv2.COLORMAP_PLASMA,
                    "TURBO": cv2.COLORMAP_TURBO
                }
                color_map = color_map_dict.get(self.color_map, cv2.COLORMAP_JET)
                color_mapped_frame = cv2.applyColorMap(gray_frame, color_map)

            # Convertir la imagen de OpenCV a un formato que tkinter pueda usar
            cv_image = cv2.cvtColor(color_mapped_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv_image)

            # Redimensionar la imagen al tamaño del Label
            label_width = self.video_label.winfo_width()
            label_height = self.video_label.winfo_height()
            if label_width > 0 and label_height > 0:  # Evitar redimensionar a 0x0
                img = img.resize((label_width, label_height), Image.ANTIALIAS)

            imgtk = ImageTk.PhotoImage(image=img)
            
            # Mostrar la imagen en el label de tkinter
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        
        # Actualiza el frame cada 10 ms
        self.root.after(10, self.update_frame)

    def change_color_map(self, selected_map):
        # Cambiar el mapa de colores basado en la selección del usuario
        self.color_map = selected_map
        print(f"Color map changed to: {self.color_map}")

    def on_closing(self):
        # Liberar el recurso de la cámara
        self.cap.release()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = ThermalCameraApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
