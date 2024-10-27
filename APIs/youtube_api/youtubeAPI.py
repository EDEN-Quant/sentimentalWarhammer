import requests
import csv
import os

# Replace with your YouTube Data API key
API_KEY = 'AIzaSyAmsrtE349oSwGB4qTfYxGizW__5w4zS4k'

# Base URL for the YouTube Data API
BASE_URL = "https://www.googleapis.com/youtube/v3/search"

def get_youtube_titles(query, max_results=10):
    # Parameters for the API request
    params = {
        'part': 'snippet',
        'q': query,
        'maxResults': max_results,
        'type': 'video',  # Ensures only video results are returned
        'key': API_KEY
    }
    
    # Make the request to the YouTube API
    response = requests.get(BASE_URL, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Extract video titles from the response
        titles = [item['snippet']['title'] for item in data.get('items', [])]
        return titles
    else:
        print(f"An error occurred: {response.status_code}")
        return []

def save_titles_to_csv(titles, output_path="data/youtube_csv/youtube_titles.csv"):
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save the titles to the specified CSV file path
    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Youtube"])  # CSV header
        for title in titles:
            writer.writerow([title])
    print(f"Titles saved to {output_path}")

if __name__ == "__main__":
    query = "BlackRock"  # Customize your search query
    max_results = 10  # Customize the number of results (up to 50 per request)

    # Get video titles
    titles = get_youtube_titles(query, max_results)

    # Specify output path for the CSV file
    output_path = "data/youtube_csv/youtube_titles.csv"  # Customize the path here

    # Save titles to CSV
    save_titles_to_csv(titles, output_path)
    