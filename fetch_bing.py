import os
import datetime
import requests

UNSPLASH_KEY = os.environ.get("UNDAILY")
API_URL = f"https://api.unsplash.com/photos/random?topics=wallpapers&orientation=landscape&client_id={UNDAILY}"

def fetch_unsplash_wallpaper():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    data = requests.get(API_URL, headers=headers, timeout=15).json()
    
    img_url = data["urls"]["full"]
    title = data.get("alt_description") or "Unsplash Wallpaper"
    author_name = data["user"]["name"]
    author_link = data["user"]["links"]["html"]
    today = datetime.date.today().isoformat()

    images_dir = os.path.join(os.getcwd(), "images")
    os.makedirs(images_dir, exist_ok=True)

    img_bytes = requests.get(img_url, headers=headers, timeout=30).content

    with open(os.path.join(images_dir, "latest.jpg"), "wb") as f:
        f.write(img_bytes)

    with open(os.path.join(images_dir, "unsplash.jpg"), "wb") as f:
        f.write(img_bytes)

    readme_content = f"""# Daily Unsplash Wallpaper

![{title}](images/latest.jpg)

### {title.capitalize()}
**Дата:** {today}  
**Автор:** [{author_name}]({author_link})
"""
    with open(os.path.join(os.getcwd(), "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

if __name__ == "__main__":
    fetch_unsplash_wallpaper()
