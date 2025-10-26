from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import pandas as pd
import chardet
import os
import warnings
from transformers.utils.logging import set_verbosity_error

# Reduce warning noise
set_verbosity_error()
warnings.filterwarnings('ignore')

# Initialize the sentiment pipeline with better error handling
try:
    # Try to load the model with normal settings
    sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", batch_size=32)
except (OSError, EnvironmentError) as e:
    try:
        # If we can't connect to HuggingFace, try to use a local model if it's been cached before
        print("Connection to HuggingFace failed. Attempting to use cached model...")
        model_name = "distilbert-base-uncased-finetuned-sst-2-english"
        
        # Try to load from cache directly
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
        sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, batch_size=32)
    except Exception:
        # If no cached model exists, create a very simple fallback classifier
        print("Cannot access HuggingFace model. Using simple fallback classifier.")
        # Define a very basic sentiment classifier using keyword matching
        positive_words = set(['good', 'great', 'excellent', 'positive', 'amazing', 'wonderful', 'best', 'love', 'happy', 'recommend'])
        negative_words = set(['bad', 'terrible', 'awful', 'negative', 'poor', 'worst', 'hate', 'disappointing', 'disappointed', 'avoid'])
        
        def simple_sentiment_classifier(texts):
            if not isinstance(texts, list):
                texts = [texts]
                
            results = []
            for text in texts:
                text = text.lower()
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
                    # If counts are equal, slightly favor positive sentiment (optimistic bias)
                    if pos_matches > 0:
                        label = "POSITIVE"
                        score = 0.55
                    else:
                        label = "NEUTRAL"
                        score = 0.5
                
                results.append({"label": label, "score": score})
            return results
        
        # This replaces the HuggingFace pipeline with our simple classifier
        sentiment_pipeline = simple_sentiment_classifier

def main(dataset, colName):
    """
    This function:
      1) Drops rows where 'colName' is NaN.
      2) Runs sentiment analysis on that column.
      3) Computes statistics (positive%, negative%, averageScore).
      4) Returns counts and averages for that column.
    """

    # Only drop rows missing in the target column (instead of dropping from the entire DataFrame)
    sub_df = dataset.dropna(subset=[colName]).copy()

    # Convert to a list of strings (fill any leftover NaNs just in case)
    sentences = sub_df[colName].astype(str).fillna('').tolist()

    try:
        # Apply the sentiment pipeline in batches
        if callable(sentiment_pipeline):
            # For our fallback function
            results = sentiment_pipeline(sentences)
        else:
            # For the HuggingFace pipeline
            results = sentiment_pipeline(sentences)
        
        # Assign results back to sub_df
        sub_df['sentiment'] = [r['label'] for r in results]
        sub_df['score'] = [r['score'] for r in results]
        
        # Compute an adjusted score: +score for POSITIVE, -score for NEGATIVE
        sub_df['adjustedScore'] = sub_df.apply(
            lambda row: row['score'] if row['sentiment'] == "POSITIVE" else -row['score'],
            axis=1
        )
    except Exception as e:
        # In case of any other errors, return zero results
        print(f"Error processing sentiment for {colName}: {str(e)}")
        return 0, 0, 0, 0

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

    return total_count, positive_percentage, negative_percentage, averageScore

if __name__ == "__main__":
    # --------------------------------------------
    # Detect encoding and read the aggregated_data.csv
    # --------------------------------------------
    file_path = 'aggregated_data.csv'
    if not os.path.exists(file_path):
        print(f"Error: '{file_path}' not found.")
        exit(1)
    
    # Try to detect encoding
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))
        encoding = result['encoding']
    
    # Read the CSV with the detected encoding, and fallback to common encodings if it fails
    try:
        df = pd.read_csv(file_path, encoding=encoding)
        # print(f"Successfully read '{file_path}' with encoding '{encoding}'")
    except Exception as e:
        # print(f"Error reading '{file_path}' with detected encoding '{encoding}': {e}")
        # print("Trying with 'utf-8' encoding...")
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            # print(f"Successfully read '{file_path}' with 'utf-8' encoding")
        except Exception as e:
            # print(f"Error reading '{file_path}' with 'utf-8' encoding: {e}")
            # print("Trying with 'latin1' encoding...")
            try:
                df = pd.read_csv(file_path, encoding='latin1')
                # print(f"Successfully read '{file_path}' with 'latin1' encoding")
            except Exception as e:
                # print(f"Error reading '{file_path}' with 'latin1' encoding: {e}")
                exit(1)
    
    # --------------------------------------------
    # Read the SEC value from a different CSV file
    # --------------------------------------------
    sec_file_path = os.path.join('SEC', 'data', 'form4transactions', 'summary', 'summary_data.csv')
    if not os.path.exists(sec_file_path):
        print(f"Error: '{sec_file_path}' not found.")
        exit(1)
    
    try:
        sec_df = pd.read_csv(sec_file_path, encoding=encoding)
        # print(f"Successfully read '{sec_file_path}' with encoding '{encoding}'")
    except Exception as e:
        print(f"Error reading '{sec_file_path}': {e}")
        exit(1)
    
    first_company = sec_df.iloc[0]
    insider_sentiment = first_company['sentiment_score']
    
    # --------------------------------------------
    # Run main(...) on each column and store results
    # --------------------------------------------
    results = []
    for col in df.columns:
        try:
            total_count, positive_percentage, negative_percentage, averageScore = main(df, col)
            results.append((col, total_count, positive_percentage, negative_percentage, averageScore))
        except Exception as e:
            print(f"Error processing column '{col}': {e}")
    
    # --------------------------------------------
    # Output the results
    # --------------------------------------------
    for col, total_count, positive_percentage, negative_percentage, avg_score in results:
        print(
            f"Column: {col}\n"
            f"Processed {total_count} entries\n"
            f"{positive_percentage:.2f}% were positive\n"
            f"{negative_percentage:.2f}% were negative\n"
            f"The average score (-1 to 1) was {avg_score:.2f}\n"
        )
    
    # --------------------------------------------
    # Calculate the weighted average for GoogleSearch, YouTube, and SEC
    # --------------------------------------------
    google_score = next((res[4] for res in results if res[0] == "GoogleSearch"), 0)
    youtube_score = next((res[4] for res in results if res[0] == "YouTube"), 0)
    
    weighted_average_score = (google_score * 0.5) + (youtube_score * 0.4) + (insider_sentiment * 0.1)
    print(f"The weighted average score is {weighted_average_score:.2f}")
