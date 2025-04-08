import sys
import os
import subprocess
import pandas as pd
import streamlit as st
import time
from dotenv import load_dotenv

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
python_interpreter = sys.executable

# Import the sentiment analysis module
sys.path.append(base_dir)
import sentiment_analysis_module as sam

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
    st.title("Macroeconomic Data Aggregation & Sentiment Analysis")

    # Sidebar Inputs
    st.sidebar.title("Pipeline Execution")
    query = st.text_input("Enter the search query:")

    if st.button("Run Pipeline"):
        
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

        # Set up the file paths for sentiment analysis
        aggregated_data_path = os.path.join(base_dir, "aggregated_data.csv")
        sec_data_path = os.path.join(base_dir, "SEC", "data", "form4transactions", "summary", "summary_data.csv")
        
        # Check if files exist
        if not os.path.exists(aggregated_data_path):
            st.sidebar.error(f"Error: '{aggregated_data_path}' not found.")
            return
            
        # Run sentiment analysis directly using the module
        update_progress(sentiment_progress, 0, 50)
        
        # Use a try/except block to catch any errors
        try:
            with st.spinner("Running sentiment analysis..."):
                analysis_results, weighted_score, error = sam.run_sentiment_analysis(
                    aggregated_data_path, 
                    sec_data_path
                )
            
            if error:
                st.sidebar.error(f"Error during sentiment analysis: {error}")
                return
                
            update_progress(sentiment_progress, 50, 100)
            
            # Display the results
            st.subheader("Sentiment Analysis Results")
            
            # For backward compatibility - debugging
            with st.expander("Raw Data (for debugging)"):
                st.json([{
                    'column': res['column'],
                    'total_count': res['total_count'],
                    'positive_percentage': res['positive_percentage'],
                    'negative_percentage': res['negative_percentage'],
                    'avg_score': res['avg_score']
                } for res in analysis_results])
            
            # Display results in a nice layout
            if analysis_results:
                # Create tabs for each column plus the combined score
                tab_labels = [res['column'] for res in analysis_results]
                tab_labels.append("Combined Score")
                tabs = st.tabs(tab_labels)
                
                # Display individual column results
                for i, result_data in enumerate(analysis_results):
                    with tabs[i]:
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Entries", f"{result_data['total_count']}")
                        with col2:
                            st.metric("Positive %", f"{result_data['positive_percentage']:.2f}%")
                        with col3:
                            st.metric("Negative %", f"{result_data['negative_percentage']:.2f}%")
                        with col4:
                            st.metric("Average Score", f"{result_data['avg_score']:.2f}")
                        
                        # Create a histogram of the sentiment distribution if we have detailed data
                        if 'detailed_df' in result_data and not result_data['detailed_df'].empty:
                            try:
                                import plotly.express as px
                                fig = px.histogram(
                                    result_data['detailed_df'], 
                                    x='adjustedScore',
                                    title=f"Sentiment Distribution for {result_data['column']}",
                                    labels={'adjustedScore': 'Sentiment Score (-1 to 1)'},
                                    nbins=20
                                )
                                fig.update_layout(yaxis_title="Count", bargap=0.1)
                                st.plotly_chart(fig, use_container_width=True)
                            except Exception as e:
                                st.warning(f"Could not display histogram: {e}")
                
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
                    
                    # Calculate component contributions
                    google_result = next((res for res in analysis_results if res['column'] == "GoogleSearch"), None)
                    youtube_result = next((res for res in analysis_results if res['column'] == "YouTube"), None)
                    
                    google_score = google_result['avg_score'] if google_result else 0
                    youtube_score = youtube_result['avg_score'] if youtube_result else 0
                    
                    st.write("### Score Components")
                    st.write("The weighted score is calculated with:")
                    st.write(f"- GoogleSearch: {google_score:.2f} × 0.50 = {google_score * 0.5:.2f}")
                    st.write(f"- YouTube: {youtube_score:.2f} × 0.40 = {youtube_score * 0.4:.2f}")
                    
                    # Get SEC data
                    insider_sentiment = 0
                    if os.path.exists(sec_data_path):
                        try:
                            sec_df, _ = sam.load_data_with_failover(sec_data_path)
                            first_company = sec_df.iloc[0]
                            insider_sentiment = first_company['sentiment_score']
                        except Exception:
                            pass
                            
                    st.write(f"- SEC Insider: {insider_sentiment:.2f} × 0.10 = {insider_sentiment * 0.1:.2f}")
                    st.write(f"**Final Score: {weighted_score:.2f}**")
                    
                    st.info("For a more detailed analysis with charts and customizable weights, please visit the 'Combined Analysis' page.")
            else:
                st.warning("No results were returned from the sentiment analysis.")
                
        except Exception as e:
            st.error(f"An error occurred during sentiment analysis: {e}")
            update_progress(sentiment_progress, 100, 100)

        st.sidebar.success("Pipeline execution complete!")

if __name__ == "__main__":
    main()
