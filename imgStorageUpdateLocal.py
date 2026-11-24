import os
import random
import datetime
import shutil

BASE_DIR = os.path.join(os.getcwd(), "images", "K-on!")
HISTORY_FILE = os.path.join(BASE_DIR, "history.txt")
OUTPUT_IMAGE = os.path.join(os.getcwd(), "images", "k-on.jpg")
README_FILE = os.path.join(os.getcwd(), "README.md")

RESERVE_LIMIT = 360

SECTION_HEADER = "## 6. K-on! (`k-on.jpg`)\n"


def collect_images():
    exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    found = []
    if not os.path.isdir(BASE_DIR):
        return found

    for entry in os.listdir(BASE_DIR):
        sub = os.path.join(BASE_DIR, entry)
        if not os.path.isdir(sub):
            continue
        for f in os.listdir(sub):
            path = os.path.join(sub, f)
            if os.path.isfile(path) and os.path.splitext(f)[1].lower() in exts:
                found.append(os.path.relpath(path, BASE_DIR))
    return found


def load_history():
    if not os.path.isfile(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def save_history(history):
    history = history[-RESERVE_LIMIT:]
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(history))


def pick_unique_image():
    all_images = collect_images()
    if not all_images:
        return None, "no images found*"

    history = load_history()

    recent = history[-RESERVE_LIMIT:]
    used = set(recent)

    available = [p for p in all_images if p not in used]

    if not available:
        if recent:
            chosen = recent[0]
            recent = recent[1:]
        else:
            chosen = random.choice(all_images)
    else:
        chosen = random.choice(available)

    recent.append(chosen)
    save_history(recent)
    return chosen, None


def copy_to_output(rel_path):
    src = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(OUTPUT_IMAGE), exist_ok=True)
    shutil.copyfile(src, OUTPUT_IMAGE)
    return OUTPUT_IMAGE


def build_section(rel_path, error=None):
    today = datetime.date.today().strftime("%d %B %Y")
    if rel_path:
        folder = os.path.dirname(rel_path) or "."
        fname = os.path.basename(rel_path)
        return (
            SECTION_HEADER
            + f"""![Local](images/k-on.jpg)
* **Файл:** `{fname}`
* **Папка:** `{folder}`
* **Дата:** {today}

---

"""
        )
    return SECTION_HEADER + f"{error}\n\n---\n\n"


def merge_into_readme(section_text):
    if os.path.isfile(README_FILE):
        with open(README_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = "# Daily Wallpaper Storage\n\n"

    if SECTION_HEADER in content:
        before, _, rest = content.partition(SECTION_HEADER)
        _, sep, after = rest.partition("---\n\n")
        if sep:
            content = before + after
        else:
            content = before

    content = content.rstrip() + "\n\n"
    content += section_text

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def fetch_local_wallpaper():
    rel_path, err = pick_unique_image()
    if err:
        print(f"Error Local: {err}")
        merge_into_readme(build_section(None, err))
        return

    copy_to_output(rel_path)
    merge_into_readme(build_section(rel_path))
    print(f"Local added: {rel_path}")


if __name__ == "__main__":
    fetch_local_wallpaper()
