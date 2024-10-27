import requests
import csv
import os

# Replace with your Google API key and Custom Search Engine ID
API_KEY = 'AIzaSyAQ4C8k_HyoRG9bZ-n_UaEDtwvUNg6uWnw'
CX = 'e39b1e4e7db0f4c2c'

# Base URL for Google Custom Search API
BASE_URL = "https://www.googleapis.com/customsearch/v1"

def get_google_search_titles(query, num_results=10):
    titles = []
    start_index = 1

    # Loop to handle pagination if num_results > 10
    while len(titles) < num_results:
        # Limit max results per request to 10 as per API
        params = {
            'key': API_KEY,
            'cx': CX,
            'q': query,
            'start': start_index,
            'num': min(10, num_results - len(titles))  # Fetch max 10 results per page
        }

        response = requests.get(BASE_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            titles.extend([item['title'] for item in items])
            start_index += 10  # Increment to fetch the next set of results
        else:
            print(f"An error occurred: {response.status_code}, {response.text}")
            break

    return titles[:num_results]  # Return only the requested number of titles

def save_titles_to_csv(titles, output_path="data/google_search_csv/webpage_titles.csv"):
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save the titles to the specified CSV file path
    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["GoogleSearch"])  # CSV header
        for title in titles:
            writer.writerow([title])
    print(f"Titles saved to {output_path}")

if __name__ == "__main__":
    query = "BlackRock financial reports"  # Customize your search query
    num_results = 10  # Customize the number of results (up to 100 per request)

    # Get search result titles
    titles = get_google_search_titles(query, num_results)

    # Specify output path for the CSV file
    output_path = "data/google_search_csv/webpage_titles.csv"  # Customize the path here

    # Save titles to CSV
    save_titles_to_csv(titles, output_path)
