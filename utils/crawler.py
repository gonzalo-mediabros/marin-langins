import json
import os
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


# Crawler de dominios: arma un array con todas las rutas internas de un sitio.

# USO:           |  Editá START_URL y OUTPUT_DIR abajo y corré: python utils/crawler.py
# REQUISITOS:    |  pip install requests beautifulsoup4
# SALIDA:        |  JSON array con todas las URLs internas del sitio

# ==========================================
#  SETTINGS — Editá acá antes de correr
# ==========================================

# URL inicial del crawl. El crawler solo sigue links del mismo dominio.
START_URL = "https://www.marinpistachia.com"

# Carpeta donde está este archivo .py (la base para las rutas relativas).
BASE_DIR = Path(__file__).parent

# Carpeta de salida.
# "scraped"         → utils/scraped/
# "public/scraped"  → utils/public/scraped/
# "../output"       → output/ (fuera de utils/)
OUTPUT_DIR = "scraped"

# Ruta completa armada automáticamente (no editar).
OUTPUT_PATH = BASE_DIR / OUTPUT_DIR

# Cantidad máxima de páginas a visitar.
MAX_PAGES = 200

# Timeout por request (segundos).
TIMEOUT = 10

# User-Agent enviado en cada request.
USER_AGENT = "Mozilla/5.0 (compatible; DomainCrawler/1.0)"

# Extensiones de archivos que NO son páginas web (se excluyen del resultado).
SKIP_EXTENSIONS = (
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico",
    ".css", ".js", ".json", ".xml",
    ".pdf", ".zip", ".rar", ".7z",
    ".mp3", ".mp4", ".avi", ".mov",
    ".woff", ".woff2", ".ttf", ".eot",
)


# ------------------------
# Helpers
# ------------------------

def is_same_domain(url, base_domain):
    return urlparse(url).netloc == base_domain


def normalize(url):
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if parsed.query:
        base += f"?{parsed.query}"
    return base


def extract_links(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].split("#")[0].strip()
        if not href or href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        absolute = urljoin(page_url, href)
        path = urlparse(absolute).path.lower()
        if any(path.endswith(ext) for ext in SKIP_EXTENSIONS):
            continue
        links.add(absolute)

    return links


# ------------------------
# Crawl
# ------------------------

def crawl(start_url, max_pages, timeout, user_agent, progress=None):
    base_domain = urlparse(start_url).netloc
    headers = {"User-Agent": user_agent}

    visited = set()
    queue = deque([start_url])
    routes = []

    while queue and len(visited) < max_pages:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        routes.append(url)

        if progress:
            progress(url, len(routes), max_pages)

        try:
            resp = requests.get(
                url,
                timeout=timeout,
                headers=headers,
                allow_redirects=True,
            )
        except requests.RequestException:
            continue

        if "text/html" not in resp.headers.get("Content-Type", ""):
            continue

        for link in extract_links(resp.text, url):
            if not is_same_domain(link, base_domain):
                continue
            normalized = normalize(link)
            if normalized not in visited:
                queue.append(normalized)

    return routes


# ------------------------
# Main
# ------------------------

def show_progress(url, current, total):
    print(f"[{current}/{total}] {url}")


def main():
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    output_file = os.path.join(OUTPUT_PATH, "routes.json")

    print(f"🕷  Crawleando: {START_URL}")
    print(f"   max_paginas: {MAX_PAGES}")
    print(f"   salida:      {output_file}\n")

    routes = crawl(START_URL, MAX_PAGES, TIMEOUT, USER_AGENT, progress=show_progress)

    print(f"\n✔ {len(routes)} rutas guardadas en {output_file}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(routes, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
