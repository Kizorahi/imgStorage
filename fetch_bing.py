import os
import datetime
import requests

BING_API = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
BASE_URL = "https://www.bing.com"

def fetch_bing_wallpaper():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    res = requests.get(BING_API, headers=headers, timeout=15)
    res.raise_for_status()
    data = res.json()
    
    image_data = data["images"][0]
    img_url = BASE_URL + image_data["url"]
    title = image_data.get("title", "Bing Wallpaper")
    copyright_text = image_data.get("copyright", "")
    
    today = datetime.date.today().isoformat()
    filename = f"{today}.jpg"

    images_dir = os.path.join(os.getcwd(), "images")
    os.makedirs(images_dir, exist_ok=True)
    
    filepath = os.path.join(images_dir, filename)
    latest_filepath = os.path.join(images_dir, "latest.jpg")
    rel_path = f"images/{filename}"

    img_res = requests.get(img_url, headers=headers, timeout=30)
    img_res.raise_for_status()

    with open(filepath, "wb") as f:
        f.write(img_res.content)

    with open(latest_filepath, "wb") as f:
        f.write(img_res.content)
        
    print(f"Изображение успешно сохранено: {filepath}")
    print(f"Постоянная копия обновлена: {latest_filepath}")

    update_readme(rel_path, title, copyright_text, today)

def update_readme(rel_path, title, copyright_text, date):
    readme_path = os.path.join(os.getcwd(), "README.md")
    readme_content = f"""# Bing Daily Wallpaper

![{title}]({rel_path})

### {title}
**Дата:** {date}  
**Описание:** {copyright_text}
"""
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

if __name__ == "__main__":
    fetch_bing_wallpaper()
