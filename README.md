# YT Steel Sentinel (YTSS)

Una aplicación de escritorio simple para descargar videos de YouTube usando una interfaz gráfica con Tkinter.

## Características

- Interfaz gráfica intuitiva con Tkinter
- Descarga de videos de YouTube usando yt-dlp
- Selección de carpeta de destino
- Validación de URLs
- Progreso de descarga en tiempo real
- Manejo de errores
- Funciona como aplicación standalone

## Requisitos

- Python 3.7 o superior
- yt-dlp
- ffmpeg (opcional, para fusionar audio/video si es necesario)

## Instalación

1. Clona o descarga este repositorio
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. (Opcional) Instala ffmpeg para mejor compatibilidad:
   - Windows: Descarga desde https://ffmpeg.org/download.html
   - O usa chocolatey: `choco install ffmpeg`

## Uso

1. Ejecuta la aplicación:
   ```bash
   python main.py
   ```

2. En la interfaz:
   - Pega la URL del video de YouTube en el campo de texto
   - Selecciona la carpeta donde quieres guardar el video
   - Haz clic en "Descargar"
   - Observa el progreso en el área de texto

## Funcionalidades

- **Validación de URL**: Verifica que la URL sea válida y de YouTube
- **Selección de carpeta**: Interfaz para elegir dónde guardar el archivo
- **Progreso en tiempo real**: Muestra la salida de yt-dlp en tiempo real
- **Manejo de errores**: Informa sobre problemas de URL, dependencias faltantes, etc.
- **Interfaz responsive**: La ventana se puede redimensionar

## Notas

- La aplicación descarga videos en la mejor calidad disponible hasta 720p
- Los archivos se guardan con el nombre original del video
- Si ffmpeg está instalado, yt-dlp puede fusionar audio y video automáticamente
- La aplicación funciona sin necesidad de abrir la consola

## Solución de problemas

- **Error "yt-dlp no está instalado"**: Ejecuta `pip install yt-dlp`
- **Problemas de descarga**: Verifica que la URL sea correcta y que tengas conexión a internet
- **Errores de formato**: Instala ffmpeg para mejor compatibilidad con formatos de video