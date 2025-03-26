import sys
import os
import subprocess
import pandas as pd
import streamlit as st
import time
from dotenv import load_dotenv

# Add the SEC scripts directory to the system path
data_processing_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'SEC', 'scripts', 'data_processing'))
sys.path.append(data_processing_path)

from tickers_ciks import tickers_ciks
from csv_extractor import fetch_edgar_data, save_filings_to_csv

# Fetch API key, CX, and Base URL from environment variables
if 'GOOGLE_SEARCH_API_KEY' not in os.environ or 'YOUTUBE_API_KEY' not in os.environ or 'CX' not in os.environ:
    st.sidebar.error("Please set the required environment variables: GOOGLE_SEARCH_API_KEY, YOUTUBE_API_KEY, CX.")
else:
    GOOGLE_SEARCH_API_KEY = os.environ.get("GOOGLE_SEARCH_API_KEY")
    YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
    CX = os.environ.get("CX")
    BASE_URL = os.environ.get("BASE_URL", "https://www.googleapis.com/customsearch/v1")  # Default BASE_URL if not provided

def update_progress(progress_bar, start, end, delay=0.1):
    """Function to gradually update a progress bar in the sidebar"""
    for percent in range(start, end + 1, 5):
        time.sleep(delay)
        progress_bar.progress(percent)

def aggregate_csv_data(root_dir, output_file, progress_bar):
    """Aggregate CSV data from various sources"""
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
    st.title("Stock Data Aggregation & Sentiment Analysis")

    # Sidebar Inputs
    st.sidebar.title("Pipeline Execution")
    stock_symbol = st.text_input("Enter the stock symbol:")
    query = st.text_input("Enter the search query:")

    if st.button("Run Pipeline"):
        if not stock_symbol:
            st.sidebar.error("Please enter a stock symbol.")
            return

        cik = tickers_ciks.get(stock_symbol.upper())
        if not cik:
            st.sidebar.error(f"Stock symbol {stock_symbol} not found in tickers_ciks.")
            return

        python_interpreter = sys.executable
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        ### **SEC Filings Processing**
        st.sidebar.info("Fetching SEC filings...")
        sec_progress = st.sidebar.progress(0)
        update_progress(sec_progress, 0, 30)

        form_4_df = fetch_edgar_data(cik)
        if not form_4_df.empty:
            save_filings_to_csv(stock_symbol, form_4_df)
            st.sidebar.success(f"Saved SEC filings for {stock_symbol}.")
        else:
            st.sidebar.warning(f"No SEC filings found for {stock_symbol}.")
            return

        update_progress(sec_progress, 30, 100)

        ### **Processing SEC CSV Files**
        processing_scripts = ["read_csv.py", "xml_extractor.py", "read_xml.py", "Summarize.py"]
        process_progress = st.sidebar.progress(0)

        for i, script_name in enumerate(processing_scripts):
            script_path = os.path.join(data_processing_path, script_name)
            if not os.path.exists(script_path):
                st.sidebar.error(f"Error: {script_path} not found.")
                return
            subprocess.run([python_interpreter, script_path, stock_symbol])
            
            next_progress = min((i + 1) * 25, 100)
            update_progress(process_progress, i * 25, next_progress)

        ### **YouTube API Processing**
        st.sidebar.info("Running YouTube API script...")
        youtube_progress = st.sidebar.progress(0)

        youtube_script = os.path.join(base_dir, "APIs", "youtube_api", "youtubeAPI.py")
        if not os.path.exists(youtube_script):
            st.sidebar.error(f"Error: {youtube_script} not found.")
            return

        total_results = 50
        youtube_process = subprocess.Popen(
            [python_interpreter, youtube_script, query, str(total_results)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        update_progress(youtube_progress, 0, 50)
        youtube_stdout, youtube_stderr = youtube_process.communicate()
        update_progress(youtube_progress, 50, 100)

        st.sidebar.subheader("YouTube API Output")
        if youtube_stdout:
            st.sidebar.text(youtube_stdout.decode())
        if youtube_stderr:
            st.sidebar.error("Seems we have run out of requests for the YouTube API: Please try again later.")
            # st.sidebar.text(youtube_stderr.decode())

        ### **Google Search API Processing**
        st.sidebar.info("Running Google Search API script...")
        google_progress = st.sidebar.progress(0)

        google_script = os.path.join(base_dir, "APIs", "google_search", "googleAPI.py")
        if not os.path.exists(google_script):
            st.sidebar.error(f"Error: {google_script} not found.")
            return

        google_process = subprocess.Popen(
            [python_interpreter, google_script, query],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        update_progress(google_progress, 0, 50)
        google_stdout, google_stderr = google_process.communicate()
        update_progress(google_progress, 50, 100)

        st.sidebar.subheader("Google Search API Output")
        if google_stdout:
            st.sidebar.text(google_stdout.decode())
        if google_stderr:
            st.sidebar.error("Seems we have run out of requests for the Google Search API: Please try again later.")
            # st.sidebar.text(google_stderr.decode())

        ### **CSV Aggregation**
        st.sidebar.info("Aggregating CSV files...")
        aggregate_progress = st.sidebar.progress(0)

        root_dir = os.path.join(base_dir, "data")
        output_file = os.path.join(base_dir, "aggregated_data.csv")

        update_progress(aggregate_progress, 0, 50)
        aggregated = aggregate_csv_data(root_dir, output_file, aggregate_progress)
        update_progress(aggregate_progress, 50, 100)

        if aggregated:
            st.sidebar.success("Aggregation complete.")

        ### **Sentiment Analysis**
        st.sidebar.info("Performing sentiment analysis...")
        sentiment_progress = st.sidebar.progress(0)

        sentiment_analysis_script = os.path.join(base_dir, "sentimentAnalysisV6.py")
        if not os.path.exists(sentiment_analysis_script):
            st.sidebar.error(f"Error: {sentiment_analysis_script} not found.")
            return

        update_progress(sentiment_progress, 0, 50)
        result = subprocess.run(
            [python_interpreter, sentiment_analysis_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        update_progress(sentiment_progress, 50, 100)
        
        if result.stdout:
            st.text("Sentiment Analysis Output")
            st.text(result.stdout)

        st.sidebar.success("Pipeline execution complete!")

if __name__ == "__main__":
    main()
