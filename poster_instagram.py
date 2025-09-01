import os
import time
import random
import requests
from instagrapi import Client
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import schedule
from datetime import datetime, timedelta

USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
SESSION_FILE = "session.json"
IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)

cl = Client()
if os.path.exists(SESSION_FILE):
    cl.load_settings(SESSION_FILE)

try:
    cl.login(USERNAME, PASSWORD)
except:
    cl.set_settings({})
    cl.login(USERNAME, PASSWORD)
    cl.dump_settings(SESSION_FILE)

def get_random_anime():
    url = "https://api.jikan.moe/v4/anime"
    params = {"page": random.randint(1, 100), "limit": 1}
    response = requests.get(url, params=params).json()
    return response["data"][0]

def create_poster(anime):
    title = anime["title"]
    score = anime.get("score", "N/A")
    image_url = anime["images"]["jpg"]["large_image_url"]
    genres = [g['name'] for g in anime.get('genres', [])]
    director = anime.get('producers', [{}])[0].get('name', 'N/A')
    year = anime.get('year')

    img_data = requests.get(image_url).content
    anime_img = Image.open(BytesIO(img_data)).convert("RGB")

    POLAROID_WIDTH = 1080
    POLAROID_HEIGHT = 1350
    POLAROID_BG_COLOR = (239, 239, 239)
    CARD_PADDING = 80
    IMAGE_WIDTH = POLAROID_WIDTH - (CARD_PADDING * 2)
    IMAGE_HEIGHT = int(POLAROID_HEIGHT * 0.6)
    anime_img = anime_img.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.LANCZOS)
    polaroid_card = Image.new("RGB", (POLAROID_WIDTH, POLAROID_HEIGHT), POLAROID_BG_COLOR)
    polaroid_card.paste(anime_img, (CARD_PADDING, CARD_PADDING))

    draw = ImageDraw.Draw(polaroid_card)
    text_color = (0, 0, 0)

    font_path_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_path_regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    font_info = ImageFont.truetype(font_path_regular, 40)
    font_info_bold = ImageFont.truetype(font_path_bold, 40)

    # --- Novo bloco: texto centralizado com sombra e título responsivo ---
    text_start_y = IMAGE_HEIGHT + CARD_PADDING
    card_center = POLAROID_WIDTH // 2

    def draw_text_centered(draw, text, y, font, color=(0,0,0), shadow=True):
        text_width, text_height = draw.textsize(text, font=font)
        x = card_center - text_width // 2
        if shadow:
            draw.text((x+2, y+2), text, font=font, fill=(150,150,150))  # sombra
        draw.text((x, y), text, font=font, fill=color)

    # Título grande, responsivo
    title_font_size = 90
    font_title = ImageFont.truetype(font_path_bold, title_font_size)
    max_title_width = IMAGE_WIDTH
    while font_title.getlength(title) > max_title_width and title_font_size > 40:
        title_font_size -= 5
        font_title = ImageFont.truetype(font_path_bold, title_font_size)

    draw_text_centered(draw, title, text_start_y, font_title)

    # Informações (ano, gênero e diretor)
    info_y = text_start_y + font_title.size + 20
    if year:
        draw_text_centered(draw, f"Year: {year}", info_y, font_info)
        info_y += font_info.size + 10
    draw_text_centered(draw, f"Genre: {', '.join(genres)}", info_y, font_info_bold)
    info_y += font_info_bold.size + 10
    draw_text_centered(draw, f"Directed by: {director}", info_y, font_info_bold)
    # --- Fim do bloco novo ---

    clean_title = "".join([c if c.isalnum() else "_" for c in title])[:30]
    path = os.path.join(IMAGE_DIR, f"{clean_title}_{int(time.time())}.jpg")
    polaroid_card.save(path, "JPEG")
    return path, title, score

def create_hashtags(title):
    keywords = ["anime","otaku","manga","japan","weeb","animes","cosplay",
                "otakulife","animesbr","instaanime","animelover"]
    title_clean = title.replace(" ", "").replace("-", "").replace(":", "")
    hashtags = [f"#{title_clean}", f"#{title_clean}Anime"] + [f"#{k}" for k in random.sample(keywords, 6)]
    return " ".join(hashtags)

def job():
    try:
        anime = get_random_anime()
        path, title, score = create_poster(anime)
        hashtags = create_hashtags(title)
        caption = f"{title}\n⭐ Nota: {score}\n\n{hashtags}"
        cl.photo_upload(path, caption)
        print(f"✅ Postado: {title} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"❌ Erro no job: {e}")

# --- AGENDAR JOB A CADA 6 HORAS ---
schedule.every(6).hours.do(job)

print(f"🕒 Script iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
job()  # primeira execução imediata

while True:
    schedule.run_pending()
    if schedule.get_jobs():
        next_run = schedule.get_jobs()[0].next_run
        remaining = next_run - datetime.now()
        total_seconds = int(remaining.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"🕒 Próximo post em: {hours:02d}h {minutes:02d}m {seconds:02d}s", end='\r')
    time.sleep(1)
