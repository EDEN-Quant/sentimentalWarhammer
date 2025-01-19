import sys
import os
import subprocess
import pandas as pd
import streamlit as st

# Add the data_processing directory to the system path
data_processing_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'SEC', 'scripts', 'data_processing'))
sys.path.append(data_processing_path)

from tickers_ciks import tickers_ciks
from csv_extractor import fetch_edgar_data, save_filings_to_csv

def aggregate_csv_data(root_dir, output_file):
    # List to store each CSV file's data
    data_frames = []
    
    # Walk through all subdirectories in the root directory
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".csv"):
                file_path = os.path.join(dirpath, filename)
                
                # Read the CSV file
                try:
                    df = pd.read_csv(file_path)
                    data_frames.append(df)  # Append the DataFrame
                except Exception as e:
                    st.error(f"Could not read {file_path}: {e}")

    # Check if we have any data to aggregate
    if not data_frames:
        st.warning("No CSV files found to aggregate.")
        return None
    
    # Concatenate all DataFrames side by side
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
    st.title("Stock Data Aggregation and Analysis")

    # Inputs
    stock_symbol = st.text_input("Enter the stock symbol:")
    query = st.text_input("Enter the search query:")

    if st.button("Run Pipeline"):
        if not stock_symbol:
            st.error("Please enter a stock symbol.")
            return

        cik = tickers_ciks.get(stock_symbol.upper())
        if not cik:
            st.error(f"Stock symbol {stock_symbol} not found in tickers_ciks.")
            return

        # Fetch EDGAR data
        st.info("Fetching EDGAR data...")
        form_4_df = fetch_edgar_data(cik)

        if not form_4_df.empty:
            save_filings_to_csv(stock_symbol, form_4_df)
            st.success(f"Saved filings for {stock_symbol}.")
        else:
            st.warning(f"No filings found for {stock_symbol}.")
            return

        # Process saved CSV files
        read_csv_script = os.path.join(data_processing_path, 'read_csv.py')
        python_interpreter = sys.executable
        subprocess.run([python_interpreter, read_csv_script, stock_symbol])

        # Download and save XML files
        xml_extractor_script = os.path.join(data_processing_path, 'xml_extractor.py')
        subprocess.run([python_interpreter, xml_extractor_script])

        # Process downloaded XML files
        read_xml_script = os.path.join(data_processing_path, 'read_xml.py')
        subprocess.run([python_interpreter, read_xml_script, stock_symbol])

        # Generate summary CSV
        summarize_script = os.path.join(data_processing_path, 'Summarize.py')
        subprocess.run([python_interpreter, summarize_script, stock_symbol])

        # Run YouTube API script
        base_dir = os.path.dirname(__file__)
        youtube_script = os.path.join(base_dir, "APIs", "youtube_api", "youtubeAPI.py")

        if not os.path.exists(youtube_script):
            st.error(f"Error: {youtube_script} not found.")
            return

        youtube_process = subprocess.Popen(
            [python_interpreter, youtube_script, query],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        youtube_stdout, youtube_stderr = youtube_process.communicate()

        # Display YouTube API output
        st.subheader("YouTube API Output")
        st.text(youtube_stdout.decode())
        if youtube_stderr:
            st.error(youtube_stderr.decode())

        # Aggregate CSV files
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
            text=True  # Ensure the output is captured as a string
        )

        # Display the output of the sentiment analysis
        if result.stdout:
            st.subheader("Sentiment Analysis Output")
            st.text(result.stdout)
        # if result.stderr:
        #     st.error("Error in Sentiment Analysis")
        #     st.text(result.stderr)

        st.success("Pipeline execution complete.")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))  # Default to port 8000
    st._is_running_with_streamlit = True
    st.run(port=port)
