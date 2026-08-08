import os
import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor


# Scraper de páginas a HTML estático limpio con imágenes locales.

# USO:           |  python scraper.py
# REQUISITOS:    |  pip install requests beautifulsoup4 lxml                    |
# SALIDA:        |  pages/<slug>.html      HTML limpio con <head> + meta tags   |
# (OUTPUT_DIR)   |  public/<slug>/<img>    Imágenes descargadas en paralelo     |
  
# ------------------------
# Configuración
# ------------------------

# Carpeta donde está este archivo .py (la base para las rutas relativas).
BASE_DIR = Path(__file__).parent

# Carpeta de salida.
# "scraped"         → utils/scraped/
# "public/scraped"  → utils/public/scraped/
# "../output"       → output/ (fuera de utils/)
OUTPUT_DIR = "scraped"

# Ruta completa armada automáticamente (no editar).
OUTPUT_PATH = BASE_DIR / OUTPUT_DIR

# Subcarpetas dentro de OUTPUT_DIR
PAGES_SUBDIR = "pages"
PUBLIC_SUBDIR = "public"


URLS = [
    "https://mediabrosonline.com/new/agencia-marketing-digital-4",
]

BASE_PATH = "/"  # Path base a quitar al generar el slug



# ------------------------
# Helpers
# ------------------------

def slugify(url):
    parsed = urlparse(url)
    path = parsed.path

    # quitar base path
    if path.startswith(BASE_PATH):
        path = path[len(BASE_PATH):]

    path = path.strip("/")

    if path == "":
        return "index"

    slug = re.sub(r'[^a-zA-Z0-9]+', '-', path).strip('-')
    return slug or "page"


def clean_html(soup):
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # atributos permitidos
    allowed_attrs = {
        "id",
        "href",
        "src",
        "alt",
        "title",
        "target",
        "rel",
        "content",   # meta
        "property",  # og
        "name"
    }

    for tag in soup.find_all(True):
        attrs = dict(tag.attrs)
        for attr in attrs:
            if attr not in allowed_attrs:
                del tag.attrs[attr]

    return soup


def extract_meta(soup):
    data = {}

    data["title"] = soup.title.string if soup.title else ""

    desc = soup.find("meta", attrs={"name": "description"})
    data["description"] = desc["content"] if desc and "content" in desc.attrs else ""

    og_tags = soup.find_all("meta", property=re.compile("^og:"))
    for tag in og_tags:
        if "content" in tag.attrs:
            data[tag["property"]] = tag["content"]

    return data


# ------------------------
# Imágenes (paralelo)
# ------------------------

def download_image(img_url, filepath):
    try:
        r = requests.get(img_url, timeout=5)
        if r.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(r.content)
    except:
        pass


def download_images(soup, base_url, slug, public_dir):
    folder = os.path.join(public_dir, slug)
    os.makedirs(folder, exist_ok=True)

    with ThreadPoolExecutor(max_workers=6) as executor:
        for img in soup.find_all("img"):
            src = (
                img.get("src") or
                img.get("data-src") or
                img.get("data-lazy-src") or
                img.get("data-original")
            )
            if not src:
                continue

            if any(x in src.lower() for x in ["icon", "logo", "svg"]):
                continue

            img_url = urljoin(base_url, src)
            filename = os.path.basename(urlparse(img_url).path)

            if not filename:
                filename = "image.jpg"

            filepath = os.path.join(folder, filename)

            executor.submit(download_image, img_url, filepath)

            # URL pública: con default (raíz del proyecto) las imágenes en
            # public/<slug>/<file> se sirven en /<slug>/<file> en Astro
            img["src"] = f"/{slug}/{filename}"


# ------------------------
# Procesamiento
# ------------------------

def process_url(url, pages_dir, public_dir):
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "lxml")

    slug = slugify(url)

    meta = extract_meta(soup)

    download_images(soup, url, slug, public_dir)

    soup = clean_html(soup)

    final_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{meta.get("title", "")}</title>
<meta name="description" content="{meta.get("description", "")}">
"""

    for k, v in meta.items():
        if k.startswith("og:"):
            final_html += f'<meta property="{k}" content="{v}">\n'

    final_html += "</head>\n<body>\n"
    final_html += str(soup.body) if soup.body else str(soup)
    final_html += "\n</body>\n</html>"

    os.makedirs(pages_dir, exist_ok=True)

    filepath = os.path.join(pages_dir, f"{slug}.html")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"✔ Guardado: {filepath}\n")


# ------------------------
# Main
# ------------------------

def main():
    pages_dir = os.path.join(OUTPUT_PATH, PAGES_SUBDIR)
    public_dir = os.path.join(OUTPUT_PATH, PUBLIC_SUBDIR)

    print(f"📁 Carpeta de salida: {OUTPUT_PATH}")
    print(f"   pages/  → {pages_dir}")
    print(f"   public/ → {public_dir}\n")

    total = len(URLS)
    for i, url in enumerate(URLS, 1):
        print(f"[{i}/{total}] {url}")
        try:
            process_url(url, pages_dir, public_dir)
        except Exception as e:
            print(f"  ✘ Error: {e}")


if __name__ == "__main__":
    main()