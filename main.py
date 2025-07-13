import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YT Steel Sentinel (YTSS)")
        self.root.geometry("700x500")
        self.config_file = "config.txt"

        self.url_label = tk.Label(root, text="URL del Video:")
        self.url_label.pack(pady=5)

        self.url_entry = tk.Entry(root, width=70)
        self.url_entry.pack(pady=5, padx=10)

        self.folder_button = tk.Button(root, text="Seleccionar Carpeta", command=self.select_folder)
        self.folder_button.pack(pady=5)

        self.folder_path_label = tk.Label(root, text="Carpeta no seleccionada")
        self.folder_path_label.pack(pady=5)

        self.download_button = tk.Button(root, text="Descargar", command=self.start_download_thread)
        self.download_button.pack(pady=20)

        self.progress_text = tk.Text(root, height=15, width=80)
        self.progress_text.pack(pady=10, padx=10)

        self.download_folder = ""
        self.load_last_folder()

    def load_last_folder(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    last_folder = f.read().strip()
                    if os.path.isdir(last_folder):
                        self.download_folder = last_folder
                        self.folder_path_label.config(text=self.download_folder)
        except Exception as e:
            # Silenciosamente ignorar errores de carga, la app puede continuar
            pass

    def save_last_folder(self):
        try:
            with open(self.config_file, 'w') as f:
                f.write(self.download_folder)
        except Exception as e:
            # No es crítico si falla el guardado
            pass

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.download_folder = folder_selected
            self.folder_path_label.config(text=self.download_folder)
            self.save_last_folder()

    def start_download_thread(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Por favor, ingresa una URL.")
            return
        if not self.download_folder:
            messagebox.showerror("Error", "Por favor, selecciona una carpeta de descarga.")
            return

        # Inicia la descarga en un hilo separado para no bloquear la GUI
        download_thread = threading.Thread(target=self.download_video, args=(url,))
        download_thread.start()

    def download_video(self, url):
        self.progress_text.delete(1.0, tk.END)
        self.progress_text.insert(tk.END, "Iniciando descarga...\n")
        self.root.update_idletasks()

        try:
            output_template = os.path.join(self.download_folder, '%(title)s.%(ext)s')
            
            # Comando para yt-dlp
            command = [
                'yt-dlp',
                '--no-mtime',
                '-o', output_template,
                url
            ]

            # Inicia el proceso
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)

            # Lee la salida en tiempo real
            for output in iter(process.stdout.readline, ''):
                self.progress_text.insert(tk.END, output)
                self.progress_text.see(tk.END)
                self.root.update_idletasks()

            process.wait()

            # Verifica si hubo errores
            if process.returncode != 0:
                messagebox.showerror("Error", "La descarga falló. Revisa la ventana de progreso para más detalles.")
            else:
                self.progress_text.insert(tk.END, "\n\nDescarga completada exitosamente!")
                messagebox.showinfo("Éxito", "El video se ha descargado correctamente.")

        except FileNotFoundError:
            messagebox.showerror("Error", "yt-dlp no encontrado. Asegúrate de que esté instalado y en el PATH del sistema.")
            self.progress_text.insert(tk.END, "\nError: yt-dlp no encontrado.")
        except Exception as e:
            messagebox.showerror("Error", f"Ha ocurrido un error inesperado: {e}")
            self.progress_text.insert(tk.END, f"\nError inesperado: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()