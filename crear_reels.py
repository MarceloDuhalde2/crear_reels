from moviepy.editor import ImageClip, CompositeVideoClip, ColorClip, AudioFileClip
from moviepy.video.fx.all import fadein, fadeout
import sys
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import argparse

"""
Ejemplo de comando con todas las posibilidades de configuración:
.\venv\Scripts\python.exe crear_reels.py
    --text-font segoeui.ttf
    --text-style bold
    --text-size 40
    --text-bg-color "255,0,0,128"
    --text-color "0,255,0"
    --text-effect fade
    --image-effect fade
    --image-duration 5
    --text-duration 4
    --output corewave_reel.mp4

Descripción de los parámetros:
- images: Lista de rutas a las imágenes (opcional, si no se especifica, se cargan desde la carpeta 'images').
- --text-font: Nombre del archivo de la fuente (ejemplo: segoeui.ttf para Segoe UI).
- --text-style: Estilo del texto (regular, bold, italic, bolditalic).
- --text-size: Tamaño de la fuente en píxeles (ejemplo: 40).
- --text-bg-color: Color del fondo del texto en formato RGBA (ejemplo: 255,0,0,128 para rojo translúcido).
- --text-color: Color del texto en formato RGB (ejemplo: 0,255,0 para verde).
- --text-effect: Efecto para el texto (none, fade, shadow).
- --image-effect: Efecto para las imágenes (none, fade).
- --image-duration: Duración de cada imagen en segundos (ejemplo: 5).
- --text-duration: Duración de cada frase de texto en segundos (ejemplo: 4).
- --output: Nombre del archivo de salida (ejemplo: corewave_reel.mp4).
"""

# Función para dividir texto en varias líneas si excede el ancho máximo
def split_text_to_lines(text, font, max_width, stroke_width):
    words = text.split()
    lines = []
    current_line = []
    current_width = 0

    for word in words:
        word_bbox = font.getbbox(word, stroke_width=stroke_width)
        word_width = word_bbox[2] - word_bbox[0]

        space_bbox = font.getbbox(" ", stroke_width=stroke_width)
        space_width = space_bbox[2] - space_bbox[0]

        if current_width + word_width + (space_width if current_line else 0) <= max_width:
            current_line.append(word)
            current_width += word_width + (space_width if current_line else 0)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_width = word_width

    if current_line:
        lines.append(" ".join(current_line))

    return lines

# Función para ajustar el tamaño de una imagen manteniendo su relación de aspecto
def resize_with_aspect_ratio(image, max_size):
    width, height = image.size
    aspect_ratio = width / height

    max_width, max_height = max_size
    if width / max_width > height / max_height:
        new_width = max_width
        new_height = int(max_width / aspect_ratio)
    else:
        new_height = max_height
        new_width = int(max_height * aspect_ratio)

    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

# Función para cargar imágenes desde una carpeta o argumentos
def load_images(image_paths):
    images = []
    for path in image_paths:
        if os.path.exists(path):
            try:
                img = Image.open(path)
                is_png = path.lower().endswith('.png')
                if is_png:
                    img = img.convert("RGBA")
                else:
                    img = img.convert("RGB")
                max_size = (800, 800)
                img = resize_with_aspect_ratio(img, max_size)
                img_array = np.array(img)
                clip = ImageClip(img_array, transparent=is_png)
                images.append(clip)
            except Exception as e:
                print(f"Error al cargar la imagen {path}: {e}")
        else:
            print(f"Imagen no encontrada: {path}")
    return images

# Función para ajustar el nombre de la fuente según el estilo
def adjust_font_name(font_filename, style):
    base_name = font_filename.replace('.ttf', '')
    style_suffixes = {
        "regular": "",
        "bold": "b",
        "italic": "i",
        "bolditalic": "z"
    }
    if style != "regular":
        if base_name.endswith(('b', 'i', 'z')):
            base_name = base_name[:-1]
        base_name += style_suffixes[style]
    return f"{base_name}.ttf"

# Función para crear una imagen de texto con fondo usando Pillow
def create_text_image_with_background(
    text,
    width,
    height,
    font_path="Arial",
    font_size=50,
    text_color=(255, 255, 102),
    bg_color=(0, 51, 102, 128),
    stroke_color=(0, 0, 0),
    stroke_width=2,
    position=("center", 1500),
    effect="none"
):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()
        print(f"Error al cargar la fuente {font_path}. Usando fuente por defecto.")

    max_width = width - 200

    lines = split_text_to_lines(text, font, max_width, stroke_width)

    line_heights = []
    line_widths = []
    for line in lines:
        line_bbox = draw.textbbox((0, 0), line, font=font, stroke_width=stroke_width)
        line_width = (line_bbox[2] - line_bbox[0]) + stroke_width * 2
        line_height = (line_bbox[3] - line_bbox[1]) + stroke_width * 2
        line_widths.append(line_width)
        line_heights.append(line_height)

    text_width = max(line_widths)
    text_height = sum(line_heights) + (len(lines) - 1) * 10

    print(f"Tamaño del texto (ancho x alto): {text_width} x {text_height}")

    if position[0] == "center":
        x = (width - text_width) // 2
    else:
        x = position[0]
    y = position[1]

    padding = 20
    box_x1 = x - padding
    box_y1 = y - padding
    box_x2 = x + text_width + padding
    box_y2 = y + text_height + padding
    radius = 20

    print(f"Fondo (x1,y1,x2,y2): ({box_x1}, {box_y1}, {box_x2}, {box_y2})")

    draw.rounded_rectangle(
        (box_x1, box_y1, box_x2, box_y2),
        radius=radius,
        fill=bg_color
    )

    current_y = y
    for line in lines:
        line_bbox = draw.textbbox((0, 0), line, font=font, stroke_width=stroke_width)
        line_width = (line_bbox[2] - line_bbox[0]) + stroke_width * 2
        if position[0] == "center":
            line_x = (width - line_width) // 2
        else:
            line_x = x

        if effect == "shadow":
            shadow_offset = 5
            draw.text(
                (line_x + shadow_offset, current_y + shadow_offset),
                line,
                fill=(0, 0, 0, 128),
                font=font,
                stroke_width=stroke_width,
                stroke_fill=stroke_color
            )

        draw.text(
            (line_x, current_y),
            line,
            fill=text_color,
            font=font,
            stroke_width=stroke_width,
            stroke_fill=stroke_color
        )
        line_height = (line_bbox[3] - line_bbox[1]) + stroke_width * 2
        current_y += line_height + 10

    return np.array(img)

# Función para aplicar efectos a los clips de texto
def apply_text_effect(clip, effect, duration):
    if effect == "fade":
        clip = fadein(clip, 0.5).fadeout(0.5)
    elif effect == "shadow":
        pass  # El efecto shadow ya se aplica al crear la imagen del texto
    return clip

# Función para aplicar efectos a los clips de imágenes
def apply_image_effect(clip, effect, duration):
    if effect == "fade":
        clip = fadein(clip, 0.5).fadeout(0.5)
    return clip

# Función para convertir una cadena RGB a tupla
def parse_rgb(color_str):
    try:
        r, g, b = map(int, color_str.split(","))
        return (r, g, b)
    except Exception as e:
        print(f"Error al parsear color RGB: {e}. Usando color por defecto.")
        return (255, 255, 102)  # Amarillo brillante por defecto

# Función para convertir una cadena RGBA a tupla
def parse_rgba(color_str):
    try:
        r, g, b, a = map(int, color_str.split(","))
        return (r, g, b, a)
    except Exception as e:
        print(f"Error al parsear color RGBA: {e}. Usando color por defecto.")
        return (0, 51, 102, 128)  # Azul oscuro translúcido por defecto

# Configuración de argumentos
parser = argparse.ArgumentParser(description="Generar Reel con imágenes, texto y música")
parser.add_argument("images", nargs='*', help="Rutas a las imágenes para el video")
parser.add_argument("--text-effect", choices=["none", "fade", "shadow"], default="none", help="Efecto para el texto (none, fade, shadow)")
parser.add_argument("--image-effect", choices=["none", "fade"], default="none", help="Efecto para las imágenes (none, fade)")
parser.add_argument("--output", default="sancayetano_reel.mp4", help="Nombre del archivo de salida (ejemplo: mi_reel.mp4)")
parser.add_argument("--text-bg-color", default="0,51,102,128", help="Color del fondo del texto en formato RGBA (ejemplo: 0,51,102,128 para azul oscuro translúcido)")
parser.add_argument("--text-color", default="255,255,102", help="Color del texto en formato RGB (ejemplo: 255,255,102 para amarillo brillante)")
parser.add_argument("--text-font", default="segoeui.ttf", help="Nombre del archivo de la fuente (ejemplo: segoeui.ttf para Segoe UI)")
parser.add_argument("--text-style", choices=["regular", "bold", "italic", "bolditalic"], default="regular", help="Estilo del texto (regular, bold, italic, bolditalic)")
parser.add_argument("--text-size", type=int, default=50, help="Tamaño de la fuente en píxeles (ejemplo: 40)")
parser.add_argument("--image-duration", type=float, default=4.0, help="Duración de cada imagen en segundos (ejemplo: 5.0)")
parser.add_argument("--text-duration", type=float, default=3.5, help="Duración de cada frase de texto en segundos (ejemplo: 4.0)")
args = parser.parse_args()

# Ajustar el nombre del archivo de la fuente según el estilo
font_filename = adjust_font_name(args.text_font, args.text_style)
font = os.path.join(r"C:\Windows\Fonts", font_filename)

# Configuración del video
duration_per_image = args.image_duration  # Usar el valor especificado
text_duration = args.text_duration        # Usar el valor especificado
video_size = (1080, 1920)  # Formato vertical para Reels
font_size = args.text_size  # Usar el tamaño de fuente especificado
text_color = parse_rgb(args.text_color)
bg_color = parse_rgba(args.text_bg_color)
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
image_paths = args.images
if not image_paths:
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

# Crear clips de imágenes con transiciones y efectos
image_clips = []
for i, img in enumerate(images):
    try:
        print(f"Procesando imagen {i + 1}/{len(images)}")
        clip = img.set_duration(duration_per_image)
        clip = apply_image_effect(clip, args.image_effect, duration_per_image)
        clip = clip.set_position("center").set_start(i * duration_per_image)
        print(f"Clip de imagen creado: {clip}")
        image_clips.append(clip)
    except Exception as e:
        print(f"Error al procesar la imagen {i + 1}: {e}")
print(f"Total de clips de imagen creados: {len(image_clips)}")

# Crear clips de texto con fondo
text_clips = []
for i, text in enumerate(script):
    try:
        print(f"Creando clip de texto: {text}")
        text_img = create_text_image_with_background(
            text,
            video_size[0],
            video_size[1],
            font_path=font,
            font_size=font_size,
            text_color=text_color,
            bg_color=bg_color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            position=("center", 1500),
            effect=args.text_effect
        )
        txt_clip = ImageClip(text_img).set_duration(text_duration).set_start(i * duration_per_image)
        txt_clip = apply_text_effect(txt_clip, args.text_effect, text_duration)
        text_clips.append(txt_clip)
    except Exception as e:
        print(f"Error al crear texto {text}: {e}")
print(f"Total de clips de texto creados: {len(text_clips)}")

# Cargar marco con logotipo
if os.path.exists(frame_logo_path):
    try:
        frame_img = Image.open(frame_logo_path).convert("RGBA")
        max_size = (1000, 1800)
        frame_img = resize_with_aspect_ratio(frame_img, max_size)
        frame_array = np.array(frame_img)
        frame_logo = ImageClip(frame_array, transparent=True).set_duration(len(images) * duration_per_image)
        frame_logo = frame_logo.set_position("center")
    except Exception as e:
        print(f"Error al cargar frame_logo.png: {e}")
        frame_logo = None
else:
    print("Marco con logotipo no encontrado. Se omite.")
    frame_logo = None

# Combinar todos los clips, asegurando que el texto esté en la capa superior
clips = [background] + image_clips
if frame_logo:
    clips.append(frame_logo)
clips.extend(text_clips)  # El texto se agrega al final para estar en la capa superior

# Crear video
final_clip = CompositeVideoClip(clips, size=video_size)

# Agregar música (opcional)
if os.path.exists(music_path):
    try:
        audio = AudioFileClip(music_path).subclip(0, final_clip.duration)
        final_clip = final_clip.set_audio(audio)
        print("Música de fondo agregada correctamente")
    except Exception as e:
        print(f"Error al cargar música: {e}")
else:
    print("Archivo de música no encontrado. El video se generará sin música.")

# Exportar video
output_path = args.output
try:
    final_clip.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
except Exception as e:
    print(f"Error al generar el video: {e}")
finally:
    final_clip.close()  # Liberar recursos

print(f"Video generado: {output_path}")