import re
import os

def process_tickers_titles(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Replace single quotes in names with double quotes
    content = re.sub(r"'([^']*)': '([^']*)'", r'"\1": "\2"', content)

    # Replace \DE\ with (DE)
    content = re.sub(r'\\([A-Z]+)\\', r'(\1)', content)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

if __name__ == "__main__":
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'tickers_titles.py'))
    process_tickers_titles(file_path)
    print(f"Processed {file_path}")