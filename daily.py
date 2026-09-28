import os
import datetime
import requests

# Официальный API Bing
BING_API = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
BASE_URL = "https://www.bing.com"

def fetch_bing_wallpaper():
    # 1. Получаем данные от Bing
    response = requests.get(BING_API)
    response.raise_for_status()
    data = response.json()
    
    image_data = data["images"][0]
    img_url = BASE_URL + image_data["url"]
    title = image_data.get("title", "Bing Wallpaper")
    copyright_text = image_data.get("copyright", "")
    
    # Имя файла на основе даты (например, 2026-09-28.jpg)
    today = datetime.date.today().isoformat()
    filename = f"{today}.jpg"
    
    # 2. Создаем папку images, если её нет
    os.makedirs("images", exist_ok=True)
    filepath = os.path.join("images", filename)
    
    # 3. Скачиваем саму картинку
    img_response = requests.get(img_url)
    img_response.raise_for_status()
    with open(filepath, "wb") as f:
        f.write(img_response.content)
        
    print(f"Загружено изображение: {filepath}")
    
    # 4. Обновляем README.md
    update_readme(filepath, title, copyright_text, today)

def update_readme(img_path, title, copyright_text, date):
    readme_content = f"""# Bing Daily Wallpaper

![{title}]({img_path})

### {title}
**Дата:** {date}  
**Описание:** {copyright_text}

---
*Автоматически обновлено с помощью GitHub Actions.*
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

if __name__ == "__main__":
    fetch_bing_wallpaper()
