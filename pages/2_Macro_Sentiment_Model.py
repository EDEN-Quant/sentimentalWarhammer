import sys
import os
import subprocess
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Fetch API key, CX, and Base URL from environment variables
GOOGLE_SEARCH_API_KEY = os.environ.get("GOOGLE_SEARCH_API_KEY")
CX = os.environ.get("CX")
BASE_URL = os.environ.get("BASE_URL", "https://www.googleapis.com/customsearch/v1")  # Default BASE_URL if not provided

if not GOOGLE_SEARCH_API_KEY or not CX:
    raise ValueError("Missing API_KEY or CX environment variables.")

def aggregate_csv_data(root_dir, output_file):
    """ Aggregate CSV data from the YouTube and Google Search API results """
    data_frames = []
    
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".csv"):
                file_path = os.path.join(dirpath, filename)
                
                try:
                    df = pd.read_csv(file_path)
                    data_frames.append(df)
                except Exception as e:
                    st.error(f"Could not read {file_path}: {e}")

    if not data_frames:
        st.warning("No CSV files found to aggregate.")
        return None
    
    try:
        aggregate_df = pd.concat(data_frames, axis=1)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        aggregate_df.to_csv(output_file, index=False)
        st.success(f"Aggregated data saved to {output_file}")
        return output_file
    except Exception as e:
        st.error(f"Error during concatenation: {e}")
        return None

def main():
    st.title("Macro Sentiment Analysis Pipeline")

    # Inputs
    query = st.text_input("Enter the search query:")

    if st.button("Run Pipeline"):
        if not query:
            st.error("Please enter a search query.")
            return

        # Set base directory correctly for the new script location
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        # Run YouTube API script
        youtube_script = os.path.join(base_dir, "APIs", "youtube_api", "youtubeAPI.py")

        if not os.path.exists(youtube_script):
            st.error(f"Error: {youtube_script} not found.")
            return

        st.info("Running YouTube API script...")
        python_interpreter = sys.executable
        total_results = 50  # Change this based on user input or requirements

        youtube_process = subprocess.Popen(
            [python_interpreter, youtube_script, query, str(total_results)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        youtube_stdout, youtube_stderr = youtube_process.communicate()

        # Display YouTube API output
        st.subheader("YouTube API Output")
        if youtube_stdout:
            st.text(youtube_stdout.decode())
        if youtube_stderr:
            st.error("Error in YouTube API")
            st.text(youtube_stderr.decode())

        # Run Google Search API script
        google_script = os.path.join(base_dir, "APIs", "google_search", "googleAPI.py")

        if not os.path.exists(google_script):
            st.error(f"Error: {google_script} not found.")
            return

        st.info("Running Google Search API script...")
        google_process = subprocess.Popen(
            [python_interpreter, google_script, query],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        google_stdout, google_stderr = google_process.communicate()

        # Display Google API output
        st.subheader("Google Search API Output")
        if google_stdout:
            st.text(google_stdout.decode())
        if google_stderr:
            st.error("Error in Google Search API")
            st.text(google_stderr.decode())

        # Aggregate CSV files from YouTube & Google Search results
        st.info("Aggregating CSV files...")
        root_dir = os.path.join(base_dir, "data")
        output_file = os.path.join(base_dir, "aggregated_data.csv")
        aggregated = aggregate_csv_data(root_dir, output_file)
        if aggregated:
            st.success("Aggregation complete.")

        # Perform sentiment analysis
        sentiment_analysis_script = os.path.join(base_dir, "sentimentAnalysisV6.py")

        if not os.path.exists(sentiment_analysis_script):
            st.error(f"Error: {sentiment_analysis_script} not found.")
            return

        st.info("Performing sentiment analysis...")
        result = subprocess.run(
            [python_interpreter, sentiment_analysis_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Display sentiment analysis output
        if result.stdout:
            st.subheader("Sentiment Analysis Output")
            st.text(result.stdout)

        st.success("Pipeline execution complete.")

if __name__ == "__main__":
    main()
