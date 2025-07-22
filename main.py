# -*- coding: utf-8 -*-

# Importaciones necesarias para la aplicación
import tkinter as tk  # Para la interfaz gráfica (GUI)
from tkinter import filedialog, messagebox  # Widgets específicos de Tkinter para diálogos
import threading  # Para ejecutar la descarga en un hilo separado y no bloquear la GUI
import os  # Para interactuar con el sistema operativo (rutas de archivos)
import sys  # Para interactuar con el intérprete de Python
import yt_dlp  # La biblioteca para descargar videos de YouTube

# --- Clase Principal de la Aplicación ---
class DownloaderApp:
    """Define la estructura y comportamiento de la aplicación de descarga."""

    def __init__(self, root):
        """Inicializa la ventana principal y todos sus componentes (widgets)."""
        self.root = root
        self.root.title("YT Steel Sentinel (YTSS)")  # Título de la ventana
        self.root.geometry("700x500")  # Dimensiones iniciales de la ventana
        self.config_file = "config.txt"  # Archivo para guardar la última carpeta usada

        # --- Creación de Widgets de la Interfaz ---

        # Etiqueta para el campo de la URL
        self.url_label = tk.Label(root, text="URL del Video:")
        # Creamos una etiqueta que dice "URL del Video:". Es como un cartelito.
        # 'tk.Label' es la herramienta para hacer etiquetas.
        # 'root' es dónde la ponemos (en nuestra ventana principal).
        # 'text' es lo que dice el cartelito.

        self.url_label.pack(pady=5)
        # Ponemos el cartelito en la ventana. 'pack' es como decir "ponlo aquí".
        # 'pady=5' significa que deje un pequeño espacio arriba y abajo, como un cojín.

        self.url_entry = tk.Entry(root, width=70)
        # Creamos un espacio para que puedas escribir la dirección del video de YouTube.
        # 'tk.Entry' es la herramienta para hacer espacios de escritura.
        # 'width=70' significa que sea lo suficientemente largo para escribir.

        self.url_entry.pack(pady=5, padx=10)
        # Ponemos el espacio de escritura en la ventana.
        # 'padx=10' significa que deje un pequeño espacio a los lados.

        self.folder_button = tk.Button(root, text="Seleccionar Carpeta", command=self.select_folder)
        # Creamos un botón que dice "Seleccionar Carpeta".
        # 'tk.Button' es la herramienta para hacer botones.
        # 'command=self.select_folder' significa que cuando lo presiones, haga la magia de 'select_folder'.

        self.folder_button.pack(pady=5)
        # Ponemos el botón en la ventana.

        self.folder_path_label = tk.Label(root, text="Carpeta no seleccionada")
        # Creamos otra etiqueta para mostrar qué carpeta elegiste.

        self.folder_path_label.pack(pady=5)

        # Frame (contenedor) para agrupar los botones de descarga
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        # Botón para descargar el video
        self.download_video_button = tk.Button(self.button_frame, text="Descargar Video", command=lambda: self.start_download_thread('video'))
        self.download_video_button.pack(side=tk.LEFT, padx=10)

        # Botón para descargar solo el audio
        self.download_audio_button = tk.Button(self.button_frame, text="Descargar Audio", command=lambda: self.start_download_thread('audio'))
        self.download_audio_button.pack(side=tk.LEFT, padx=10)

        # Área de texto para mostrar el progreso de la descarga
        self.progress_text = tk.Text(root, height=15, width=80)
        # Este es como un cuaderno grande donde el programa escribe lo que está haciendo.
        self.progress_text.pack(pady=10, padx=10);

        # --- Inicialización de Variables y Estado ---

        self.download_folder = ""  # Variable para almacenar la ruta de descarga
        self.load_last_folder()  # Carga la última carpeta usada desde el archivo de config

    # --- Métodos para Manejo de Archivos y Carpetas ---

    def load_last_folder(self):
        """Carga la ruta de la última carpeta de descarga desde config.txt."""
        try:
            # 'try' es como decir "intenta hacer esto, y si no puedes, no te preocupes".
            if os.path.exists(self.config_file):
                # 'os.path.exists' es como preguntar "¿Existe este papelito?"
                with open(self.config_file, 'r') as f:
                    # 'open' es como abrir el papelito. 'r' significa que solo lo vamos a leer.
                    # 'as f' es como darle un nombre corto al papelito mientras lo usamos.
                    last_folder = f.read().strip()
                    if os.path.isdir(last_folder):  # Verifica si la carpeta aún existe
                        self.download_folder = last_folder
                        # Si es una carpeta de verdad, la recordamos.
                        self.folder_path_label.config(text=self.download_folder)
        except Exception as e:
            # Si hay un error (ej. archivo corrupto), simplemente no carga la ruta
            pass
            # 'pass' significa "no hagas nada".

    def save_last_folder(self):
        """Guarda la ruta de la carpeta de descarga actual en config.txt."""
        try:
            with open(self.config_file, 'w') as f:
                # 'w' significa que vamos a escribir en el papelito (y si no existe, lo crea).
                f.write(self.download_folder)
        except Exception as e:
            # Si no se puede guardar, no es un error crítico
            pass

    def select_folder(self):
        """Abre un diálogo para que el usuario seleccione una carpeta de descarga."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:  # Si el usuario selecciona una carpeta y no cancela
            self.download_folder = folder_selected
            # Recordamos la carpeta que elegiste.
            self.folder_path_label.config(text=self.download_folder)
            # Actualizamos el cartelito de la carpeta.
            self.save_last_folder()

    # --- Métodos para la Lógica de Descarga ---

    def start_download_thread(self, download_type):
        """Inicia el proceso de descarga en un hilo separado para no congelar la GUI."""
        url = self.url_entry.get()
        # Validaciones previas a la descarga
        if not url:
            messagebox.showerror("Error", "Por favor, ingresa una URL.")
            return
        if not self.download_folder:
            messagebox.showerror("Error", "Por favor, selecciona una carpeta de descarga.")
            return

        # Crea y comienza el hilo de descarga
        download_thread = threading.Thread(target=self.execute_download, args=(url, download_type))
        download_thread.start()

    def progress_hook(self, d):
        """Función que yt-dlp llama para reportar el progreso."""
        if d['status'] == 'downloading':
            # Extrae la línea de progreso formateada por yt-dlp
            line = d['_default_template']
            # Actualiza el área de texto en el hilo principal de la GUI
            self.progress_text.insert(tk.END, line + '\r')
            self.progress_text.see(tk.END)
            self.root.update_idletasks()
        elif d['status'] == 'finished':
            self.progress_text.insert(tk.END, "\nDescarga finalizada, procesando...\n")
            self.progress_text.see(tk.END)
            self.root.update_idletasks()

    def execute_download(self, url, download_type):
        """Configura y ejecuta la descarga usando la biblioteca yt-dlp."""
        self.progress_text.delete(1.0, tk.END)  # Limpia el área de progreso
        self.progress_text.insert(tk.END, f"Iniciando descarga de {download_type}...\n")
        self.root.update_idletasks()

        try:
            # Define la plantilla para el nombre del archivo de salida
            output_template = os.path.join(self.download_folder, '%(title)s.%(ext)s')
            # Le decimos dónde guardar el archivo y cómo llamarlo.

            if download_type == 'video':
                # Si queremos descargar el video...
                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',  # Mejor video y audio, requiere ffmpeg
                    'outtmpl': output_template,  # Dónde guardar y cómo nombrar el archivo
                    'progress_hooks': [self.progress_hook],  # Función para el progreso
                    'noprogress': True, # Desactiva la barra de progreso de yt-dlp
                }
            else:  # audio
                # Si queremos descargar solo la música...
                ydl_opts = {
                    'format': 'bestaudio/best',  # Queremos la mejor calidad de música.
                    'outtmpl': output_template,  # Dónde guardarla.
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',  # Para sacar solo la música.
                        'preferredcodec': 'mp3',  # Para que sea un archivo MP3.
                        'preferredquality': '192',  # Con buena calidad.
                    }],
                    'progress_hooks': [self.progress_hook],
                    'noprogress': True, # Desactiva la barra de progreso de yt-dlp
                }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Le damos las instrucciones al detective de YouTube.
                ydl.download([url])
                # ¡Y el detective descarga la música o el video!
            
            # Mensajes de éxito seguros para la GUI
            self.root.after(0, lambda: self.progress_text.insert(tk.END, f"\n\nDescarga de {download_type} completada exitosamente!"))
            self.root.after(0, lambda: messagebox.showinfo("Éxito", f"El {download_type} se ha descargado correctamente."))
        except Exception as e:
            # Si algo sale mal al descargar...
            error_message = f"Ha ocurrido un error inesperado: {e}"
            messagebox.showerror("Error", error_message)
            self.progress_text.insert(tk.END, f"\nError: {e}")

# --- Punto de Entrada de la Aplicación ---
if __name__ == "__main__":
    """Este bloque se ejecuta solo si el script es el archivo principal."""
    root = tk.Tk()  # Crea la ventana principal
    app = DownloaderApp(root)  # Crea una instancia de nuestra aplicación
    root.mainloop()  # Inicia el bucle de eventos de la GUI (la mantiene abierta)

