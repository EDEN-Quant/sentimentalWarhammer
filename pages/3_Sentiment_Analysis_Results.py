import streamlit as st
import pandas as pd
import chardet
import os
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import plotly.express as px
import plotly.graph_objects as go
import warnings

# Reduce warning noise
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Sentiment Analysis Results", page_icon="📊")

st.title("Sentiment Analysis Results")
st.write("This page displays the sentiment analysis results for various data sources.")

# Initialize the sentiment pipeline with a loading indicator and fallback options
with st.spinner("Loading sentiment analysis model..."):
    @st.cache_resource
    def load_pipeline():
        try:
            # Try to load the normal model first
            return pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", batch_size=32)
        except (OSError, EnvironmentError) as e:
            try:
                # Try to load from cache
                model_name = "distilbert-base-uncased-finetuned-sst-2-english"
                model = AutoModelForSequenceClassification.from_pretrained(
                    model_name, 
                    local_files_only=True,
                    cache_dir=os.path.expanduser("~/.cache/huggingface/")
                )
                tokenizer = AutoTokenizer.from_pretrained(
                    model_name, 
                    local_files_only=True,
                    cache_dir=os.path.expanduser("~/.cache/huggingface/")
                )
                return pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, batch_size=32)
            except Exception:
                # If all else fails, use a simple keyword-based classifier
                st.warning("⚠️ Using simplified sentiment analysis due to HuggingFace connection issues. Results may be less accurate than normal.")
                
                # Define a simple fallback classifier
                positive_words = set(['good', 'great', 'excellent', 'positive', 'amazing', 'wonderful', 'best', 'love', 'happy', 'recommend'])
                negative_words = set(['bad', 'terrible', 'awful', 'negative', 'poor', 'worst', 'hate', 'disappointing', 'disappointed', 'avoid'])
                
                def simple_sentiment_classifier(texts):
                    if not isinstance(texts, list):
                        texts = [texts]
                        
                    results = []
                    for text in texts:
                        text = str(text).lower()
                        words = set(text.split())
                        
                        pos_matches = len(words.intersection(positive_words))
                        neg_matches = len(words.intersection(negative_words))
                        
                        if pos_matches > neg_matches:
                            label = "POSITIVE"
                            score = 0.5 + min(0.4, (pos_matches * 0.1))
                        elif neg_matches > pos_matches:
                            label = "NEGATIVE"
                            score = 0.5 + min(0.4, (neg_matches * 0.1)) 
                        else:
                            # If counts are equal, slightly favor positive sentiment
                            if pos_matches > 0:
                                label = "POSITIVE"
                                score = 0.55
                            else:
                                label = "NEUTRAL"
                                score = 0.5
                        
                        results.append({"label": label, "score": score})
                    return results
                
                return simple_sentiment_classifier
    
    # Load the pipeline (or fallback)
    sentiment_pipeline = load_pipeline()

def run_sentiment_analysis(dataset, colName):
    """
    This function:
      1) Drops rows where 'colName' is NaN.
      2) Runs sentiment analysis on that column.
      3) Computes statistics (positive%, negative%, averageScore).
      4) Returns counts and averages for that column.
    """
    
    # Create a progress indicator
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Only drop rows missing in the target column
    status_text.text(f"Preparing data for {colName}...")
    sub_df = dataset.dropna(subset=[colName]).copy()

    # Convert to a list of strings
    sentences = sub_df[colName].astype(str).fillna('').tolist()
    
    # Apply the sentiment pipeline in batches
    status_text.text(f"Running sentiment analysis on {len(sentences)} entries from {colName}...")
    progress_bar.progress(25)
    
    try:
        # Different handling for regular pipeline vs. fallback function
        if callable(sentiment_pipeline) and not hasattr(sentiment_pipeline, 'tokenizer'):
            results = sentiment_pipeline(sentences)
        else:
            results = sentiment_pipeline(sentences)
        
        progress_bar.progress(50)
        
        # Assign results back to sub_df
        sub_df['sentiment'] = [r['label'] for r in results]
        sub_df['score'] = [r['score'] for r in results]
        progress_bar.progress(75)
        
        # Compute an adjusted score: +score for POSITIVE, -score for NEGATIVE
        sub_df['adjustedScore'] = sub_df.apply(
            lambda row: row['score'] if row['sentiment'] == "POSITIVE" else -row['score'],
            axis=1
        )
    except Exception as e:
        status_text.error(f"Error in sentiment analysis: {str(e)}")
        progress_bar.progress(100)
        status_text.empty()
        return sub_df, 0, 0, 0, 0

    # Identify strong positives/negatives (score > 0.85)
    strong_positive = sub_df[(sub_df['sentiment'] == "POSITIVE") & (sub_df['score'] > 0.85)]
    strong_negative = sub_df[(sub_df['sentiment'] == "NEGATIVE") & (sub_df['score'] > 0.85)]

    # Calculate statistics
    total_count = len(sub_df)
    positive_count = len(strong_positive)
    negative_count = len(strong_negative)

    # Avoid zero-division if total_count = 0
    if total_count > 0:
        positive_percentage = positive_count / total_count * 100
        negative_percentage = negative_count / total_count * 100
        averageScore = sub_df['adjustedScore'].mean()
    else:
        positive_percentage = 0
        negative_percentage = 0
        averageScore = 0
    
    progress_bar.progress(100)
    status_text.empty()
    
    return sub_df, total_count, positive_percentage, negative_percentage, averageScore

def main():
    # File loading section with error handling
    st.subheader("Data Loading")
    
    try:
        # Detect encoding and read the aggregated_data.csv
        file_path = 'aggregated_data.csv'
        if not os.path.exists(file_path):
            st.error(f"Error: '{file_path}' not found.")
            return
            
        # Try to detect encoding
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read(10000))
            encoding = result['encoding']
            
        st.success(f"Detected encoding for aggregated_data.csv: {encoding}")
        
        # Read the CSV with the detected encoding, and fallback to common encodings if it fails
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            st.success(f"Successfully read '{file_path}'")
        except Exception as e:
            st.warning(f"Error with detected encoding, trying alternatives...")
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
                st.success(f"Successfully read '{file_path}' with 'utf-8' encoding")
            except Exception as e:
                try:
                    df = pd.read_csv(file_path, encoding='latin1')
                    st.success(f"Successfully read '{file_path}' with 'latin1' encoding")
                except Exception as e:
                    st.error(f"Failed to read '{file_path}' with any encoding")
                    return
        
        # Read the SEC value from a different CSV file
        sec_file_path = os.path.join('SEC', 'data', 'form4transactions', 'summary', 'summary_data.csv')
        if not os.path.exists(sec_file_path):
            st.error(f"Error: '{sec_file_path}' not found.")
            insider_sentiment = 0
        else:
            try:
                sec_df = pd.read_csv(sec_file_path, encoding=encoding)
                st.success(f"Successfully read '{sec_file_path}'")
                first_company = sec_df.iloc[0]
                insider_sentiment = first_company['sentiment_score']
            except Exception as e:
                st.error(f"Error reading '{sec_file_path}': {e}")
                insider_sentiment = 0
        
        # Process columns
        st.subheader("Sentiment Analysis Results")
        
        # Run sentiment analysis on each column
        results = []
        detailed_data = {}
        
        # Let user select which columns to analyze
        default_columns = ["GoogleSearch", "YouTube"]
        available_columns = df.columns.tolist()
        selected_columns = st.multiselect(
            "Select columns to analyze:", 
            available_columns,
            default=default_columns if all(col in available_columns for col in default_columns) else available_columns[:2]
        )
        
        if not selected_columns:
            st.warning("Please select at least one column to analyze")
            return
            
        for col in selected_columns:
            with st.expander(f"Analyzing {col}", expanded=True):
                try:
                    detailed_df, total_count, positive_percentage, negative_percentage, averageScore = run_sentiment_analysis(df, col)
                    results.append((col, total_count, positive_percentage, negative_percentage, averageScore))
                    detailed_data[col] = detailed_df
                    
                    # Display metrics in columns
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Entries", f"{total_count}")
                    with col2:
                        st.metric("Positive %", f"{positive_percentage:.2f}%")
                    with col3:
                        st.metric("Negative %", f"{negative_percentage:.2f}%")
                    with col4:
                        st.metric("Average Score", f"{averageScore:.2f}")
                    
                    # Create a sentiment distribution chart
                    fig = px.histogram(detailed_df, x='adjustedScore', 
                                      title=f"Sentiment Distribution for {col}",
                                      labels={'adjustedScore': 'Sentiment Score (-1 to 1)'},
                                      nbins=20)
                    fig.update_layout(yaxis_title="Count", bargap=0.1)
                    st.plotly_chart(fig, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Error processing column '{col}': {e}")
        
        # Calculate the weighted average
        st.subheader("Weighted Average Sentiment")
        
        # Create a form for weight adjustment
        with st.form("weight_form"):
            st.write("Adjust the weights for the final sentiment score:")
            weights = {}
            
            # Create weight sliders for each source
            google_weight = 0.5
            youtube_weight = 0.4
            sec_weight = 0.1
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if "GoogleSearch" in [r[0] for r in results]:
                    google_weight = st.slider("GoogleSearch Weight", 0.0, 1.0, 0.5, 0.05)
                    weights["GoogleSearch"] = google_weight
            
            with col2:
                if "YouTube" in [r[0] for r in results]:
                    youtube_weight = st.slider("YouTube Weight", 0.0, 1.0, 0.4, 0.05)
                    weights["YouTube"] = youtube_weight
            
            with col3:
                sec_weight = st.slider("SEC Insider Weight", 0.0, 1.0, 0.1, 0.05)
            
            # Normalize weights to ensure they sum to 1
            total_weight = sum(weights.values()) + sec_weight
            if total_weight > 0:
                norm_factor = 1.0 / total_weight
                for key in weights:
                    weights[key] *= norm_factor
                sec_weight *= norm_factor
            
            submit_button = st.form_submit_button("Calculate Weighted Score")
        
        # After form submission or by default
        google_score = next((res[4] for res in results if res[0] == "GoogleSearch"), 0)
        youtube_score = next((res[4] for res in results if res[0] == "YouTube"), 0)
        
        # Calculate weighted average based on actual available data
        components = []
        weighted_score = 0
        
        if "GoogleSearch" in [r[0] for r in results]:
            weighted_score += google_score * weights.get("GoogleSearch", 0)
            components.append(f"GoogleSearch: {google_score:.2f} × {weights.get('GoogleSearch', 0):.2f}")
        
        if "YouTube" in [r[0] for r in results]:
            weighted_score += youtube_score * weights.get("YouTube", 0)
            components.append(f"YouTube: {youtube_score:.2f} × {weights.get('YouTube', 0):.2f}")
        
        weighted_score += insider_sentiment * sec_weight
        components.append(f"SEC Insider: {insider_sentiment:.2f} × {sec_weight:.2f}")
        
        # Display the weighted score with a gauge chart
        st.write("## Final Sentiment Score")
        
        # Create columns for the formula and the gauge
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.write("### Calculation")
            st.write("The weighted score is calculated as:")
            for component in components:
                st.write(f"- {component}")
            st.write(f"**Final Score: {weighted_score:.2f}**")
            
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
            
            st.write(f"**Interpretation:** {sentiment}")
        
        with col2:
            # Create a gauge chart
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = weighted_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Sentiment Score"},
                gauge = {
                    'axis': {'range': [-1, 1]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [-1, -0.5], 'color': "red"},
                        {'range': [-0.5, -0.2], 'color': "orange"},
                        {'range': [-0.2, 0.2], 'color': "gray"},
                        {'range': [0.2, 0.5], 'color': "lightgreen"},
                        {'range': [0.5, 1], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': weighted_score
                    }
                }
            ))
            
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Run the main function
if __name__ == "__main__":
    main() 