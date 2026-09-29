import os
import random
import datetime
import requests

UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
UNSPLASH_API = f"https://api.unsplash.com/photos/random?topics=wallpapers&orientation=landscape&client_id={UNSPLASH_KEY}"
BING_API = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=de-DE"
WALLHAVEN_API = "https://wallhaven.cc/api/v1/search?categories=100&purity=100&sorting=date_added&order=desc"
PEAPIX_API = "https://peapix.com/spotlight/feed?country=us"

HEADERS = { 
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36" 
}

def fetch_all_wallpapers():
    today = datetime.date.today().strftime("%d %B %Y")
    images_dir = os.path.join(os.getcwd(), "images")
    os.makedirs(images_dir, exist_ok=True)

    # Bing
    bing_data = {}
    try:
        res = requests.get(BING_API, headers=HEADERS, timeout=15)
        res.raise_for_status()
        data = res.json()["images"][0]
        img_bytes = requests.get("https://www.bing.com" + data["url"], headers=HEADERS, timeout=30).content
        
        with open(os.path.join(images_dir, "bing.jpg"), "wb") as f:
            f.write(img_bytes)
        with open(os.path.join(images_dir, "latest.jpg"), "wb") as f:
            f.write(img_bytes)
            
        bing_data = {
            "title": data.get("title", "Bing Wallpaper"),
            "copyright": data.get("copyright", "Bing")
        }
        print("Bing added!")
    except Exception as e:
        print(f"Error Bing: {e}")

    # Unsplash
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
            print("Unsplash added!")
        except Exception as e:
            print(f"Error Unsplash: {e}")

    # Wallhaven
    wallhaven_data = {}
    try:
        res = requests.get(WALLHAVEN_API, headers=HEADERS, timeout=15)
        res.raise_for_status()
        items = res.json().get("data", [])
        if items:
            latest_bg = items[0]
            img_url = latest_bg["path"]
            img_bytes = requests.get(img_url, headers=HEADERS, timeout=30).content
            
            with open(os.path.join(images_dir, "wallhaven.jpg"), "wb") as f:
                f.write(img_bytes)
                
            wallhaven_data = {
                "title": f"Wallhaven Wallpaper #{latest_bg['id']}",
                "url": latest_bg["url"],
                "resolution": latest_bg["resolution"]
            }
            print("Wallhaven added!")
    except Exception as e:
        print(f"Error Wallhaven: {e}")

    # Peapix Windows Spotlight
    peapix_data = {}
    try:
        res = requests.get(PEAPIX_API, headers=HEADERS, timeout=15)
        res.raise_for_status()
        items = res.json()
        if items:
            today_item = items[0]
            img_url = today_item.get("imageUrl") or today_item.get("fullUrl")
            img_bytes = requests.get(img_url, headers=HEADERS, timeout=30).content
            
            with open(os.path.join(images_dir, "peapix.jpg"), "wb") as f:
                f.write(img_bytes)
                
            peapix_data = {
                "title": today_item.get("title", "Windows Spotlight Wallpaper"),
                "copyright": today_item.get("copyright", "Microsoft Spotlight")
            }
            print("Peapix added!")
    except Exception as e:
        print(f"Error Peapix: {e}")
        
    readme_content = f"# Daily Wallpaper Storage\n\n"

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

    if wallhaven_data:
        readme_content += f"""## 3. Wallhaven (`wallhaven.jpg`)
![Wallhaven](images/wallhaven.jpg)
* **Заголовок:** [{wallhaven_data['title']}]({wallhaven_data['url']})
* **Разрешение:** {wallhaven_data['resolution']}
* **Дата:** {today}

---
"""

    if peapix_data:
        readme_content += f"""## 4. Windows Spotlight via Peapix (`peapix.jpg`)
![Peapix](images/peapix.jpg)
* **Заголовок:** {peapix_data['title']}
* **Описание:** {peapix_data['copyright']}
* **Дата:** {today}
"""

    with open(os.path.join(os.getcwd(), "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

if __name__ == "__main__":
    fetch_all_wallpapers()
