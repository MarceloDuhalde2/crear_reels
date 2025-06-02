from PIL import Image, ImageDraw
import numpy as np
import argparse
import os
from sklearn.cluster import KMeans

# Configuración
width, height = 1080, 1920
output_path = "frame_logo.png"

# Extraer colores dominantes del logotipo
def extract_colors(image_path, num_colors=3):
    img = Image.open(image_path).convert("RGBA")
    pixels = np.array(img)
    non_transparent = pixels[pixels[:, :, 3] > 0][:, :3]  # Solo píxeles no transparentes
    if len(non_transparent) == 0:
        return [(0, 0, 255), (0, 255, 0), (255, 255, 255)]  # Colores por defecto
    kmeans = KMeans(n_clusters=min(num_colors, len(non_transparent)), random_state=0)
    kmeans.fit(non_transparent)
    colors = kmeans.cluster_centers_.astype(int)
    return [tuple(color) for color in colors]

# Crear marco reutilizable según el estilo
def create_frame(logo_path, colors, style, logo_width):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")
    
    # Cargar y escalar logotipo
    logo = Image.open(logo_path).convert("RGBA")
    logo_height = int(logo.height * (logo_width / logo.width))
    logo = logo.resize((logo_width, logo_height), Image.LANCZOS)
    
    # Colores del marco
    border_color = colors[0] + (200,)  # Primer color, 80% opacidad
    accent_color = colors[1] + (150,)  # Segundo color, 60% opacidad
    
    if style == "moderno":
        # Borde curvo y líneas dinámicas
        draw.rectangle(
            [20, 20, width - 20, height - 20],
            outline=border_color,
            width=8
        )
        # Líneas curvas
        draw.line(
            [(50, 150 + logo_height), (150, 250 + logo_height), (100, 300 + logo_height)],
            fill=accent_color,
            width=5
        )
        # Partículas
        for _ in range(10):
            x = np.random.randint(width - 150, width - 50)
            y = np.random.randint(50, 300)
            radius = np.random.randint(3, 10)
            draw.ellipse(
                [x - radius, y - radius, x + radius, y + radius],
                fill=accent_color
            )
        # Logotipo en esquina superior izquierda
        img.paste(logo, (50, 50), logo)
    
    elif style == "clásico":
        # Borde doble elegante
        draw.rectangle(
            [15, 15, width - 15, height - 15],
            outline=border_color,
            width=5
        )
        draw.rectangle(
            [30, 30, width - 30, height - 30],
            outline=border_color,
            width=3
        )
        # Líneas rectas
        draw.line(
            [(50, 100 + logo_height), (width - 50, 100 + logo_height)],
            fill=accent_color,
            width=4
        )
        # Logotipo centrado arriba
        logo_x = (width - logo_width) // 2
        img.paste(logo, (logo_x, 50), logo)
    
    elif style == "futurista":
        # Borde con efecto neón
        draw.rectangle(
            [25, 25, width - 25, height - 25],
            outline=border_color,
            width=12
        )
        # Círculos neón
        for _ in range(5):
            x = np.random.randint(50, width - 50)
            y = np.random.randint(height - 300, height - 50)
            radius = 15
            draw.ellipse(
                [x - radius, y - radius, x + radius, y + radius],
                outline=accent_color,
                width=3
            )
        # Logotipo en esquina inferior derecha
        img.paste(logo, (width - logo_width - 50, height - logo_height - 50), logo)
    
    elif style == "minimalista":
        # Borde fino simple
        draw.rectangle(
            [10, 10, width - 10, height - 10],
            outline=border_color,
            width=4
        )
        # Logotipo pequeño en esquina superior izquierda
        img.paste(logo, (30, 30), logo)
    
    return img

# Configurar argumentos
parser = argparse.ArgumentParser(description="Generar marco reutilizable con logotipo")
parser.add_argument("--logo", required=True, help="Ruta al logotipo en formato PNG")
parser.add_argument("--style", choices=["moderno", "clásico", "futurista", "minimalista"], default="moderno",
                    help="Estilo del marco: moderno, clásico, futurista o minimalista")
parser.add_argument("--logo-width", type=int, default=None,
                    help="Ancho del logotipo en píxeles (por defecto: 350 moderno/futurista, 400 clásico, 250 minimalista)")
args = parser.parse_args()

# Validar logotipo
if not args.logo.lower().endswith('.png'):
    print("Error: El logotipo debe ser un archivo PNG")
    exit(1)
if not os.path.exists(args.logo):
    print(f"Error: No se encontró el logotipo en {args.logo}")
    exit(1)

# Definir ancho del logotipo
logo_width = args.logo_width
if logo_width is None:
    if args.style == "clásico":
        logo_width = 400
    elif args.style == "minimalista":
        logo_width = 250
    else:  # moderno, futurista
        logo_width = 350

# Extraer colores y crear marco
colors = extract_colors(args.logo)
frame = create_frame(args.logo, colors, args.style, logo_width)

# Guardar imagen
frame.save(output_path, "PNG")
print(f"Marco generado: {output_path}")