import os
import datetime
import requests

UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
UNSPLASH_API = f"https://api.unsplash.com/photos/random?topics=wallpapers&orientation=landscape&client_id={UNSPLASH_KEY}"
BING_API = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=de-DE"
WALLHAVEN_API = "https://wallhaven.cc/api/v1/search?categories=100&purity=100&sorting=date_added&order=desc"
PICSUM_API = "https://picsum.photos/1920/1080"
PIXABAY_KEY = os.environ.get("PIXABAY_API_KEY")
PIXABAY_API = "https://pixabay.com/api/"

HEADERS = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36" }

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

    # Picsum
    picsum_data = {}
    try:
        res = requests.get(PICSUM_API, headers=HEADERS, timeout=30, allow_redirects=True)
        res.raise_for_status()
        content_type = res.headers.get("Content-Type", "")
        if "image" in content_type:
            with open(os.path.join(images_dir, "picsum.jpg"), "wb") as f:
                f.write(res.content)
            picsum_data = {
                "title": "Picsum Random Photo",
                "url": "https://picsum.photos/1920/1080",
                "final_url": res.url
            }
            print("Picsum added!")
        else:
            print(f"Error Picsum: unexpected content-type {content_type}")
    except Exception as e:
        print(f"Error Picsum: {e}")

    # Pixabay
    pixabay_data = {}
    if PIXABAY_KEY:
        try:
            params = {
                "key": PIXABAY_KEY,
                "q": "wallpaper",
                "image_type": "photo",
                "orientation": "horizontal",   # горизонтальные
                "per_page": 20,
                "safesearch": "true",
                "order": "latest",
            }
            res = requests.get(PIXABAY_API, params=params, headers=HEADERS, timeout=15)
            res.raise_for_status()
            hits = res.json().get("hits", [])

            target_ratio = 16 / 9
            candidates = []
            for h in hits:
                w, hh = h.get("imageWidth"), h.get("imageHeight")
                if not w or not hh:
                    continue
                ratio = w / hh
                if abs(ratio - target_ratio) <= 0.15:
                    candidates.append(h)

            if not candidates and hits:
                candidates = sorted(
                    hits,
                    key=lambda h: abs((h.get("imageWidth", 0) / max(h.get("imageHeight", 1), 1)) - target_ratio)
                )[:5]

            if candidates:
                chosen = candidates[0]
                img_url = chosen.get("largeImageURL") or chosen.get("webformatURL")
                img_bytes = requests.get(img_url, headers=HEADERS, timeout=30).content

                with open(os.path.join(images_dir, "pixabay.jpg"), "wb") as f:
                    f.write(img_bytes)

                pixabay_data = {
                    "title": (chosen.get("tags") or "Pixabay Wallpaper").capitalize(),
                    "author": f"[{chosen.get('user', 'Pixabay')}]({chosen.get('pageURL', 'https://pixabay.com')})",
                    "resolution": f"{chosen.get('imageWidth')}x{chosen.get('imageHeight')}",
                    "url": chosen.get("pageURL", "https://pixabay.com"),
                }
                print("Pixabay added!")
            else:
                print("Error Pixabay: no suitable images found")
        except Exception as e:
            print(f"Error Pixabay: {e}")

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

    if picsum_data:
        readme_content += f"""## 4. Picsum (`picsum.jpg`)
![Picsum](images/picsum.jpg)
* **Заголовок:** {picsum_data['title']}
* **Источник:** [{picsum_data['final_url']}]({picsum_data['final_url']})
* **Дата:** {today}

---
"""

    if pixabay_data:
        readme_content += f"""## 5. Pixabay (`pixabay.jpg`)
![Pixabay](images/pixabay.jpg)
* **Заголовок:** {pixabay_data['title']}
* **Разрешение:** {pixabay_data['resolution']}
* **Источник:** [{pixabay_data['url']}]({pixabay_data['url']})
* **Автор:** {pixabay_data['author']}
* **Дата:** {today}
"""

    with open(os.path.join(os.getcwd(), "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

if __name__ == "__main__":
    fetch_all_wallpapers()
