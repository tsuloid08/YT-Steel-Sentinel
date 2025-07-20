# -*- coding: utf-8 -*-

# ¡Hola, pequeño programador!
# Este es un programa de computadora que te ayuda a escuchar canciones de YouTube.
# Es como una caja mágica que puede buscar la música y hacer que suene en tu computadora.

# --- Las Herramientas Mágicas (Importaciones) ---
# Para construir nuestra caja mágica, necesitamos algunas herramientas especiales.
# Imagina que son como los juguetes que sacas de tu caja de juguetes para jugar.

import tkinter as tk  # Esta es nuestra caja de juguetes principal para hacer ventanas y botones bonitos.
# 'tk' es como el nombre corto de la caja de juguetes, para no escribir 'tkinter' todo el tiempo.

from tkinter import filedialog, messagebox  # Estas son herramientas especiales de la caja de juguetes 'tkinter'.
# 'filedialog' es como una varita mágica para abrir una ventana y elegir dónde guardar cosas.
# 'messagebox' es como un cartelito que aparece para decirte cosas importantes o si algo salió mal.

import threading  # Esta herramienta es para hacer muchas cosas a la vez.
# Imagina que tienes dos manos: una para dibujar y otra para comer un dulce.
# 'threading' permite que la computadora haga dos cosas al mismo tiempo, como escuchar música y dibujar la ventana.

import os  # Esta herramienta nos ayuda a hablar con la computadora.
# Es como si le preguntaras a la computadora: "¿Dónde está mi carpeta de música?" o "Guarda esto aquí".

import yt_dlp  # ¡Esta es la herramienta más mágica! Es como un detective de YouTube.
# Le dices el nombre de un video de YouTube y él encuentra la música o el video para ti.

from ffpyplayer.player import MediaPlayer # Esta es la herramienta para que la música suene.
# Es como un reproductor de música de verdad, pero dentro de nuestro programa.

import psutil # Esta herramienta nos ayuda a obtener información del sistema, como el uso de RAM.
import logging # Esta herramienta nos ayuda a escribir mensajes de depuración para encontrar problemas.
import tempfile # Esta herramienta nos ayuda a crear archivos temporales para la previsualización.

# Configurar el sistema de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ytss_debug.log'),
        logging.StreamHandler()
    ]
)


# --- La Caja de Juguetes Principal (Clase DownloaderApp) ---
# Una 'clase' es como una gran caja de juguetes donde guardamos todas las instrucciones para hacer algo.
# Nuestra 'DownloaderApp' es la caja de juguetes para hacer nuestra aplicación de descarga.

class DownloaderApp:
    # Esto es como el nombre de nuestra caja de juguetes.

    def __init__(self, root):
        # Esta es la primera instrucción que se ejecuta cuando abrimos la caja de juguetes.
        # 'self' es como decir "yo mismo" o "esta caja de juguetes".
        # 'root' es como el lienzo grande donde vamos a dibujar nuestra ventana.

        self.root = root
        # Le decimos a nuestra caja de juguetes que el lienzo grande es 'root'.

        self.root.title("YT Steel Sentinel (YTSS)")
        # Le ponemos un nombre a nuestra ventana, como "Mi Reproductor de Música".

        self.root.geometry("800x500")
        # Le decimos a la ventana qué tan grande debe ser, como un dibujo de 700 pasos de ancho y 500 pasos de alto.

        self.config_file = "config.txt"
        # Este es como un papelito donde anotamos la última carpeta que usamos, para recordarla.

        # --- Dibujando la Ventana (Creación de Widgets) ---
        # Ahora vamos a poner los botones y los espacios para escribir en nuestra ventana.
        # Cada botón o espacio es como un juguete diferente que sacamos de la caja.

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
        # Ponemos la etiqueta en la ventana.

        # --- Botones para Escuchar y Descargar ---
        # Estos son los botones para hacer la magia de la música.

        self.preview_frame = tk.Frame(root)
        # Creamos una pequeña caja invisible para poner los botones de previsualización juntos.
        self.preview_frame.pack(pady=10)
        # Ponemos esta caja invisible en la ventana.

        self.preview_audio_button = tk.Button(self.preview_frame, text="Escuchar Audio", command=self.start_preview_thread)
        # Creamos un botón que dice "Escuchar Audio".
        # Cuando lo presiones, hará la magia de 'start_preview_thread'.
        self.preview_audio_button.pack(side=tk.LEFT, padx=5)
        # Ponemos el botón a la izquierda de la caja invisible.

        self.play_pause_button = tk.Button(self.preview_frame, text="Reproducir/Pausar", command=self.toggle_play_pause, state=tk.DISABLED)
        # Creamos un botón para reproducir o pausar la música.
        # 'state=tk.DISABLED' significa que al principio está "dormido" y no se puede presionar.
        self.play_pause_button.pack(side=tk.LEFT, padx=5)
        # Lo ponemos al lado del botón de "Escuchar Audio".

        self.stop_button = tk.Button(self.preview_frame, text="Detener", command=self.stop_preview, state=tk.DISABLED)
        # Creamos un botón para detener la música. También está "dormido" al principio.
        self.stop_button.pack(side=tk.LEFT, padx=5)
        # Lo ponemos al lado del botón de "Reproducir/Pausar".

        # --- Barra de Tiempo (Timeline) ---
        # Esta es la barra mágica que muestra dónde estamos en la canción.
        
        self.timeline_frame = tk.Frame(root)
        # Creamos una caja para la barra de tiempo.
        self.timeline_frame.pack(pady=10, padx=10, fill=tk.X)
        # La ponemos en la ventana y que se estire a lo ancho.

        self.time_label_current = tk.Label(self.timeline_frame, text="00:00")
        # Etiqueta para mostrar el tiempo actual.
        self.time_label_current.pack(side=tk.LEFT)

        self.timeline_scale = tk.Scale(self.timeline_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                     command=self.on_timeline_change, state=tk.DISABLED)
        # Creamos la barra deslizante para la línea de tiempo.
        self.timeline_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        self.time_label_total = tk.Label(self.timeline_frame, text="00:00")
        # Etiqueta para mostrar el tiempo total.
        self.time_label_total.pack(side=tk.LEFT)

        # --- Controles para el Timeline (Reducir Lag) ---
        # Estos controles ayudan a reducir el lag durante la reproducción
        
        self.timeline_options_frame = tk.Frame(root)
        self.timeline_options_frame.pack(pady=5)
        
        self.disable_timeline_var = tk.BooleanVar(value=False)
        self.disable_timeline_check = tk.Checkbutton(
            self.timeline_options_frame, 
            text="Deshabilitar actualizaciones de timeline (reduce lag)",
            variable=self.disable_timeline_var,
            command=self.toggle_timeline_updates
        )
        self.disable_timeline_check.pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.timeline_options_frame, text="Intervalo (ms):").pack(side=tk.LEFT)
        self.timeline_interval_var = tk.StringVar(value="3000")
        self.timeline_interval_entry = tk.Entry(self.timeline_options_frame, width=6, textvariable=self.timeline_interval_var)
        self.timeline_interval_entry.pack(side=tk.LEFT, padx=5)
        self.timeline_interval_entry.bind('<Return>', self.update_timeline_interval)

        # --- Botones para Descargar (Guardar la Música) ---
        # Estos son los botones para guardar la música o el video en tu computadora.

        self.download_frame = tk.Frame(root)
        # Otra caja invisible para los botones de descarga.
        self.download_frame.pack(pady=10)
        # La ponemos en la ventana.

        self.download_video_button = tk.Button(self.download_frame, text="Descargar Video", command=lambda: self.start_download_thread('video'))
        # Botón para descargar el video completo.
        # 'lambda' es como una pequeña nota que dice "haz esto cuando me presiones".
        self.download_video_button.pack(side=tk.LEFT, padx=10);

        self.download_audio_button = tk.Button(self.download_frame, text="Descargar Audio", command=lambda: self.start_download_thread('audio'))
        # Botón para descargar solo la música.
        self.download_audio_button.pack(side=tk.LEFT, padx=10);

        self.progress_text = tk.Text(root, height=15, width=80)
        # Este es como un cuaderno grande donde el programa escribe lo que está haciendo.
        self.progress_text.pack(pady=10, padx=10);

        # --- Cosas que Recordamos (Variables de Estado) ---
        # Estas son como las notas que el programa guarda para recordar cosas.

        self.download_folder = ""
        # Aquí guardamos el nombre de la carpeta donde quieres guardar las cosas.

        self.player = None
        # Aquí guardamos nuestro reproductor de música cuando está funcionando. Al principio, no hay ninguno.

        self.temp_audio_file = None
        # Aquí guardamos la referencia al archivo temporal de audio para poder borrarlo después.

        # --- Variables para la Barra de Tiempo ---
        # Estas son las notas especiales para controlar la línea de tiempo.
        
        self.audio_duration = 0
        # Aquí guardamos cuánto dura toda la canción.
        
        self.is_seeking = False
        # Esta nota nos dice si estamos moviendo la barra manualmente.
        
        self.timeline_update_job = None
        # Aquí guardamos el trabajo de actualizar la barra de tiempo.
        
        self.timeline_update_interval = 3000  # Actualizar cada 3 segundos para evitar lag
        # Intervalo de actualización del timeline en milisegundos
        
        self.disable_timeline_updates = False
        # Opción para deshabilitar actualizaciones del timeline completamente

        self.load_last_folder()
        # Al principio, el programa intenta recordar la última carpeta que usaste.

        self.ram_label = tk.Label(root, text="Uso de RAM: Calculando...")
        self.ram_label.pack(pady=5)
        self.update_ram_usage()

    # --- Magia para Recordar Carpetas (Métodos de Archivos) ---
    # Estas son las instrucciones para guardar y recordar la carpeta.

    def load_last_folder(self):
        # Esta es la magia para leer el papelito de la última carpeta.
        try:
            # 'try' es como decir "intenta hacer esto, y si no puedes, no te preocupes".
            if os.path.exists(self.config_file):
                # 'os.path.exists' es como preguntar "¿Existe este papelito?"
                with open(self.config_file, 'r') as f:
                    # 'open' es como abrir el papelito. 'r' significa que solo lo vamos a leer.
                    # 'as f' es como darle un nombre corto al papelito mientras lo usamos.
                    last_folder = f.read().strip()
                    # Leemos lo que dice el papelito y quitamos los espacios extra.
                    if os.path.isdir(last_folder):
                        # 'os.path.isdir' es como preguntar "¿Es esto una carpeta de verdad?"
                        self.download_folder = last_folder
                        # Si es una carpeta de verdad, la recordamos.
                        self.folder_path_label.config(text=self.download_folder)
        except Exception:
            # 'except Exception' es como decir "si algo sale mal al leer el papelito, no hagas nada".
            pass
            # 'pass' significa "no hagas nada".

    def save_last_folder(self):
        # Esta es la magia para escribir en el papelito la carpeta actual.
        try:
            with open(self.config_file, 'w') as f:
                # 'w' significa que vamos a escribir en el papelito (y si no existe, lo crea).
                f.write(self.download_folder)
                # Escribimos el nombre de la carpeta en el papelito.
        except Exception:
            # Si algo sale mal al escribir, no es un gran problema, así que no hacemos nada.
            pass

    def select_folder(self):
        # Esta es la magia para que aparezca la ventana y elijas una carpeta.
        folder_selected = filedialog.askdirectory()
        # 'filedialog.askdirectory()' es la varita mágica que abre la ventana para elegir carpetas.
        if folder_selected:
            # Si elegiste una carpeta (no cerraste la ventana sin elegir nada)...
            self.download_folder = folder_selected
            # Recordamos la carpeta que elegiste.
            self.folder_path_label.config(text=self.download_folder)
            # Actualizamos el cartelito de la carpeta.
            self.save_last_folder()
            # Y guardamos la carpeta en el papelito para la próxima vez.

    # --- Magia para Escuchar Música (Métodos de Previsualización) ---
    # Estas son las instrucciones para que la música suene.

    def start_preview_thread(self):
        # Esta es la magia que empieza a buscar la música en un hilo separado.
        # 'threading.Thread' es como decir "haz esto en otra mano de la computadora".
        logging.info("=== INICIANDO PREVIEW THREAD ===")
        url = self.url_entry.get()
        logging.info(f"URL obtenida: {url}")
        # Leemos la dirección de YouTube que escribiste.
        if not url:
            # Si no escribiste nada...
            logging.warning("No se proporcionó URL")
            self.root.after(0, lambda: messagebox.showerror("Error", "Por favor, ingresa una URL."))
            # Aparece un cartelito de error.
            return
            # Y la magia se detiene aquí.
        
        logging.info("Limpiando texto de progreso y iniciando thread")
        self.root.after(0, lambda: self.progress_text.delete(1.0, tk.END))
        self.root.after(0, lambda: self.progress_text.insert(tk.END, "Obteniendo información del audio para previsualizar...\n"))
        
        preview_thread = threading.Thread(target=self.execute_preview, args=(url,))
        # Creamos un nuevo hilo (otra mano) para hacer la magia de 'execute_preview'.
        preview_thread.daemon = True
        # 'daemon = True' es como decir "si el programa principal se va a dormir, tú también puedes irte a dormir".
        logging.info("Thread creado, iniciando...")
        preview_thread.start()
        logging.info("Thread iniciado exitosamente")
        # ¡Empezamos la magia en la otra mano!

    def execute_preview(self, url):
        logging.info("=== EJECUTANDO PREVIEW ===")
        try:
            # Deshabilitar el botón para prevenir clics múltiples
            self.root.after(0, lambda: self.preview_audio_button.config(state=tk.DISABLED))
            
            # Actualizaciones seguras de la GUI
            self.root.after(0, lambda: self.progress_text.insert(tk.END, "Descargando audio temporal para previsualización...\n"))
            
            # Crear nombre base para el archivo temporal (sin extensión)
            with tempfile.NamedTemporaryFile(delete=False) as temp_audio:
                temp_filename_base = temp_audio.name
            
            logging.info(f"Nombre base para archivo temporal: {temp_filename_base}")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': temp_filename_base + '.%(ext)s',  # Usar template explícito para la extensión
                'quiet': True,
                'noprogress': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logging.info("Descargando audio temporal...")
                info = ydl.extract_info(url, download=True)
                
                # Construir el nombre del archivo usando la extensión de la info
                actual_filename = f"{temp_filename_base}.{info['ext']}"
                logging.info(f"Archivo esperado: {actual_filename}")
                
                # También buscar archivos con glob como respaldo
                import glob
                possible_files = glob.glob(f"{temp_filename_base}.*")
                logging.info(f"Archivos encontrados con glob: {possible_files}")
                
                # Verificar si el archivo esperado existe
                if os.path.exists(actual_filename):
                    logging.info(f"Archivo encontrado en ubicación esperada: {actual_filename}")
                elif possible_files:
                    actual_filename = possible_files[0]
                    logging.info(f"Usando archivo encontrado con glob: {actual_filename}")
                else:
                    # Listar contenido del directorio temporal para debug
                    temp_dir = os.path.dirname(temp_filename_base)
                    temp_files = os.listdir(temp_dir) if os.path.exists(temp_dir) else []
                    logging.error(f"Contenido del directorio temporal {temp_dir}: {temp_files}")
                    raise Exception(f"No se encontró archivo descargado. Esperado: {actual_filename}, Encontrados: {possible_files}")
                
                # Verificar si el archivo existe y tiene tamaño > 0
                if not os.path.exists(actual_filename) or os.path.getsize(actual_filename) == 0:
                    raise Exception(f"Archivo temporal no creado o vacío: {actual_filename}")
                
                # Obtenemos la duración del audio desde la información de YouTube
                self.audio_duration = info.get('duration', 0)
                logging.info(f"Duración del audio: {self.audio_duration} segundos")

            logging.info("Deteniendo preview anterior si existe")
            self.stop_preview()

            logging.info("Creando MediaPlayer con archivo local...")
            self.player = MediaPlayer(actual_filename)
            self.temp_audio_file = actual_filename  # Guardamos la referencia para borrarlo después
            logging.info("MediaPlayer creado exitosamente")
            
            # Actualizaciones seguras de la GUI
            logging.info("Actualizando GUI - habilitando botones")
            self.root.after(0, lambda: self.play_pause_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.timeline_scale.config(state=tk.NORMAL))
            
            logging.info("Configurando timeline...")
            self.root.after(0, lambda: self.setup_timeline())
            
            logging.info("Iniciando actualizaciones de timeline...")
            # Aumentar el delay inicial para dar tiempo al reproductor de estabilizarse
            self.root.after(2500, lambda: self.start_timeline_updates())
            
            self.root.after(0, lambda: self.progress_text.insert(tk.END, "Previsualización lista. Presiona Reproducir/Pausar.\n"))
            logging.info("=== PREVIEW CONFIGURADO EXITOSAMENTE ===")

        except Exception as e:
            logging.error(f"Error en execute_preview: {e}", exc_info=True)
            error_message = f"Ha ocurrido un error inesperado: {e}"
            self.root.after(0, lambda: messagebox.showerror("Error de Previsualización", f"No se pudo obtener el audio: {str(e)}"))
            self.root.after(0, lambda: self.progress_text.insert(tk.END, f"\nError al previsualizar: {str(e)}"))
        finally:
            # Siempre re-habilitar el botón al final (éxito o error)
            self.root.after(0, lambda: self.preview_audio_button.config(state=tk.NORMAL))

    def toggle_play_pause(self):
        # Esta es la magia para que la música se pause o siga sonando.
        logging.info("=== TOGGLE PLAY/PAUSE PRESIONADO ===")
        try:
            if self.player:
                # Si tenemos un reproductor de música...
                logging.info("Player existe, llamando toggle_pause()")
                self.player.toggle_pause()
                logging.info("toggle_pause() ejecutado exitosamente")
                # Le decimos al reproductor que pause o siga.
            else:
                logging.warning("No hay player disponible para toggle_pause")
        except Exception as e:
            logging.error(f"Error en toggle_play_pause: {e}", exc_info=True)
            # Si hay error, mostramos mensaje seguro
            self.root.after(0, lambda: messagebox.showerror("Error de Reproducción", f"Error al reproducir/pausar: {e}"))

    def stop_preview(self):
        # Esta es la magia para detener la música por completo.
        if self.player:
            # Si tenemos un reproductor de música...
            self.player.close_player()
            # Le decimos al reproductor que se detenga y se guarde.
            self.player = None
            # Borramos el reproductor para que no quede nada.
            
        # Borrar el archivo temporal si existe
        if self.temp_audio_file and os.path.exists(self.temp_audio_file):
            try:
                # Borrar el archivo
                os.remove(self.temp_audio_file)
                logging.info(f"Archivo temporal borrado: {self.temp_audio_file}")
                
                # Borrar el directorio temporal si está vacío
                temp_dir = os.path.dirname(self.temp_audio_file)
                try:
                    os.rmdir(temp_dir)
                    logging.info(f"Directorio temporal borrado: {temp_dir}")
                except OSError:
                    # El directorio no está vacío o no se puede borrar, no es crítico
                    pass
                    
            except Exception as e:
                logging.warning(f"No se pudo borrar el archivo temporal: {e}")
            self.temp_audio_file = None
            
        # Actualizaciones seguras de la GUI
        self.root.after(0, lambda: self.play_pause_button.config(state=tk.DISABLED))
        # Le decimos al botón de "Reproducir/Pausar" que se "duerma" de nuevo.
        self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
        # Le decimos al botón de "Detener" que también se "duerma".
        self.root.after(0, lambda: self.timeline_scale.config(state=tk.DISABLED))
        # Dormimos la barra de tiempo también.
        self.root.after(0, lambda: self.stop_timeline_updates())
        # Detenemos las actualizaciones de la barra de tiempo.
        self.root.after(0, lambda: self.reset_timeline())
        # Reiniciamos la barra de tiempo a cero.
        self.root.after(0, lambda: self.progress_text.insert(tk.END, "Previsualización detenida.\n"))
        # Escribimos en nuestro cuaderno que la música se detuvo.

    # --- Magia para Descargar (Métodos de Descarga) ---
    # Estas son las instrucciones para guardar la música o el video.

    def start_download_thread(self, download_type):
        # Esta es la magia que empieza a descargar en un hilo separado.
        url = self.url_entry.get()
        # Leemos la dirección de YouTube.
        if not url:
            # Si no escribiste nada...
            self.root.after(0, lambda: messagebox.showerror("Error", "Por favor, ingresa una URL."))
            return
        if not self.download_folder:
            # Si no elegiste una carpeta...
            self.root.after(0, lambda: messagebox.showerror("Error", "Por favor, selecciona una carpeta de descarga."))
            return

        self.stop_preview()
        # Si la música estaba sonando, la detenemos antes de descargar.

        # Limpiar y actualizar el texto de progreso de forma segura
        self.root.after(0, lambda: self.progress_text.delete(1.0, tk.END))
        self.root.after(0, lambda: self.progress_text.insert(tk.END, f"Iniciando descarga de {download_type}...\n"))
        
        download_thread = threading.Thread(target=self.execute_download, args=(url, download_type))
        # Creamos un nuevo hilo para la magia de 'execute_download'.
        download_thread.daemon = True
        download_thread.start()
        # ¡Empezamos la magia de descarga!



    def execute_download(self, url, download_type):
        # Esta es la magia principal para descargar la música o el video.
        try:
            output_template = os.path.join(self.download_folder, '%(title)s.%(ext)s')
            # Le decimos dónde guardar el archivo y cómo llamarlo.

            if download_type == 'video':
                # Si queremos descargar el video...
                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',  # Queremos el mejor video y audio.
                    'outtmpl': output_template,  # Dónde guardarlo.
                    'quiet': True,
                    'noprogress': True, # No queremos que yt-dlp muestre su propia barra de progreso.
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
                    'quiet': True,
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

    # --- Magia para la Barra de Tiempo (Métodos de Timeline) ---
    # Estas son las instrucciones para que la barra de tiempo funcione correctamente.

    def setup_timeline(self):
        # Esta magia configura la barra de tiempo con la duración correcta.
        logging.info(f"Configurando timeline con duración: {self.audio_duration}")
        try:
            if self.audio_duration > 0:
                # Si sabemos cuánto dura la canción...
                self.timeline_scale.config(to=self.audio_duration, resolution=0.1)
                # Configuramos la barra para que vaya de 0 hasta la duración total con resolución fina.
                total_time = self.format_time(self.audio_duration)
                # Convertimos los segundos a formato "mm:ss".
                self.time_label_total.config(text=total_time)
                # Mostramos el tiempo total en la etiqueta.
                logging.info(f"Timeline configurado: 0 a {self.audio_duration}, tiempo total: {total_time}")
            else:
                # Si no sabemos la duración...
                self.timeline_scale.config(to=100, resolution=0.1)
                # Usamos 100 como máximo temporal.
                self.time_label_total.config(text="--:--")
                # Mostramos guiones en lugar del tiempo.
                logging.info("Timeline configurado con duración desconocida (0-100)")
        except Exception as e:
            logging.error(f"Error en setup_timeline: {e}", exc_info=True)

    def start_timeline_updates(self):
        # Esta magia empieza a actualizar la barra de tiempo regularmente.
        logging.info("=== INICIANDO ACTUALIZACIONES DE TIMELINE ===")
        self.update_timeline()
        # Llamamos a la primera actualización.

    def update_timeline(self):
        # Esta es la magia que actualiza la posición de la barra de tiempo.
        logging.debug("update_timeline() llamado")
        try:
            # Si las actualizaciones están deshabilitadas, no hacer nada
            if self.disable_timeline_updates:
                logging.debug("Actualizaciones de timeline deshabilitadas")
                return
                
            if self.player and not self.is_seeking:
                # Si tenemos un reproductor y no estamos moviendo la barra manualmente...
                logging.debug("Player existe y no estamos seeking, obteniendo tiempo actual...")
                try:
                    # Verificar si el player está realmente listo
                    if hasattr(self.player, 'get_pts'):
                        current_time = self.player.get_pts()
                        logging.debug(f"Tiempo actual obtenido: {current_time}")
                        
                        # Clamp PTS to prevent overflow beyond duration
                        if current_time is not None and isinstance(current_time, (int, float)):
                            if current_time > self.audio_duration:
                                logging.warning(f"PTS excedió duración ({current_time} > {self.audio_duration}), pausando player")
                                current_time = self.audio_duration
                                try:
                                    self.player.set_pause(True)  # Pause when reaching end
                                except:
                                    pass
                            
                            # Validar que el tiempo sea un número válido y dentro de rango
                            if 0 <= current_time <= self.audio_duration + 1:
                                # Si el tiempo es válido...
                                logging.debug(f"Actualizando timeline a posición: {current_time}")
                                # Usar root.after para actualizaciones seguras de GUI
                                self.root.after(0, lambda t=current_time: self._update_timeline_gui(t))
                            else:
                                logging.debug(f"Tiempo inválido recibido: {current_time} - Deteniendo player")
                                self.stop_preview()  # Stop if stuck/invalid
                        else:
                            logging.debug(f"Tiempo inválido recibido: {current_time} - tipo incorrecto")
                            self.stop_preview()  # Stop if stuck/invalid
                    else:
                        logging.warning("Player no tiene método get_pts disponible")
                except Exception as e:
                    # Si algo sale mal al obtener el tiempo, lo registramos pero continuamos
                    logging.error(f"Error al obtener tiempo del player: {e}", exc_info=True)
            else:
                if not self.player:
                    logging.debug("No hay player disponible para actualizar timeline")
                if self.is_seeking:
                    logging.debug("Saltando actualización porque estamos seeking")
            
            # Programamos la próxima actualización usando el intervalo configurable
            if self.player:
                logging.debug(f"Programando próxima actualización de timeline en {self.timeline_update_interval}ms")
                self.timeline_update_job = self.root.after(self.timeline_update_interval, self.update_timeline)
            else:
                logging.debug("No hay player, no programando próxima actualización")
        except Exception as e:
            logging.error(f"Error crítico en update_timeline: {e}", exc_info=True)
            # Intentar continuar con las actualizaciones después de un error con intervalo mayor
            if self.player:
                self.timeline_update_job = self.root.after(self.timeline_update_interval * 2, self.update_timeline)

    def _update_timeline_gui(self, current_time):
        # Método auxiliar para actualizar la GUI de forma segura
        try:
            # Temporarily disable command to prevent triggering on_timeline_change
            original_command = self.timeline_scale.cget('command')
            self.timeline_scale.config(command=None)
            self.timeline_scale.set(current_time)
            # Restore command
            self.timeline_scale.config(command=original_command)
            
            formatted_time = self.format_time(current_time)
            # Convertimos el tiempo a formato "mm:ss".
            self.time_label_current.config(text=formatted_time)
            # Actualizamos la etiqueta del tiempo actual.
            logging.debug(f"Timeline actualizado exitosamente: {formatted_time}")
        except Exception as e:
            logging.error(f"Error al actualizar GUI del timeline: {e}", exc_info=True)

    def stop_timeline_updates(self):
        # Esta magia detiene las actualizaciones de la barra de tiempo.
        if self.timeline_update_job:
            # Si hay un trabajo de actualización programado...
            self.root.after_cancel(self.timeline_update_job)
            # Lo cancelamos.
            self.timeline_update_job = None
            # Y borramos la referencia.

    def reset_timeline(self):
        # Esta magia reinicia la barra de tiempo a cero.
        self.timeline_scale.set(0)
        # Ponemos la barra en posición cero.
        self.time_label_current.config(text="00:00")
        # Reiniciamos el tiempo actual.
        self.time_label_total.config(text="00:00")
        # Reiniciamos el tiempo total.

    def on_timeline_change(self, value):
        # Esta magia se activa cuando mueves la barra de tiempo manualmente.
        if self.player:
            # Si tenemos un reproductor...
            self.is_seeking = True
            # Marcamos que estamos buscando una posición específica.
            try:
                seek_time = float(value)
                # Clamp to valid range to avoid errors
                seek_time = max(0, min(seek_time, self.audio_duration))
                logging.debug(f"Seeking a posición: {seek_time}")
                
                # Check if player is currently playing to restore state after seek
                was_playing = False
                try:
                    was_playing = not self.player.get_pause()
                except:
                    pass  # If we can't get pause state, continue anyway
                
                # Pause during seek to prevent advance during debounce
                if was_playing:
                    self.player.set_pause(True)
                
                # Seek with accurate positioning to avoid keyframe snapping
                self.player.seek(seek_time, relative=False, accurate=True)
                
                # Restore playing state if it was playing before
                if was_playing:
                    self.player.set_pause(False)
                
                # Le decimos al reproductor que vaya a esa posición.
                formatted_time = self.format_time(seek_time)
                # Convertimos el tiempo a formato "mm:ss".
                self.time_label_current.config(text=formatted_time)
                # Actualizamos la etiqueta del tiempo actual.
                logging.debug(f"Seek exitoso a: {formatted_time}")
            except Exception as e:
                # Si algo sale mal al buscar, lo registramos.
                logging.error(f"Error en seek: {e}", exc_info=True)
            finally:
                # Siempre, al final...
                self.root.after(200, lambda: setattr(self, 'is_seeking', False))
                # Después de 0.2 segundos, marcamos que ya no estamos buscando.

    def format_time(self, seconds):
        # Esta magia convierte segundos a formato "mm:ss".
        if seconds is None or seconds < 0:
            # Si no hay tiempo válido...
            return "00:00"
        
        minutes = int(seconds // 60)
        # Calculamos los minutos.
        seconds = int(seconds % 60)
        # Calculamos los segundos restantes.
        return f"{minutes:02d}:{seconds:02d}"
        # Devolvemos el tiempo en formato "mm:ss".

    def toggle_timeline_updates(self):
        # Esta función habilita o deshabilita las actualizaciones del timeline
        self.disable_timeline_updates = self.disable_timeline_var.get()
        if self.disable_timeline_updates:
            # Si se deshabilitan las actualizaciones
            self.progress_text.insert(tk.END, "Actualizaciones de timeline deshabilitadas para reducir lag.\n")
            self.stop_timeline_updates()
        else:
            # Si se habilitan las actualizaciones
            self.progress_text.insert(tk.END, "Actualizaciones de timeline habilitadas.\n")
            if self.player:
                self.start_timeline_updates()

    def update_timeline_interval(self, event=None):
        # Esta función actualiza el intervalo de actualización del timeline
        try:
            new_interval = int(self.timeline_interval_var.get())
            if new_interval < 100:
                new_interval = 100  # Mínimo 100ms
            elif new_interval > 10000:
                new_interval = 10000  # Máximo 10 segundos
            
            self.timeline_update_interval = new_interval
            self.timeline_interval_var.set(str(new_interval))
            self.progress_text.insert(tk.END, f"Intervalo de actualización cambiado a {new_interval}ms.\n")
            
            # Si hay actualizaciones activas, reiniciarlas con el nuevo intervalo
            if self.player and not self.disable_timeline_updates:
                self.stop_timeline_updates()
                self.start_timeline_updates()
        except ValueError:
            self.progress_text.insert(tk.END, "Por favor ingresa un número válido para el intervalo.\n")
            self.timeline_interval_var.set(str(self.timeline_update_interval))

    def update_ram_usage(self):
        # Esta función obtiene y muestra el uso de RAM del programa.
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        # Convertir bytes a MB
        ram_usage_mb = mem_info.rss / (1024 * 1024)
        self.ram_label.config(text=f"Uso de RAM: {ram_usage_mb:.2f} MB")
        # Programar la próxima actualización en 2 segundos (2000 milisegundos)
        self.root.after(2000, self.update_ram_usage)

# --- El Gran Inicio (Punto de Entrada) ---
# Esto es como cuando le dices a la computadora: "¡Empieza el programa!"

if __name__ == "__main__":
    # Esto significa: "Si este es el archivo principal que estás ejecutando, haz lo siguiente".
    root = tk.Tk()
    # Creamos nuestra ventana principal, el lienzo grande.
    app = DownloaderApp(root)
    # Creamos nuestra caja de juguetes principal (la aplicación).
    
    # Asegurarse de que el reproductor se cierre al cerrar la ventana
    def on_closing():
        # Esta es una pequeña magia que se activa cuando intentas cerrar la ventana.
        app.stop_preview()
        # Le decimos a la aplicación que detenga cualquier música que esté sonando y limpie archivos temporales.
        root.destroy()
        # Y luego cerramos la ventana por completo.

    root.protocol("WM_DELETE_WINDOW", on_closing)
    # Le decimos a la ventana que cuando alguien intente cerrarla (con la 'X'), use nuestra magia 'on_closing'.
    root.mainloop()
    # ¡Esto hace que la ventana se quede abierta y espere a que hagas cosas!
    # Es como el corazón del programa, lo mantiene vivo.