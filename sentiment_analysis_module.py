from transformers import pipeline
import pandas as pd
import chardet
import os

# Initialize the sentiment pipeline
sentiment_pipeline = pipeline("sentiment-analysis", batch_size=32)

def analyze_text(text):
    """Analyze a single text and return sentiment and score"""
    result = sentiment_pipeline(text)[0]
    return result['label'], result['score']

def analyze_column(dataset, colName):
    """
    This function:
      1) Drops rows where 'colName' is NaN.
      2) Runs sentiment analysis on that column.
      3) Computes statistics (positive%, negative%, averageScore).
      4) Returns counts and averages for that column.
    """

    # Only drop rows missing in the target column
    sub_df = dataset.dropna(subset=[colName]).copy()

    # Convert to a list of strings (fill any leftover NaNs just in case)
    sentences = sub_df[colName].astype(str).fillna('').tolist()

    # Apply the sentiment pipeline in batches
    results = sentiment_pipeline(sentences)

    # Assign results back to sub_df
    sub_df['sentiment'] = [r['label'] for r in results]
    sub_df['score'] = [r['score'] for r in results]

    # Compute an adjusted score: +score for POSITIVE, -score for NEGATIVE
    sub_df['adjustedScore'] = sub_df.apply(
        lambda row: row['score'] if row['sentiment'] == "POSITIVE" else -row['score'],
        axis=1
    )

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

    return {
        'column': colName,
        'total_count': total_count, 
        'positive_percentage': positive_percentage, 
        'negative_percentage': negative_percentage, 
        'avg_score': averageScore,
        'detailed_df': sub_df
    }

def load_data_with_failover(file_path):
    """Load data with encoding detection and failover options"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: '{file_path}' not found.")

    # Try to detect encoding
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))
        encoding = result['encoding']

    # Read the CSV with the detected encoding, and fallback to common encodings if it fails
    try:
        df = pd.read_csv(file_path, encoding=encoding)
        return df, encoding
    except Exception:
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            return df, 'utf-8'
        except Exception:
            try:
                df = pd.read_csv(file_path, encoding='latin1')
                return df, 'latin1'
            except Exception as e:
                raise ValueError(f"Failed to read '{file_path}' with any encoding: {e}")

def run_sentiment_analysis(aggregated_data_path, sec_data_path=None):
    """
    Run sentiment analysis on all columns in the aggregated data
    and calculate the weighted average with SEC data if provided.
    
    Returns:
    - A list of dictionaries with analysis results for each column
    - The weighted average score
    - Any error messages
    """
    
    try:
        # Load aggregated data
        df, encoding = load_data_with_failover(aggregated_data_path)
        
        # Load SEC data if path provided
        insider_sentiment = 0
        if sec_data_path and os.path.exists(sec_data_path):
            try:
                sec_df, _ = load_data_with_failover(sec_data_path)
                first_company = sec_df.iloc[0]
                insider_sentiment = first_company['sentiment_score']
            except Exception as e:
                pass
        
        # Run sentiment analysis on each column
        results = []
        for col in df.columns:
            try:
                result = analyze_column(df, col)
                results.append(result)
            except Exception as e:
                print(f"Error processing column '{col}': {e}")
        
        # Calculate the weighted average for GoogleSearch, YouTube, and SEC
        google_result = next((res for res in results if res['column'] == "GoogleSearch"), None)
        youtube_result = next((res for res in results if res['column'] == "YouTube"), None)
        
        google_score = google_result['avg_score'] if google_result else 0
        youtube_score = youtube_result['avg_score'] if youtube_result else 0
        
        weighted_average_score = (google_score * 0.5) + (youtube_score * 0.4) + (insider_sentiment * 0.1)
        
        return results, weighted_average_score, None
    
    except Exception as e:
        return [], 0, str(e)

if __name__ == "__main__":
    # For backward compatibility with the original script
    aggregated_data_path = 'aggregated_data.csv'
    sec_data_path = os.path.join('SEC', 'data', 'form4transactions', 'summary', 'summary_data.csv')
    
    results, weighted_score, error = run_sentiment_analysis(aggregated_data_path, sec_data_path)
    
    if error:
        print(f"Error: {error}")
    else:
        # Print results in the same format as the original script
        for result in results:
            print(
                f"Column: {result['column']}\n"
                f"Processed {result['total_count']} entries\n"
                f"{result['positive_percentage']:.2f}% were positive\n"
                f"{result['negative_percentage']:.2f}% were negative\n"
                f"The average score (-1 to 1) was {result['avg_score']:.2f}\n"
            )
        
        print(f"The weighted average score is {weighted_score:.2f}") 