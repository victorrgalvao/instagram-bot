import os
import time
import random
import requests
from instagrapi import Client
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# --- CONFIGURAÇÕES VIA VARIÁVEIS DE AMBIENTE ---
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
SESSION_FILE = "session.json"
IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)

# --- LOGIN ---
cl = Client()
if os.path.exists(SESSION_FILE):
    cl.load_settings(SESSION_FILE)

try:
    cl.login(USERNAME, PASSWORD)
except:
    cl.set_settings({})
    cl.login(USERNAME, PASSWORD)
    cl.dump_settings(SESSION_FILE)

# --- FUNÇÃO PARA PEGAR ANIME ALEATÓRIO ---
def get_random_anime():
    url = "https://api.jikan.moe/v4/anime"
    params = {"page": random.randint(1, 100), "limit": 1}
    response = requests.get(url, params=params).json()
    anime = response["data"][0]
    return anime

# --- CRIAR POSTER ESTILO POLAROID ---
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
    try:
        font_title_bold = ImageFont.truetype("arialbd.ttf", 90)
        font_info = ImageFont.truetype("arial.ttf", 40)
        font_info_bold = ImageFont.truetype("arialbd.ttf", 40)
    except IOError:
        font_title_bold = ImageFont.load_default()
        font_info = ImageFont.load_default()
        font_info_bold = ImageFont.load_default()

    text_start_y = IMAGE_HEIGHT + (CARD_PADDING * 1.5)
    padding_x = CARD_PADDING

    # Ajuste responsivo do título
    max_title_width = IMAGE_WIDTH
    if year:
        max_title_width -= (font_info.getlength(str(year)) + 20)
    title_font_size = 90
    font_title_bold = ImageFont.truetype("arialbd.ttf", title_font_size)
    while font_title_bold.getlength(title.upper()) > max_title_width:
        title_font_size -= 5
        if title_font_size <= 40:
            break
        font_title_bold = ImageFont.truetype("arialbd.ttf", title_font_size)

    draw.text((padding_x, text_start_y), title.upper(), font=font_title_bold, fill=text_color)
    if year:
        draw.text(
            (padding_x + font_title_bold.getlength(title.upper()) + 20, text_start_y + font_title_bold.size - font_info.size - 5),
            str(year), font=font_info, fill=text_color
        )

    y_pos = text_start_y + font_title_bold.size + 40
    draw.text((padding_x, y_pos), "genre", font=font_info_bold, fill=text_color)
    draw.text((padding_x + 160, y_pos), ", ".join(genres), font=font_info, fill=text_color)

    y_pos += font_info.size + 20
    draw.text((padding_x, y_pos), "directed by", font=font_info_bold, fill=text_color)
    draw.text((padding_x + 240, y_pos), director, font=font_info, fill=text_color)

    clean_title = "".join([c if c.isalnum() else "_" for c in title])[:30]
    path = os.path.join(IMAGE_DIR, f"{clean_title}_{int(time.time())}.jpg")
    polaroid_card.save(path, "JPEG")
    return path, title, score

# --- CRIAR HASHTAGS ---
def create_hashtags(title):
    keywords = [
        "anime", "otaku", "manga", "japan", "weeb", "animes", "cosplay",
        "otakulife", "animesbr", "instaanime", "animelover"
    ]
    title_clean = title.replace(" ", "").replace("-", "").replace(":", "")
    hashtags = [f"#{title_clean}", f"#{title_clean}Anime"] + [f"#{k}" for k in random.sample(keywords, 6)]
    return " ".join(hashtags)

# --- EXECUTAR POST ---
def job():
    anime = get_random_anime()
    path, title, score = create_poster(anime)
    hashtags = create_hashtags(title)
    caption = f"{title}\n⭐ Nota: {score}\n\n{hashtags}"
    cl.photo_upload(path, caption)
    print(f"✅ Postado: {title}")

# --- RODAR O JOB ---
if __name__ == "__main__":
    job()
