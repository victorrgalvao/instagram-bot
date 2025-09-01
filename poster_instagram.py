import os
import time
import datetime
from instagrapi import Client
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURAÇÕES ---
USERNAME = "recomendanimes2"   # seu usuário
PASSWORD = "215507mrg"          # sua senha
SESSION_FILE = "session.json"
IMAGE_DIR = "images"
POST_INTERVAL = 3600            # intervalo entre posts em segundos (ex: 3600 = 1 hora)

os.makedirs(IMAGE_DIR, exist_ok=True)

# --- FUNÇÃO PARA CRIAR IMAGEM ---
def create_image_with_text(texto, largura=1080, altura=1080, font_path="arial.ttf"):
    imagem = Image.new("RGB", (largura, altura), color="white")
    draw = ImageDraw.Draw(imagem)

    # Escolher tamanho de fonte responsivo
    font_size = 60
    font = ImageFont.truetype(font_path, font_size)

    # Ajuste automático do tamanho da fonte se o texto for grande
    bbox = draw.textbbox((0,0), texto, font=font)
    w = bbox[2] - bbox[0]
    while w > largura - 100 and font_size > 10:
        font_size -= 2
        font = ImageFont.truetype(font_path, font_size)
        bbox = draw.textbbox((0,0), texto, font=font)
        w = bbox[2] - bbox[0]

    # Centralizar o texto
    h = bbox[3] - bbox[1]
    x = (largura - w) / 2
    y = (altura - h) / 2

    draw.text((x, y), texto, font=font, fill="black")
    return imagem

# --- FUNÇÃO PARA POSTAR NO INSTAGRAM ---
def post_instagram(cl: Client, texto):
    imagem = create_image_with_text(texto)
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = os.path.join(IMAGE_DIR, f"{timestamp}.jpg")
    imagem.save(file_path)
    cl.photo_upload(file_path, caption=texto)
    print(f"✅ Postado: {texto} - Horário: {datetime.datetime.now()}")

# --- LOGIN NO INSTAGRAM ---
cl = Client()
if os.path.exists(SESSION_FILE):
    cl.load_settings(SESSION_FILE)
    cl.login(USERNAME, PASSWORD)
else:
    cl.login(USERNAME, PASSWORD)
    cl.dump_settings(SESSION_FILE)

# --- LISTA DE POSTS ---
posts = [
    "Anime recomendado 1",
    "Anime recomendado 2",
    "Anime recomendado 3",
    # Adicione mais posts aqui
]

# --- LOOP DE POSTAGEM ---
while True:
    for texto in posts:
        start_time = time.time()
        try:
            post_instagram(cl, texto)
        except Exception as e:
            print(f"❌ Erro no job: {e}")
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"⏱ Tempo do post: {elapsed:.2f}s")
        time.sleep(POST_INTERVAL)
