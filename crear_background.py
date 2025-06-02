from PIL import Image, ImageDraw
import numpy as np
import sys
import argparse
import re

# Configuración
width, height = 1080, 1920
output_path = "background.jpg"

# Función para validar y convertir color hexadecimal a RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#').strip()
    if not re.match(r'^[0-9A-Fa-f]{6}$', hex_color):
        raise ValueError(f"Color inválido: {hex_color}. Usa formato hexadecimal (ej., #1E3A8A)")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Crear gradiente con hasta 3 colores
def create_gradient(colors):
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    
    # Si hay menos de 3 colores, repetir el último
    while len(colors) < 3:
        colors.append(colors[-1])
    
    # Convertir colores a RGB
    c1, c2, c3 = [hex_to_rgb(c) for c in colors]
    
    # Generar gradiente
    for y in range(height):
        t = y / height
        if t < 0.5:
            # Primera mitad: c1 -> c2
            r = int(c1[0] + (c2[0] - c1[0]) * (t * 2))
            g = int(c1[1] + (c2[1] - c1[1]) * (t * 2))
            b = int(c1[2] + (c2[2] - c1[2]) * (t * 2))
        else:
            # Segunda mitad: c2 -> c3
            r = int(c2[0] + (c3[0] - c2[0]) * ((t - 0.5) * 2))
            g = int(c2[1] + (c3[1] - c2[1]) * ((t - 0.5) * 2))
            b = int(c2[2] + (c3[2] - c2[2]) * ((t - 0.5) * 2))
        draw.line((0, y, width, y), fill=(r, g, b))
    return img

# Agregar formas abstractas según la variación
def add_shapes(img, variation):
    draw = ImageDraw.Draw(img, "RGBA")
    
    if variation in ["ondas", "mixto"]:
        # Ondas blancas en la parte inferior
        for y in range(height - 400, height, 60):
            draw.rectangle(
                [50, y, width - 50, y + 40],
                fill=(255, 255, 255, 100),  # Blanco semi-transparente
                outline=None
            )
    
    if variation in ["partículas", "mixto"]:
        # Partículas azules en la parte superior
        for _ in range(30):
            x = np.random.randint(100, width - 100)
            y = np.random.randint(100, height // 2)
            radius = np.random.randint(5, 20)
            draw.ellipse(
                [x - radius, y - radius, x + radius, y + radius],
                fill=(96, 165, 250, 80)  # Azul claro semi-transparente
            )
    
    if variation in ["líneas", "mixto"]:
        # Líneas curvas verdes en un lado
        for x in range(50, 150, 30):
            draw.line(
                [(x, height // 2), (x + 50, height - 200)],
                fill=(16, 185, 129, 120),  # Verde menta semi-transparente
                width=10
            )
    
    return img

# Configurar argumentos
parser = argparse.ArgumentParser(description="Generar fondo abstracto para Reels")
parser.add_argument("--colors", nargs='+', default=["#1E3A8A", "#10B981", "#F3F4F6"],
                    help="1 a 3 colores en formato hexadecimal (ej., #1E3A8A)")
parser.add_argument("--variation", choices=["ondas", "partículas", "líneas", "mixto"], default="mixto",
                    help="Variación del diseño: ondas, partículas, líneas o mixto")
args = parser.parse_args()

# Validar colores
if not args.colors:
    print("Error: Debes proporcionar al menos un color con --colors")
    sys.exit(1)

colors = args.colors[:3]  # Tomar hasta 3 colores
try:
    for color in colors:
        hex_to_rgb(color)  # Validar cada color
except ValueError as e:
    print(e)
    sys.exit(1)

# Crear y guardar imagen
img = create_gradient(colors)
img = add_shapes(img, args.variation)
img.save(output_path, "JPEG", quality=95)
print(f"Fondo generado: {output_path}")