import requests
import csv
import os
import sys

# Fetch API Key and CX from environment variables
API_KEY = os.environ.get("API_KEY")
CX = os.environ.get("CX")
BASE_URL = "https://www.googleapis.com/customsearch/v1"

if not API_KEY or not CX:
    raise ValueError("Missing API_KEY or CX environment variables.")

def get_google_search_titles(query, max_results=50, total_results=500):
    titles = []
    start_index = 1

    while len(titles) < total_results:
        params = {
            'key': API_KEY,
            'cx': CX,
            'q': query,
            'start': start_index,
            'num': min(10, total_results - len(titles))
        }

        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            titles.extend([item['title'] for item in items])
            start_index += 10
            if not items:
                break
        else:
            print(f"Error: {response.status_code}, {response.text}")
            break

    return titles

def save_titles_to_csv(titles, output_path):
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save titles to a CSV file
    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["GoogleSearch"])  # Add a header
        for title in titles:
            writer.writerow([title])
    print(f"Google search titles saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python googleAPI.py <query>")
        sys.exit(1)

    query = sys.argv[1]
    total_results = 10
    output_path = "google_search_results.csv"

    titles = get_google_search_titles(query, total_results=total_results)
    save_titles_to_csv(titles, output_path)
