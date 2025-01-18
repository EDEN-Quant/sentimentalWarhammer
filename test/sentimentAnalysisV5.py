from transformers import pipeline
import pandas as pd
import chardet

sentiment_pipeline = pipeline("sentiment-analysis", batch_size=32)

def main(dataset, colName): #colName used to select YouTube... columns

    # Convert the column to a list of strings
    sentences = dataset[colName].astype(str).tolist()

    # Apply the sentiment pipeline to the entire column in batches
    results = sentiment_pipeline(sentences)

    # Add results back to the dataset
    dataset['sentiment'] = [result['label'] for result in results]
    dataset['score'] = [result['score'] for result in results]

    dataset['adjustedScore'] = dataset.apply(lambda row: row['score'] if row['sentiment'] == "POSITIVE" else -row['score'], axis = 1)

    strong_positive = dataset[(dataset['sentiment'] == "POSITIVE") & (dataset['score'] > 0.85)]
    strong_negative = dataset[(dataset['sentiment'] == "NEGATIVE") & (dataset['score'] > 0.85)]

    # Calculate statistics
    positive_count = len(strong_positive)
    negative_count = len(strong_negative)
    total_count = len(dataset)
    positive_percentage = positive_count / total_count * 100
    negative_percentage = negative_count / total_count * 100

    averageScore = dataset['adjustedScore'].mean()

    print(
        f"Processed {total_count} entries\n"
        f"{positive_percentage:.2f}% were positive\n"
        f"{negative_percentage:.2f}% were negative\n"
        f"The average score (-1 to 1) was {averageScore:.2f}"
    )

    return total_count, positive_percentage, negative_percentage, averageScore

# Detect the encoding

with open('test.csv', 'rb') as f:
    result = chardet.detect(f.read(10000))
    encoding = result['encoding']

# Read the CSV file with the detected encoding

df = pd.read_csv('test.csv', encoding=encoding)
df = df.dropna()

main(df,"text")

