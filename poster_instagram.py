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

    max_title_width = IMAGE_WIDTH
    title_font_size = 90
    font_title = ImageFont.truetype(font_path_bold, title_font_size)
    while font_title.getlength(title) > max_title_width and title_font_size > 40:
        title_font_size -= 5
        font_title = ImageFont.truetype(font_path_bold, title_font_size)

    font_info = ImageFont.truetype(font_path_regular, 40)
    font_info_bold = ImageFont.truetype(font_path_bold, 40)

    text_start_y = IMAGE_HEIGHT + (CARD_PADDING * 1.5)
    padding_x = CARD_PADDING

    draw.text((padding_x, text_start_y), title, font=font_title, fill=text_color)
    if year:
        draw.text((padding_x + font_title.getlength(title) + 20,
                   text_start_y + font_title.size - font_info.size),
                  str(year), font=font_info, fill=text_color)

    y_pos = text_start_y + font_title.size + 30
    draw.text((padding_x, y_pos), "genre:", font=font_info_bold, fill=text_color)
    draw.text((padding_x + 160, y_pos), ", ".join(genres), font=font_info, fill=text_color)

    y_pos += font_info.size + 20
    draw.text((padding_x, y_pos), "directed by:", font=font_info_bold, fill=text_color)
    draw.text((padding_x + 240, y_pos), director, font=font_info, fill=text_color)

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
