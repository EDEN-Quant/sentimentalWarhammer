import os
import pandas as pd

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
                    print(f"Could not read {file_path}: {e}")

    # Check if we have any data to aggregate
    if not data_frames:
        print("No CSV files found to aggregate.")
        return
    
    # Concatenate all DataFrames side by side
    try:
        aggregate_df = pd.concat(data_frames, axis=1)
    except Exception as e:
        print(f"Error during concatenation: {e}")
        return

    # Save the aggregated DataFrame to the output file
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        aggregate_df.to_csv(output_file, index=False)
        print(f"Aggregated data saved to {output_file}")
    except Exception as e:
        print(f"Could not save aggregated data: {e}")

if __name__ == "__main__":
    # Root directory where the data subdirectories are stored
    root_dir = "C:/Users/sebas/Desktop/ie_dev/IE_Year_3/EDEN/sentimentalWarhammer/data"  # Adjust this to the path of your "data" directory
    
    # Output file for the aggregated data
    output_file = "C:/Users/sebas/Desktop/ie_dev/IE_Year_3/EDEN/sentimentalWarhammer/aggregated_data.csv"
    
    aggregate_csv_data(root_dir, output_file)
