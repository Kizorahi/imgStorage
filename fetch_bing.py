import os
import datetime
import requests

# Переменные и ссылки
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
UNSPLASH_API = f"https://api.unsplash.com/photos/random?topics=wallpapers&orientation=landscape&client_id={UNSPLASH_KEY}"
BING_API = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=de-DE"
NATGEO_API = "https://www.nationalgeographic.com/photography/photo-of-the-day/_jcr_content/.gallery.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nationalgeographic.com/photo-of-the-day"
}

def fetch_all_wallpapers():
    today = datetime.date.today().isoformat()
    images_dir = os.path.join(os.getcwd(), "images")
    os.makedirs(images_dir, exist_ok=True)

    # --- 1. Bing (основной источник для latest) ---
    bing_data = {}
    try:
        res = requests.get(BING_API, headers=HEADERS, timeout=15)
        res.raise_for_status()
        data = res.json()["images"][0]
        img_bytes = requests.get("https://www.bing.com" + data["url"], headers=HEADERS, timeout=30).content
        
        # Сохраняем в bing.jpg и дублируем в latest.jpg
        with open(os.path.join(images_dir, "bing.jpg"), "wb") as f:
            f.write(img_bytes)
        with open(os.path.join(images_dir, "latest.jpg"), "wb") as f:
            f.write(img_bytes)
            
        bing_data = {
            "title": data.get("title", "Bing Wallpaper"),
            "copyright": data.get("copyright", "Bing")
        }
    except Exception as e:
        print(f"Ошибка Bing: {e}")

    # --- 2. Unsplash ---
    unsplash_data = {}
    if UNSPLASH_KEY:
        try:
            res = requests.get(UNSPLASH_API, headers=HEADERS, timeout=15)
            res.raise_for_status()
            data = res.json()
            img_bytes = requests.get(data["urls"]["full"], headers=HEADERS, timeout=30).content
            
            with open(os.path.join(images_dir, "unsplash.jpg"), "wb") as f:
                f.write(img_bytes)
                
            unsplash_data = {
                "title": (data.get("alt_description") or "Unsplash Wallpaper").capitalize(),
                "author": f"[{data['user']['name']}]({data['user']['links']['html']})"
            }
        except Exception as e:
            print(f"Ошибка Unsplash: {e}")

    # --- 3. National Geographic ---
    natgeo_data = {}
    try:
        res = requests.get(NATGEO_API, headers=HEADERS, timeout=15)
        res.raise_for_status()
        item = res.json()["items"][0]
        img_bytes = requests.get(item["originalUrl"], headers=HEADERS, timeout=30).content
        
        with open(os.path.join(images_dir, "natgeo.jpg"), "wb") as f:
            f.write(img_bytes)
            
        caption = item.get("caption", "").replace("<p>", "").replace("</p>", "").strip()
        natgeo_data = {
            "title": item.get("title", "NatGeo Wallpaper"),
            "caption": caption,
            "author": item.get("credit", "National Geographic")
        }
    except Exception as e:
        print(f"Ошибка NatGeo: {e}")

    # --- Генерация README.md ---
    readme_content = f"# Daily Wallpaper Storage\n\n"

    # В Readme используем bing.jpg
    if bing_data:
        readme_content += f"""## 1. Bing Wallpaper (`bing.jpg`)
![Bing](images/bing.jpg)
* **Заголовок:** {bing_data['title']}
* **Описание:** {bing_data['copyright']}
* **Дата:** {today}

---
"""

    if unsplash_data:
        readme_content += f"""## 2. Unsplash (`unsplash.jpg`)
![Unsplash](images/unsplash.jpg)
* **Описание:** {unsplash_data['title']}
* **Дата:** {today}
* **Автор:** {unsplash_data['author']}

---
"""

    if natgeo_data:
        readme_content += f"""## 3. National Geographic (`natgeo.jpg`)
![NatGeo](images/natgeo.jpg)
* **Заголовок:** {natgeo_data['title']}
* **Описание:** {natgeo_data['caption']}
* **Дата:** {today}
* **Автор:** {natgeo_data['author']}
"""

    with open(os.path.join(os.getcwd(), "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

if __name__ == "__main__":
    fetch_all_wallpapers()
