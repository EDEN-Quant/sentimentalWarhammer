import requests
from requests_oauthlib import OAuth1
import csv
import os

# Replace with your Twitter API credentials
API_KEY = 'KW5tdRtt4zOfZJD4iTNMrphwo'
API_SECRET_KEY = '7ZcrgI4qke0VUlWRnXxPkBi2oOJ6A5W78KQ5bKJb8skx5IThbZ'
ACCESS_TOKEN = '1846633251743715332-Jn07CmXa0x0yVoSOkve5fLoxlFITTF'
ACCESS_TOKEN_SECRET = 'zDqNZlbBF5F5btlaHqKu1buWUWCmKyGQOImRd3ugROMim'

# Base URL for Twitter API
BASE_URL = "https://api.twitter.com/2/tweets/search/recent"

def get_tweets(query, max_results=10):
    # Set up OAuth1 for authentication
    auth = OAuth1(API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    
    # Parameters for the API request
    params = {
        'query': query,
        'max_results': max_results,
        'tweet.fields': 'text,created_at',  # Retrieve tweet text and creation date
    }
    
    # Make the request to the Twitter API
    response = requests.get(BASE_URL, auth=auth, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Extract tweets' text and creation date from the response
        tweets = [(item['text'], item['created_at']) for item in data.get('data', [])]
        return tweets
    else:
        print(f"An error occurred: {response.status_code}, {response.text}")
        return []

def save_tweets_to_csv(tweets, output_path="data/twitter_csv/tweets.csv"):
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save the tweets to the specified CSV file path
    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Tweet", "Created At"])  # CSV header
        for tweet, created_at in tweets:
            writer.writerow([tweet, created_at])
    print(f"Tweets saved to {output_path}")

if __name__ == "__main__":
    query = "BlackRock"  # Customize your search query
    max_results = 5  # Customize the number of results (up to 100 per request for elevated access)

    # Get tweets
    tweets = get_tweets(query, max_results)

    # Specify output path for the CSV file
    output_path = "data/twitter_csv/tweets.csv"  # Customize the path here

    # Save tweets to CSV
    save_tweets_to_csv(tweets, output_path)
