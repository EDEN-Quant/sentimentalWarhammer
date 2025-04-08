import sys
import os
import subprocess
import pandas as pd
import streamlit as st
import time
import chardet
from dotenv import load_dotenv
from sentimentAnalysisV6 import main as run_sentiment_analysis

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
    st.title("Stock Data Aggregation & Sentiment Analysis: Pipeline 7")

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
            st.sidebar.error("Error in YouTube API")
            st.sidebar.text(youtube_stderr.decode())

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
            st.sidebar.error("Error in Google Search API")
            st.sidebar.text(google_stderr.decode())

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

        # Check if aggregated data file exists
        aggregated_file = os.path.join(base_dir, "aggregated_data.csv")
        if not os.path.exists(aggregated_file):
            st.sidebar.error(f"Error: '{aggregated_file}' not found.")
            return

        # Read the aggregated CSV file
        try:
            # Try to detect encoding
            with open(aggregated_file, 'rb') as f:
                result = chardet.detect(f.read(10000))
                encoding = result['encoding']
            
            # Read with detected encoding
            df = pd.read_csv(aggregated_file, encoding=encoding)
            update_progress(sentiment_progress, 25, 50)
        except Exception as e:
            try:
                # Fallback to utf-8
                df = pd.read_csv(aggregated_file, encoding='utf-8')
                update_progress(sentiment_progress, 25, 50)
            except Exception as e:
                try:
                    # Fallback to latin1
                    df = pd.read_csv(aggregated_file, encoding='latin1')
                    update_progress(sentiment_progress, 25, 50)
                except Exception as e:
                    st.sidebar.error(f"Error reading aggregated data: {e}")
                    return

        # Read SEC data
        sec_file_path = os.path.join(base_dir, 'SEC', 'data', 'form4transactions', 'summary', 'summary_data.csv')
        try:
            sec_df = pd.read_csv(sec_file_path, encoding=encoding)
            first_company = sec_df.iloc[0]
            insider_sentiment = first_company['sentiment_score']
        except Exception as e:
            st.sidebar.warning(f"Could not read SEC data: {e}")
            insider_sentiment = 0

        # Run sentiment analysis directly
        update_progress(sentiment_progress, 50, 75)
        
        # Check if we're using the fallback classifier
        is_using_fallback = False
        if hasattr(run_sentiment_analysis, "__module__") and run_sentiment_analysis.__module__ == "__main__":
            is_using_fallback = True
        elif callable(run_sentiment_analysis) and not hasattr(run_sentiment_analysis, "tokenizer"):
            is_using_fallback = True
            
        if is_using_fallback:
            st.warning("⚠️ Using simplified sentiment analysis due to HuggingFace connection issues. Results may be less accurate than normal.")
        
        results = []
        for col in df.columns:
            try:
                total_count, positive_percentage, negative_percentage, averageScore = run_sentiment_analysis(df, col)
                results.append((col, total_count, positive_percentage, negative_percentage, averageScore))
            except Exception as e:
                st.sidebar.error(f"Error processing column '{col}': {e}")
        
        update_progress(sentiment_progress, 75, 100)
        
        # Calculate weighted average
        google_score = next((res[4] for res in results if res[0] == "GoogleSearch"), 0)
        youtube_score = next((res[4] for res in results if res[0] == "YouTube"), 0)
        weighted_score = (google_score * 0.5) + (youtube_score * 0.4) + (insider_sentiment * 0.1)
        
        st.subheader("Sentiment Analysis Results")
        
        # Display results in a nice layout
        if results:
            # Create tabs for each column and combined score
            tab_labels = [res[0] for res in results]
            tab_labels.append("Combined Score")
            tabs = st.tabs(tab_labels)
            
            for i, (column, total_count, positive_percentage, negative_percentage, avg_score) in enumerate(results):
                with tabs[i]:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Entries", f"{total_count}")
                    with col2:
                        st.metric("Positive %", f"{positive_percentage:.2f}%")
                    with col3:
                        st.metric("Negative %", f"{negative_percentage:.2f}%")
                    with col4:
                        st.metric("Average Score", f"{avg_score:.2f}")
            
            # Display the combined weighted average
            with tabs[-1]:
                st.metric("Weighted Average Score", f"{weighted_score:.2f}")
                
                # Interpret the score
                if weighted_score > 0.5:
                    sentiment = "Very Positive"
                    color = "green"
                elif weighted_score > 0.2:
                    sentiment = "Positive"
                    color = "lightgreen"
                elif weighted_score > -0.2:
                    sentiment = "Neutral"
                    color = "gray"
                elif weighted_score > -0.5:
                    sentiment = "Negative"
                    color = "orange"
                else:
                    sentiment = "Very Negative"
                    color = "red"
                
                st.markdown(f"<h3 style='color: {color}'>Overall Sentiment: {sentiment}</h3>", unsafe_allow_html=True)
                
                # Show weight distribution
                st.write("### Weight Distribution")
                st.write("The weighted score is calculated as:")
                st.write(f"- GoogleSearch: {google_score:.2f} × 0.5 = {google_score * 0.5:.2f}")
                st.write(f"- YouTube: {youtube_score:.2f} × 0.4 = {youtube_score * 0.4:.2f}")
                st.write(f"- SEC Insider: {insider_sentiment:.2f} × 0.1 = {insider_sentiment * 0.1:.2f}")
                st.write(f"**Final Score: {weighted_score:.2f}**")
                
                st.info("For a more detailed analysis with charts and customizable weights, please visit the 'Combined Analysis' page.")
        else:
            st.warning("No sentiment analysis results were generated. Check the logs for errors.")

        st.sidebar.success("Pipeline execution complete!")

if __name__ == "__main__":
    main()
