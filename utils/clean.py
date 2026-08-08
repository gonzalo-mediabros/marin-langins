#!/usr/bin/env python3
"""
HTML Cleanup Script for Scraper Pages

Removes <header> and <footer>, unwraps single-child divs recursively,
removes empty spans, and strips class/id/style attributes.
"""

import os
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

# Carpeta donde está este archivo .py (la base para las rutas relativas).
BASE_DIR = Path(__file__).parent

# Carpeta de entrada (de donde lee los HTML).
INPUT_DIR = "pages"

# Carpeta de salida.
# "pages-clean"     → utils/pages-clean/
# "../output"       → output/ (fuera de utils/)
OUTPUT_DIR = "pages-clean"

# Rutas completas armadas automáticamente (no editar).
INPUT_PATH = BASE_DIR / INPUT_DIR
OUTPUT_PATH = BASE_DIR / OUTPUT_DIR

def unwrap_single_child_divs(element):
    """
    Recursively unwrap divs that have exactly one child element.
    Ignores whitespace-only text nodes.
    """
    if not hasattr(element, 'children'):
        return

    # First, recurse into children
    for child in list(element.children):
        if hasattr(child, 'name') and child.name:
            unwrap_single_child_divs(child)

    # Then check if this element should be unwrapped
    if element.name == 'div':
        # Count non-whitespace children elements (not text nodes)
        element_children = [c for c in element.children if hasattr(c, 'name') and c.name]

        if len(element_children) == 1:
            # Unwrap: move child up and remove this div
            child = element_children[0]
            element.replace_with(child)
            # Recurse on the newly exposed element
            unwrap_single_child_divs(child)

def remove_empty_spans(element):
    """
    Remove <span> elements that are empty or contain only whitespace.
    """
    for span in element.find_all('span'):
        # Check if span has no text content and no semantic children
        text_content = span.get_text(strip=True)
        has_semantic_children = any(
            child.name for child in span.children
            if hasattr(child, 'name')
        )

        if not text_content and not has_semantic_children:
            span.decompose()

def strip_attributes(element):
    """
    Remove class, id, and style attributes from all elements.
    Preserves src, href, alt, and other semantic attributes.
    """
    attrs_to_remove = {'class', 'id', 'style'}

    for tag in element.find_all(True):  # True = find all tags
        for attr in attrs_to_remove:
            if attr in tag.attrs:
                del tag.attrs[attr]

def clean_html_file(input_path, output_path):
    """
    Clean a single HTML file:
    1. Parse HTML
    2. Remove <header> and <footer>
    3. Unwrap single-child divs recursively
    4. Remove empty spans
    5. Strip class/id/style attributes
    6. Write cleaned HTML
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove <header> and <footer> completely
    for tag in soup.find_all(['header', 'footer']):
        tag.decompose()

    # Unwrap single-child divs recursively
    unwrap_single_child_divs(soup)

    # Remove empty spans
    remove_empty_spans(soup)

    # Strip class, id, style attributes
    strip_attributes(soup)

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))

def main():
    # Create output directory if it doesn't exist
    OUTPUT_PATH.mkdir(exist_ok=True)

    if not INPUT_PATH.exists():
        print(f"Error: Input directory {INPUT_PATH} does not exist")
        return

    # Process each HTML file
    html_files = sorted(INPUT_PATH.glob('*.html'))

    if not html_files:
        print(f"No HTML files found in {INPUT_PATH}")
        return

    print(f"Found {len(html_files)} HTML files. Starting cleanup...\n")

    total = len(html_files)
    for i, html_file in enumerate(html_files, 1):
        output_file = OUTPUT_PATH / html_file.name
        try:
            clean_html_file(html_file, output_file)
            print(f"[{i}/{total}] ✔ {html_file.name}")
        except Exception as e:
            print(f"[{i}/{total}] ✘ {html_file.name}: {e}")

    print()
    print(f"Cleanup complete. Output files written to {OUTPUT_PATH}")

if __name__ == '__main__':
    main()
