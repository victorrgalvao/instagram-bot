import os
import time
from datetime import datetime
from instagrapi import Client
from PIL import Image, ImageDraw, ImageFont
import schedule

# --- CONFIGURAÇÕES ---
USERNAME = "seu_usuario"      # coloque aqui seu usuário do Instagram
PASSWORD = "sua_senha"        # coloque aqui sua senha
SESSION_FILE = "session.json"
IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)

# --- FUNÇÃO PARA CRIAR IMAGEM ---
def create_image_with_time(text="Novo Post!"):
    img = Image.new('RGB', (1080, 1080), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = ImageFont.truetype(font_path, 80)
    
    # Centralizar o texto
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((1080 - w)/2, (1080 - h)/2), text, fill="white", font=font)
    
    # Tempo embaixo
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    font_time = ImageFont.truetype(font_path, 40)
    draw.text((20, 1000), now, fill="lightblue", font=font_time)
    
    file_path = os.path.join(IMAGE_DIR, f"post_{int(time.time())}.png")
    img.save(file_path)
    return file_path, now

# --- FUNÇÃO PARA POSTAR NO INSTAGRAM ---
def post_instagram():
    cl = Client()
    if os.path.exists(SESSION_FILE):
        cl.load_settings(SESSION_FILE)
    cl.login(USERNAME, PASSWORD)
    cl.dump_settings(SESSION_FILE)
    
    file_path, now = create_image_with_time()
    caption = f"Novo post automático! 🕒 {now} #anime #instapost #recomendacao"
    cl.photo_upload(file_path, caption)
    print(f"Post feito às {now}")

# --- AGENDAMENTO ---
# Postar a cada 6 horas
schedule.every(6).hours.do(post_instagram)

print("Bot iniciado. Postando a cada 6 horas...")

while True:
    schedule.run_pending()
    time.sleep(1)
