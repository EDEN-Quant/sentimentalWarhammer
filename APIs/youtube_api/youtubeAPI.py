import requests
import csv
import os
import sys
import time

# Fetch API Key and Base URL from environment variables
API_KEY = os.environ.get("API_KEY")
BASE_URL = os.environ.get("BASE_URL", "https://www.googleapis.com/youtube/v3/search")

if not API_KEY:
    raise ValueError("Missing API_KEY environment variable.")

def get_youtube_titles(query, max_results=50, total_results=50, order='viewCount'):
    if not query.strip():
        raise ValueError("The query cannot be empty.")

    if max_results < 1 or max_results > 50:
        raise ValueError("maxResults must be between 1 and 50.")

    titles = []
    next_page_token = None
    retrieved_results = 0

    print(f"Fetching YouTube videos for query: {query}")
    print(f"Total results requested: {total_results}")

    while retrieved_results < total_results:
        fetch_count = min(max_results, total_results - retrieved_results)  # Ensure correct batch size

        params = {
            'part': 'snippet',
            'q': query,
            'maxResults': fetch_count,  # Each request fetches up to 50 results
            'type': 'video',
            'key': API_KEY,
            'order': order,
            'pageToken': next_page_token,
        }

        print(f"\nMaking API request with params: {params}")  # Debugging

        response = requests.get(BASE_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            video_titles = [item['snippet']['title'] for item in data.get('items', [])]
            titles.extend(video_titles)
            retrieved_results += len(video_titles)

            print(f"Retrieved {len(video_titles)} videos. Total so far: {retrieved_results}")

            next_page_token = data.get('nextPageToken')
            if not next_page_token or len(video_titles) == 0:
                print("No more pages available, stopping pagination.")
                break  # Stop if no more pages are available
        else:
            print(f"\nError: {response.status_code} - {response.text}")
            break  # Stop execution on error

        time.sleep(1)  # Prevent hitting API rate limits

    print(f"\nFinal count of YouTube videos retrieved: {len(titles)}")
    return titles[:total_results]  # Ensure we return exactly `total_results`


def save_titles_to_csv(titles, output_path):
    """Saves YouTube video titles to a CSV file."""
    directory = os.path.dirname(output_path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["YouTube Video Titles"])
        for title in titles:
            writer.writerow([title])

    print(f"YouTube titles saved to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python youtubeAPI.py <query> [total_results]")
        sys.exit(1)

    query = sys.argv[1]
    total_results = int(sys.argv[2]) if len(sys.argv) > 2 else 20  # Default to 20 results

    # Set the output path
    output_path = os.path.join("..", "sentimentalWarhammer", "data", "youtube_csv", "youtube_titles.csv")

    try:
        titles = get_youtube_titles(query, total_results=min(total_results, 500))  # Max limit set to 500
        save_titles_to_csv(titles, output_path)
    except ValueError as e:
        print(str(e))
