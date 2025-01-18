import requests
import csv
import os
import sys
import time

API_KEY = 'AIzaSyAmsrtE349oSwGB4qTfYxGizW__5w4zS4k'
BASE_URL = "https://www.googleapis.com/youtube/v3/search"

def get_youtube_titles(query, max_results=50, total_results=500, order='viewCount'):
    titles = []
    next_page_token = None

    while len(titles) < total_results:
        params = {
            'part': 'snippet',
            'q': query,
            'maxResults': min(max_results, total_results - len(titles)),
            'type': 'video',
            'key': API_KEY,
            'pageToken': next_page_token,
        }

        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            titles.extend([item['snippet']['title'] for item in data.get('items', [])])
            next_page_token = data.get('nextPageToken')
            if not next_page_token:
                break
        else:
            print(f"Error: {response.status_code}, {response.text}")
            break

        time.sleep(1)

    return titles

def save_titles_to_csv(titles, output_path):
    # Ensure the output directory exists
    directory = os.path.dirname(output_path)
    if directory:  # Check if a directory path exists in output_path
        os.makedirs(directory, exist_ok=True)

    # Save the titles to the specified CSV file path
    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["YouTube"])  # CSV header
        for title in titles:
            writer.writerow([title])
    print(f"YouTube titles saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python youtubeAPI.py <query>")
        sys.exit(1)

    query = sys.argv[1]
    # Set the output path to your desired location
    output_path = r"..\sentimentalWarhammer\data\youtube_csv\youtube_titles.csv"

    total_results = 500
    titles = get_youtube_titles(query, total_results=total_results)
    save_titles_to_csv(titles, output_path)
