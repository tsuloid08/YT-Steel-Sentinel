# -*- coding: utf-8 -*-

# --- Imports ---
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import yt_dlp
from ffpyplayer.player import MediaPlayer
import psutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ytss_debug.log'),
        logging.StreamHandler()
    ]
)

# --- Main Application Class ---
class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YT Steel Sentinel (YTSS)")
        self.root.geometry("800x500")
        self.config_file = "config.txt"

        # --- UI Widgets ---
        self.url_label = tk.Label(root, text="URL del Video:")
        self.url_label.pack(pady=5)

        self.url_entry = tk.Entry(root, width=70)
        self.url_entry.pack(pady=5, padx=10)

        self.folder_button = tk.Button(root, text="Seleccionar Carpeta", command=self.select_folder)
        self.folder_button.pack(pady=5)

        self.folder_path_label = tk.Label(root, text="Carpeta no seleccionada")
        self.folder_path_label.pack(pady=5)

        # --- Preview Controls ---
        self.preview_frame = tk.Frame(root)
        self.preview_frame.pack(pady=10)

        self.preview_audio_button = tk.Button(self.preview_frame, text="Escuchar Audio", command=self.start_preview_thread)
        self.preview_audio_button.pack(side=tk.LEFT, padx=5)

        self.play_pause_button = tk.Button(self.preview_frame, text="Reproducir/Pausar", command=self.toggle_play_pause, state=tk.DISABLED)
        self.play_pause_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(self.preview_frame, text="Detener", command=self.stop_preview, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # --- Timeline ---
        self.timeline_frame = tk.Frame(root)
        self.timeline_frame.pack(pady=10, padx=10, fill=tk.X)

        self.time_label_current = tk.Label(self.timeline_frame, text="00:00")
        self.time_label_current.pack(side=tk.LEFT)

        self.timeline_scale = tk.Scale(self.timeline_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                     command=self.on_timeline_change, state=tk.DISABLED)
        self.timeline_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        self.time_label_total = tk.Label(self.timeline_frame, text="00:00")
        self.time_label_total.pack(side=tk.LEFT)

        # --- Download Buttons ---
        self.download_frame = tk.Frame(root)
        self.download_frame.pack(pady=10)

        self.download_video_button = tk.Button(self.download_frame, text="Descargar Video", command=lambda: self.start_download_thread('video'))
        self.download_video_button.pack(side=tk.LEFT, padx=10)

        self.download_audio_button = tk.Button(self.download_frame, text="Descargar Audio", command=lambda: self.start_download_thread('audio'))
        self.download_audio_button.pack(side=tk.LEFT, padx=10)

        self.progress_text = tk.Text(root, height=15, width=80)
        self.progress_text.pack(pady=10, padx=10)

        # --- State Variables ---
        self.download_folder = ""
        self.player = None
        self.audio_duration = 0
        self.is_seeking = False
        self.timeline_update_job = None

        self.load_last_folder()

        self.ram_label = tk.Label(root, text="Uso de RAM: Calculando...")
        self.ram_label.pack(pady=5)
        self.update_ram_usage()

    # --- File Management ---
    def load_last_folder(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    last_folder = f.read().strip()
                    if os.path.isdir(last_folder):
                        self.download_folder = last_folder
                        self.folder_path_label.config(text=self.download_folder)
        except Exception:
            pass

    def save_last_folder(self):
        try:
            with open(self.config_file, 'w') as f:
                f.write(self.download_folder)
        except Exception:
            pass

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.download_folder = folder_selected
            self.folder_path_label.config(text=self.download_folder)
            self.save_last_folder()

    # --- Preview Methods ---
    def start_preview_thread(self):
        logging.info("=== INICIANDO PREVIEW THREAD ===")
        url = self.url_entry.get()
        logging.info(f"URL obtenida: {url}")
        if not url:
            logging.warning("No se proporcionó URL")
            self.root.after(0, lambda: messagebox.showerror("Error", "Por favor, ingresa una URL."))
            return
        
        logging.info("Limpiando texto de progreso y iniciando thread")
        self.root.after(0, lambda: self.progress_text.delete(1.0, tk.END))
        self.root.after(0, lambda: self.progress_text.insert(tk.END, "Obteniendo información del audio para previsualizar...\n"))
        
        preview_thread = threading.Thread(target=self.execute_preview, args=(url,))
        preview_thread.daemon = True
        logging.info("Thread creado, iniciando...")
        preview_thread.start()
        logging.info("Thread iniciado exitosamente")

    def execute_preview(self, url):
        logging.info("=== EJECUTANDO PREVIEW ===")
        try:
            logging.info("Configurando yt-dlp para obtener mejor audio")
            ydl_opts = {'format': 'bestaudio/best'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logging.info("Extrayendo información del video...")
                info = ydl.extract_info(url, download=False)
                audio_url = info['url']
                logging.info(f"URL de audio obtenida: {audio_url[:100]}...")

            logging.info("Deteniendo preview anterior si existe")
            self.stop_preview()

            logging.info("Creando MediaPlayer...")
            self.player = MediaPlayer(audio_url)
            logging.info("MediaPlayer creado exitosamente")
            
            self.audio_duration = info.get('duration', 0)
            logging.info(f"Duración del audio: {self.audio_duration} segundos")
            
            # GUI updates must be thread-safe
            logging.info("Actualizando GUI - habilitando botones")
            self.root.after(0, lambda: self.play_pause_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.timeline_scale.config(state=tk.NORMAL))
            logging.info("Configurando timeline...")
            self.root.after(0, lambda: self.setup_timeline())
            logging.info("Iniciando actualizaciones de timeline...")
            self.root.after(1500, lambda: self.start_timeline_updates())
            self.root.after(0, lambda: self.progress_text.insert(tk.END, "Previsualización lista. Presiona Reproducir/Pausar.\n"))
            logging.info("=== PREVIEW CONFIGURADO EXITOSAMENTE ===")

        except Exception as e:
            logging.error(f"Error en execute_preview: {e}", exc_info=True)
            error_message = f"Ha ocurrido un error inesperado: {e}"
            self.root.after(0, lambda: messagebox.showerror("Error de Previsualización", f"No se pudo obtener el audio: {e}"))
            self.root.after(0, lambda: self.progress_text.insert(tk.END, f"\nError al previsualizar: {e}"))

    def toggle_play_pause(self):
        logging.info("=== TOGGLE PLAY/PAUSE PRESIONADO ===")
        try:
            if self.player:
                logging.info("Player existe, llamando toggle_pause()")
                self.player.toggle_pause()
                logging.info("toggle_pause() ejecutado exitosamente")
            else:
                logging.warning("No hay player disponible para toggle_pause")
        except Exception as e:
            logging.error(f"Error en toggle_play_pause: {e}", exc_info=True)
            self.root.after(0, lambda: messagebox.showerror("Error de Reproducción", f"Error al reproducir/pausar: {e}"))

    def stop_preview(self):
        if self.player:
            self.player.close_player()
            self.player = None
            
            self.root.after(0, lambda: self.play_pause_button.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.timeline_scale.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.stop_timeline_updates())
            self.root.after(0, lambda: self.reset_timeline())
            self.root.after(0, lambda: self.progress_text.insert(tk.END, "Previsualización detenida.\n"))

    # --- Download Methods ---
    def start_download_thread(self, download_type):
        url = self.url_entry.get()
        if not url:
            self.root.after(0, lambda: messagebox.showerror("Error", "Por favor, ingresa una URL."))
            return
        if not self.download_folder:
            self.root.after(0, lambda: messagebox.showerror("Error", "Por favor, selecciona una carpeta de descarga."))
            return

        self.stop_preview()

        self.root.after(0, lambda: self.progress_text.delete(1.0, tk.END))
        self.root.after(0, lambda: self.progress_text.insert(tk.END, f"Iniciando descarga de {download_type}...\n"))
        
        download_thread = threading.Thread(target=self.execute_download, args=(url, download_type))
        download_thread.daemon = True
        download_thread.start()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            line = d['_default_template']
            self.root.after(0, lambda: self.progress_text.insert(tk.END, line + '\r'))
            self.root.after(0, lambda: self.progress_text.see(tk.END))
        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.progress_text.insert(tk.END, "\nDescarga finalizada, procesando...\n"))
            self.root.after(0, lambda: self.progress_text.see(tk.END))

    def execute_download(self, url, download_type):
        try:
            output_template = os.path.join(self.download_folder, '%(title)s.%(ext)s')

            if download_type == 'video':
                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',  # Queremos el mejor video y audio.
                    'outtmpl': output_template,  # Dónde guardarlo.
                    'progress_hooks': [self.progress_hook],  # Para ver el progreso.
                    'noprogress': True, # No queremos que yt-dlp muestre su propia barra de progreso.
                }
            else:  # audio
                ydl_opts = {
                    'format': 'bestaudio/best',  # Queremos la mejor calidad de música.
                    'outtmpl': output_template,  # Dónde guardarla.
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',  # Para sacar solo la música.
                        'preferredcodec': 'mp3',  # Para que sea un archivo MP3.
                        'preferredquality': '192',  # Con buena calidad.
                    }],
                    'progress_hooks': [self.progress_hook],  # Para ver el progreso.
                    'noprogress': True, # No queremos que yt-dlp muestre su propia barra de progreso.
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
            # Guardamos el mensaje de error.
            # Mensajes de error seguros para la GUI
            self.root.after(0, lambda: messagebox.showerror("Error", error_message))
            self.root.after(0, lambda: self.progress_text.insert(tk.END, f"\nError: {e}"))

    # --- Timeline Methods ---
    def setup_timeline(self):
        logging.info(f"Configurando timeline con duración: {self.audio_duration}")
        try:
            if self.audio_duration > 0:
                self.timeline_scale.config(to=self.audio_duration)
                total_time = self.format_time(self.audio_duration)
                self.time_label_total.config(text=total_time)
                logging.info(f"Timeline configurado: 0 a {self.audio_duration}, tiempo total: {total_time}")
            else:
                self.timeline_scale.config(to=100)
                self.time_label_total.config(text="--:--")
                logging.info("Timeline configurado con duración desconocida (0-100)")
        except Exception as e:
            logging.error(f"Error en setup_timeline: {e}", exc_info=True)

    def start_timeline_updates(self):
        logging.info("=== INICIANDO ACTUALIZACIONES DE TIMELINE ===")
        self.update_timeline()

    def update_timeline(self):
        logging.debug("update_timeline() llamado")
        try:
            if self.player and not self.is_seeking:
                logging.debug("Player existe y no estamos seeking, obteniendo tiempo actual...")
                try:
                    if hasattr(self.player, 'get_pts'):
                        current_time = self.player.get_pts()
                        logging.debug(f"Tiempo actual obtenido: {current_time}")
                        
                        if current_time is not None and isinstance(current_time, (int, float)) and current_time >= 0:
                            logging.debug(f"Actualizando timeline a posición: {current_time}")
                            self.root.after(0, lambda t=current_time: self._update_timeline_gui(t))
                        else:
                            logging.debug(f"Tiempo inválido recibido: {current_time}")
                    else:
                        logging.warning("Player no tiene método get_pts disponible")
                except Exception as e:
                    logging.error(f"Error al obtener tiempo del player: {e}", exc_info=True)
            else:
                if not self.player:
                    logging.debug("No hay player disponible para actualizar timeline")
                if self.is_seeking:
                    logging.debug("Saltando actualización porque estamos seeking")
            
            if self.player:
                logging.debug("Programando próxima actualización de timeline en 1000ms")
                self.timeline_update_job = self.root.after(1000, self.update_timeline)
            else:
                logging.debug("No hay player, no programando próxima actualización")
        except Exception as e:
            logging.error(f"Error crítico en update_timeline: {e}", exc_info=True)
            if self.player:
                self.timeline_update_job = self.root.after(2000, self.update_timeline)

    def _update_timeline_gui(self, current_time):
        try:
            self.timeline_scale.set(current_time)
            formatted_time = self.format_time(current_time)
            self.time_label_current.config(text=formatted_time)
            logging.debug(f"Timeline actualizado exitosamente: {formatted_time}")
        except Exception as e:
            logging.error(f"Error al actualizar GUI del timeline: {e}", exc_info=True)

    def stop_timeline_updates(self):
        if self.timeline_update_job:
            self.root.after_cancel(self.timeline_update_job)
            self.timeline_update_job = None

    def reset_timeline(self):
        self.timeline_scale.set(0)
        self.time_label_current.config(text="00:00")
        self.time_label_total.config(text="00:00")

    def on_timeline_change(self, value):
        if self.player:
            self.is_seeking = True
            try:
                seek_time = float(value)
                logging.debug(f"Seeking a posición: {seek_time}")
                
                if 0 <= seek_time <= self.audio_duration:
                    self.player.seek(seek_time)
                    formatted_time = self.format_time(seek_time)
                    self.time_label_current.config(text=formatted_time)
                    logging.debug(f"Seek exitoso a: {formatted_time}")
                else:
                    logging.warning(f"Tiempo de seek fuera de rango: {seek_time}")
            except Exception as e:
                logging.error(f"Error en seek: {e}", exc_info=True)
            finally:
                self.root.after(1500, lambda: setattr(self, 'is_seeking', False))

    def format_time(self, seconds):
        if seconds is None or seconds < 0:
            return "00:00"
        
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def update_ram_usage(self):
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        ram_usage_mb = mem_info.rss / (1024 * 1024)
        self.ram_label.config(text=f"Uso de RAM: {ram_usage_mb:.2f} MB")
        self.root.after(2000, self.update_ram_usage)

# --- Entry Point ---
if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    
    # Ensure player is closed on window close
    def on_closing():
        app.stop_preview()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
