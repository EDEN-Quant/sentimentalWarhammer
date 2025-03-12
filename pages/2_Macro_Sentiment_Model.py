import sys
import os
import subprocess
import pandas as pd
import streamlit as st
import time
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def update_progress(progress_bar, start, end, delay=0.1):
    """Function to gradually update progress bar"""
    for percent in range(start, end + 1, 5):
        time.sleep(delay)  # Simulate progress delay
        progress_bar.progress(percent)

def aggregate_csv_data(root_dir, output_file, progress_bar):
    """Aggregate CSV data from YouTube and Google Search results"""
    data_frames = []
    
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".csv"):
                file_path = os.path.join(dirpath, filename)
                try:
                    df = pd.read_csv(file_path)
                    data_frames.append(df)
                except Exception as e:
                    st.sidebar.error(f"Could not read {file_path}: {e}")

    if not data_frames:
        st.sidebar.warning("No CSV files found to aggregate.")
        return None
    
    try:
        aggregate_df = pd.concat(data_frames, axis=1)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        aggregate_df.to_csv(output_file, index=False)
        update_progress(progress_bar, 50, 100)  # Finish progress update
        st.sidebar.success(f"Aggregated data saved to {output_file}")
        return output_file
    except Exception as e:
        st.sidebar.error(f"Error during concatenation: {e}")
        return None

def main():
    st.title("Macro Sentiment Analysis Pipeline")

    # Sidebar Inputs
    st.sidebar.title("Pipeline Execution")
    query = st.text_input("Enter the search query:")

    if st.button("Run Pipeline"):
        if not query:
            st.sidebar.error("Please enter a search query.")
            return

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        python_interpreter = sys.executable

        ### **Run YouTube API Script**
        st.sidebar.info("Running YouTube API script...")
        youtube_progress = st.sidebar.progress(0)  # Initialize progress bar

        youtube_script = os.path.join(base_dir, "APIs", "youtube_api", "youtubeAPI.py")
        if not os.path.exists(youtube_script):
            st.sidebar.error(f"Error: {youtube_script} not found.")
            return

        update_progress(youtube_progress, 0, 50)  # Simulate initial progress
        youtube_process = subprocess.Popen(
            [python_interpreter, youtube_script, query, "50"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        youtube_stdout, youtube_stderr = youtube_process.communicate()
        update_progress(youtube_progress, 50, 100)  # Complete progress

        st.sidebar.subheader("YouTube API Output")
        if youtube_stdout:
            st.sidebar.text(youtube_stdout.decode())
        if youtube_stderr:
            st.sidebar.error("Error in YouTube API")
            st.sidebar.text(youtube_stderr.decode())

        ### **Run Google Search API Script**
        st.sidebar.info("Running Google Search API script...")
        google_progress = st.sidebar.progress(0)

        google_script = os.path.join(base_dir, "APIs", "google_search", "googleAPI.py")
        if not os.path.exists(google_script):
            st.sidebar.error(f"Error: {google_script} not found.")
            return

        update_progress(google_progress, 0, 50)  # Simulate initial progress
        google_process = subprocess.Popen(
            [python_interpreter, google_script, query],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        google_stdout, google_stderr = google_process.communicate()
        update_progress(google_progress, 50, 100)  # Complete progress

        st.sidebar.subheader("Google Search API Output")
        if google_stdout:
            st.sidebar.text(google_stdout.decode())
        if google_stderr:
            st.sidebar.error("Error in Google Search API")
            st.sidebar.text(google_stderr.decode())

        ### **Aggregate CSV Files**
        st.sidebar.info("Aggregating CSV files...")
        aggregate_progress = st.sidebar.progress(0)

        root_dir = os.path.join(base_dir, "data")
        output_file = os.path.join(base_dir, "aggregated_data.csv")

        update_progress(aggregate_progress, 0, 50)  # Simulate initial progress
        aggregated = aggregate_csv_data(root_dir, output_file, aggregate_progress)

        if aggregated:
            st.sidebar.success("Aggregation complete.")

        ### **Perform Sentiment Analysis**
        st.sidebar.info("Performing sentiment analysis...")
        sentiment_progress = st.sidebar.progress(0)

        sentiment_analysis_script = os.path.join(base_dir, "sentimentAnalysisV6.py")
        if not os.path.exists(sentiment_analysis_script):
            st.sidebar.error(f"Error: {sentiment_analysis_script} not found.")
            return

        update_progress(sentiment_progress, 0, 50)  # Simulate initial progress
        result = subprocess.run(
            [python_interpreter, sentiment_analysis_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        update_progress(sentiment_progress, 50, 100)  # Complete progress

        st.sidebar.subheader("Sentiment Analysis Output")
        if result.stdout:
            st.text(result.stdout)

        st.sidebar.success("Pipeline execution complete.")

if __name__ == "__main__":
    main()
