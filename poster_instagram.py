import os
import time
import random
from datetime import datetime
from instagrapi import Client
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURAÇÕES ---
USERNAME = "recomendanimes2"   # seu usuário do Instagram
PASSWORD = "215507mrg"         # sua senha
SESSION_FILE = "session.json"
IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)

# --- AUTENTICAÇÃO INSTAGRAM ---
cl = Client()
if os.path.exists(SESSION_FILE):
    cl.load_settings(SESSION_FILE)
cl.login(USERNAME, PASSWORD)
cl.dump_settings(SESSION_FILE)

# --- FUNÇÃO PARA CRIAR IMAGEM COM HORA ---
def create_image_with_time(text="Novo Post!"):
    img = Image.new('RGB', (1080, 1080), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = ImageFont.truetype(font_path, 80)
    
    # Texto centralizado
    w, h = draw.textsize(text, font=font)
    draw.text(((1080-w)/2, (1080-h)/2), text, fill="white", font=font)
    
    # Tempo embaixo
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    font_time = ImageFont.truetype(font_path, 40)
    draw.text((20, 1000), now, fill="lightblue", font=font_time)
    
    file_path = os.path.join(IMAGE_DIR, f"post_{int(time.time())}.png")
    img.save(file_path)
    return file_path, now

# --- GERAR HASHTAGS ---
def generate_hashtags():
    tags = ["#anime", "#otaku", "#manga", "#animebrasil", "#animes"]
    return " ".join(random.sample(tags, 3))

# --- POSTAR NO INSTAGRAM ---
def post_instagram():
    file_path, now = create_image_with_time()
    caption = f"Post automático 🚀\n{now}\n{generate_hashtags()}"
    cl.photo_upload(file_path, caption=caption)
    print(f"[{now}] Post feito com sucesso: {file_path}")

# --- LOOP PRINCIPAL ---
POST_INTERVAL_HOURS = 6
POST_INTERVAL_SECONDS = POST_INTERVAL_HOURS * 3600

while True:
    start_time = time.time()
    post_instagram()
    
    # Log a cada segundo enquanto espera próximo post
    for elapsed in range(POST_INTERVAL_SECONDS):
        print(f"Tempo desde último post: {elapsed} s", end="\r")
        time.sleep(1)
