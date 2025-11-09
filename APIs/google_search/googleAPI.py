import requests
import csv
import os
import sys

# Fetch API Key and CX from environment variables
GOOGLE_SEARCH_API_KEY = os.environ.get("GOOGLE_SEARCH_API_KEY")
CX = os.environ.get("CX")
BASE_URL = "https://www.googleapis.com/customsearch/v1"

# Ensure API Key and CX are available
if not GOOGLE_SEARCH_API_KEY or not CX:
    raise ValueError("Missing GOOGLE_SEARCH_API_KEY or GOOGLE_CX environment variables.")

# Where to write the CSV results
OUTPUT_PATH = os.path.join("data", "google_search_csv", "google_search_results.csv")

def get_google_search_titles(query, total_results=100):
    """
    Fetch up to 100 Google search results for a given query.
    """
    titles = []
    start_index = 1  # Pagination starts at 1

    while len(titles) < total_results:
        fetch_count = min(10, total_results - len(titles))  # Google API max per request

        params = {
            "key": GOOGLE_SEARCH_API_KEY,
            "cx": CX,
            "q": query,
            "start": start_index,  # Pagination index
            "num": fetch_count  # Max is 10
        }

        response = requests.get(BASE_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            titles.extend([item["title"] for item in items])

            # Google API only allows 10 results per page, so increment by 10
            start_index += 10

            # Stop if there are no more results
            if not items or len(items) < 10:
                break
        else:
            print(f"Error: {response.status_code}, {response.text}")
            break

    return titles

def save_titles_to_csv(titles):
    """
    Saves the Google search results to the correct path based on environment.
    """
    directory = os.path.dirname(OUTPUT_PATH)

    # Ensure the output directory exists (only for local use)
    os.makedirs(directory, exist_ok=True)

    # Save titles to a CSV file
    with open(OUTPUT_PATH, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["GoogleSearch"])  # Add a header
        for title in titles:
            writer.writerow([title])

    print(f"✅ Google search titles saved to: {OUTPUT_PATH}")
    return OUTPUT_PATH

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python googleAPI.py <query>")
        sys.exit(1)

    query = sys.argv[1]
    total_results = 100  # Default to fetching 100 results

    # Fetch Google search titles and save them to the correct path
    titles = get_google_search_titles(query, total_results=total_results)
    csv_file = save_titles_to_csv(titles)

