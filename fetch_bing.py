import os
import datetime
import requests

NATGEO_API = "https://www.nationalgeographic.com/photography/photo-of-the-day/_jcr_content/.gallery.json"

def fetch_natgeo_wallpaper():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    # 1. Запрос к API National Geographic
    res = requests.get(NATGEO_API, headers=headers, timeout=15)
    res.raise_for_status()
    data = res.json()

    # Извлекаем данные первого (сегодняшнего) фото
    item = data["items"][0]
    
    # Ссылка на изображение в хорошем качестве
    img_url = item["originalUrl"]
    title = item["title"]
    # Очищаем подпись от HTML-тегов, если они есть
    caption = item.get("caption", "").replace("<p>", "").replace("</p>", "").strip()
    author = item.get("credit", "National Geographic")
    today = datetime.date.today().isoformat()

    # 2. Скачивание изображения
    images_dir = os.path.join(os.getcwd(), "images")
    os.makedirs(images_dir, exist_ok=True)

    img_bytes = requests.get(img_url, headers=headers, timeout=30).content

    # Сохраняем в latest.jpg и natgeo.jpg
    with open(os.path.join(images_dir, "latest.jpg"), "wb") as f:
        f.write(img_bytes)

    with open(os.path.join(images_dir, "natgeo.jpg"), "wb") as f:
        f.write(img_bytes)

    # 3. Обновление README.md
    readme_content = f"""# Daily Wallpaper Storage

## 1. Latest Wallpaper (`latest.jpg`)
![Latest Wallpaper](images/latest.jpg)

* **Заголовок:** {title}
* **Описание:** {caption}
* **Дата:** {today}
* **Автор:** {author}

---

## 2. National Geographic Archive (`natgeo.jpg`)
![NatGeo Wallpaper](images/natgeo.jpg)

* **Заголовок:** {title}
* **Описание:** {caption}
* **Дата:** {today}
* **Автор:** {author}
"""
    with open(os.path.join(os.getcwd(), "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

if __name__ == "__main__":
    fetch_natgeo_wallpaper()
