from moviepy.editor import ImageClip, TextClip, CompositeVideoClip, ColorClip, AudioFileClip
from moviepy.config import change_settings
import sys
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Configurar la ruta a ImageMagick
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})
# Función para cargar imágenes desde una carpeta o argumentos
def load_images(image_paths):
    images = []
    for path in image_paths:
        if os.path.exists(path):
            try:
                # Cargar y redimensionar imagen con Pillow
                img = Image.open(path).convert("RGB")
                # Calcular nuevo ancho proporcional para altura de 1000 (ajustado para caber dentro del marco)
                aspect_ratio = img.width / img.height
                new_width = int(1000 * aspect_ratio)
                img = img.resize((new_width, 1000), Image.Resampling.LANCZOS)
                # Convertir imagen a array NumPy para MoviePy
                img_array = np.array(img)
                # Crear ImageClip con la imagen redimensionada
                clip = ImageClip(img_array)
                images.append(clip)
            except Exception as e:
                print(f"Error al cargar la imagen {path}: {e}")
        else:
            print(f"Imagen no encontrada: {path}")
    return images

# Función para crear una imagen de texto con fondo usando Pillow
def create_text_image_with_background(text, width, height, font_path="Arial", font_size=30, text_color=(255, 255, 255), stroke_color=(0, 0, 0), stroke_width=2, position=("center", 1500)):
    # Crear una imagen transparente
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Cargar fuente
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    # Calcular tamaño del texto
    text_bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Calcular posición del texto
    if position[0] == "center":
        x = (width - text_width) // 2
    else:
        x = position[0]
    y = position[1]

    # Dibujar un cuadro de fondo (negro con 50% de opacidad)
    padding = 10  # Margen alrededor del texto
    box_x1 = x - padding
    box_y1 = y - padding
    box_x2 = x + text_width + padding
    box_y2 = y + text_height + padding
    draw.rectangle(
        (box_x1, box_y1, box_x2, box_y2),
        fill=(0, 0, 0, 128)  # Negro con 50% de opacidad
    )

    # Dibujar el texto con borde
    draw.text(
        (x, y),
        text,
        fill=text_color,
        font=font,
        stroke_width=stroke_width,
        stroke_fill=stroke_color
    )

    return np.array(img)

# Configuración del video
duration_per_image = 4  # Segundos por imagen
text_duration = 3.5     # Duración del texto por frase
video_size = (1080, 1920)  # Formato vertical para Reels
font = r"C:\Windows\Fonts\arial.ttf"  # Ruta completa a la fuente
font_size = 50              # Reducido para que quepa dentro del marco
text_color = (255, 255, 255)  # Blanco
stroke_color = (0, 0, 0)      # Negro
stroke_width = 2

# Guion se lee desde un archivo
try:
    with open("guion.txt", "r", encoding="utf-8") as f:
        script = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print("Error: No se encontró el archivo guion.txt")
    sys.exit(1)
except Exception as e:
    print(f"Error al leer guion.txt: {e}")
    sys.exit(1)

# Archivos de entrada
background_path = "background.jpg"
frame_logo_path = "frame_logo.png"
music_path = "background_music.mp3"

# Cargar imágenes desde argumentos o carpeta
if len(sys.argv) > 1:
    image_paths = sys.argv[1:]  # Imágenes pasadas como argumentos
else:
    # Alternativa: Cargar desde una carpeta
    image_folder = "images"
    try:
        image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith(('.jpg', '.png'))]
    except FileNotFoundError:
        print("Error: La carpeta 'images' no existe o no contiene imágenes.")
        sys.exit(1)

# Cargar imágenes
images = load_images(image_paths)

# Validar que haya imágenes
if not images:
    print("Error: No se encontraron imágenes.")
    sys.exit(1)

# Crear clip de fondo
if os.path.exists(background_path):
    try:
        # Cargar fondo con Pillow y redimensionar
        bg_img = Image.open(background_path).convert("RGB")
        bg_img = bg_img.resize(video_size, Image.Resampling.LANCZOS)
        bg_array = np.array(bg_img)
        background = ImageClip(bg_array).set_duration(len(images) * duration_per_image)
    except Exception as e:
        print(f"Error al cargar background.jpg: {e}")
        background = ColorClip(size=video_size, color=(53, 94, 59)).set_duration(len(images) * duration_per_image)  # Verde oscuro #355E3B
else:
    print("Fondo no encontrado. Usando fondo verde oscuro por defecto.")
    background = ColorClip(size=video_size, color=(53, 94, 59)).set_duration(len(images) * duration_per_image)

# Crear clips de imágenes con transiciones
image_clips = []
for i, img in enumerate(images):
    try:
        clip = img.set_duration(duration_per_image).set_position("center").crossfadein(0.5)
        clip = clip.set_start(i * duration_per_image)
        image_clips.append(clip)
    except Exception as e:
        print(f"Error al procesar la imagen {i + 1}: {e}")

# Crear clips de texto con fondo
text_clips = []
for i, text in enumerate(script):
    try:
        print(f"Creando clip de texto: {text}")
        # Crear imagen de texto con fondo usando Pillow
        text_img = create_text_image_with_background(
            text,
            video_size[0],
            video_size[1],
            font_path=font,
            font_size=font_size,
            text_color=text_color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            position=("center", 1500)  # Ajustado más abajo para que quepa dentro del marco
        )
        txt_clip = ImageClip(text_img).set_duration(text_duration).set_start(i * duration_per_image)
        # Como estamos usando ImageClip para el texto, no podemos usar crossfadein/out directamente
        text_clips.append(txt_clip)
    except Exception as e:
        print(f"Error al crear texto {text}: {e}")
print(f"Total de clips de texto creados: {len(text_clips)}")

# Cargar marco con logotipo
if os.path.exists(frame_logo_path):
    try:
        # Cargar marco con Pillow y redimensionar
        frame_img = Image.open(frame_logo_path).convert("RGBA")
        frame_img = frame_img.resize(video_size, Image.Resampling.LANCZOS)
        frame_array = np.array(frame_img)
        frame_logo = ImageClip(frame_array).set_duration(len(images) * duration_per_image)
    except Exception as e:
        print(f"Error al cargar frame_logo.png: {e}")
        frame_logo = None
else:
    print("Marco con logotipo no encontrado. Se omite.")
    frame_logo = None

# Combinar todos los clips
clips = [background] + image_clips + text_clips
if frame_logo:
    clips.append(frame_logo)

# Crear video
final_clip = CompositeVideoClip(clips, size=video_size)

# Agregar música (opcional)
if os.path.exists(music_path):
    try:
        audio = AudioFileClip(music_path).subclip(0, final_clip.duration)
        final_clip = final_clip.set_audio(audio)
    except Exception as e:
        print(f"Error al cargar música: {e}")

# Exportar video
output_path = "corewave_reel.mp4"
try:
    final_clip.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
except Exception as e:
    print(f"Error al generar el video: {e}")
finally:
    final_clip.close()  # Liberar recursos

print(f"Video generado: {output_path}")