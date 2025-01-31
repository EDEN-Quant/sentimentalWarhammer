import requests
import csv
import os
import sys
import streamlit as st

# 🔹 Fetch API Key from environment variables
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY") or st.secrets["YOUTUBE_API_KEY"]
BASE_URL = "https://www.googleapis.com/youtube/v3/search"

# 🔹 Ensure API Key is available
if not YOUTUBE_API_KEY:
    raise ValueError("Missing API_KEY environment variable.")

# 🔹 Define the correct output path
if "STREAMLIT_SERVER" in os.environ:  # Detect if running on Streamlit Cloud
    OUTPUT_PATH = os.path.join("/tmp", "youtube_titles.csv")  # Use /tmp/ on Streamlit
else:
    OUTPUT_PATH = os.path.join("data", "youtube_csv", "youtube_titles.csv")  # Local path

def get_youtube_titles(query, max_results=50, total_results=500, order="relevance"):
    """
    Fetch YouTube video titles based on a search query.
    """
    titles = []
    next_page_token = None

    while len(titles) < total_results:
        fetch_count = min(max_results, total_results - len(titles))

        params = {
            "part": "snippet",
            "q": query,
            "maxResults": fetch_count,
            "type": "video",
            "key": YOUTUBE_API_KEY,
            "order": order,
            "pageToken": next_page_token,
        }

        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            titles.extend([item["snippet"]["title"] for item in items])
            next_page_token = data.get("nextPageToken")
            if not items or not next_page_token:
                break
        else:
            print(f"Error: {response.status_code}, {response.text}")
            break

    return titles

def save_titles_to_csv(titles):
    """
    Saves the YouTube search results to the correct path based on environment.
    """
    directory = os.path.dirname(OUTPUT_PATH)
    
    # Ensure the output directory exists (only for local use)
    if "STREAMLIT_SERVER" not in os.environ:
        os.makedirs(directory, exist_ok=True)

    # Save titles to a CSV file
    with open(OUTPUT_PATH, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["YouTubeSearch"])  # Add a header
        for title in titles:
            writer.writerow([title])
    
    print(f"✅ YouTube search titles saved to: {OUTPUT_PATH}")
    return OUTPUT_PATH

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python youtubeAPI.py <query>")
        sys.exit(1)

    query = sys.argv[1]
    total_results = 5  # Default to fetching 5 results

    # Fetch YouTube titles and save them to the correct path
    titles = get_youtube_titles(query, total_results=total_results)
    csv_file = save_titles_to_csv(titles)

    # If running on Streamlit, provide a download link
    if "STREAMLIT_SERVER" in os.environ:
        print(f"💾 Download available: {csv_file}")
