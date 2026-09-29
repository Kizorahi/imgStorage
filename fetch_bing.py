import os
import datetime
import requests

UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
UNSPLASH_API = f"https://api.unsplash.com/photos/random?topics=wallpapers&orientation=landscape&client_id={UNSPLASH_KEY}"
BING_API = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=de-DE"
REDDIT_API = "https://www.reddit.com/r/wallpapers/top.json?limit=10&t=day"

HEADERS = { 
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36" 
}
# Reddit требует уникальный/понятный User-Agent, чтобы не выдавать 429/403
REDDIT_HEADERS = { 
    "User-Agent": "python:unDaily.wallpaper.fetcher:v1.0 (by /u/github_actions)" 
}

def fetch_all_wallpapers():
    today = datetime.date.today().isoformat()
    images_dir = os.path.join(os.getcwd(), "images")
    os.makedirs(images_dir, exist_ok=True)

    # 1. Bing
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

    # 2. Unsplash
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

    # 3. Reddit (r/wallpapers)
    reddit_data = {}
    try:
        res = requests.get(REDDIT_API, headers=REDDIT_HEADERS, timeout=15)
        res.raise_for_status()
        posts = res.json()["data"]["children"]

        # Ищем первый пост из топа, где прямая ссылка на изображение
        for post in posts:
            post_data = post["data"]
            url = post_data.get("url", "")
            if url.endswith((".jpg", ".jpeg", ".png")):
                img_bytes = requests.get(url, headers=HEADERS, timeout=30).content
                
                with open(os.path.join(images_dir, "reddit.jpg"), "wb") as f:
                    f.write(img_bytes)
                
                reddit_data = {
                    "title": post_data.get("title", "Reddit Wallpaper"),
                    "author": f"[{post_data.get('author', 'reddit')}](" + f"https://reddit.com/user/{post_data.get('author')}" + ")",
                    "permalink": "https://reddit.com" + post_data.get("permalink", "")
                }
                print("Reddit added!")
                break
    except Exception as e:
        print(f"Error Reddit: {e}")

    # Генерация README.md
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

    if reddit_data:
        readme_content += f"""## 3. Reddit r/wallpapers (`reddit.jpg`)
![Reddit](images/reddit.jpg)
* **Заголовок:** [{reddit_data['title']}]({reddit_data['permalink']})
* **Автор:** {reddit_data['author']}
* **Дата:** {today}
"""

    with open(os.path.join(os.getcwd(), "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

if __name__ == "__main__":
    fetch_all_wallpapers()
