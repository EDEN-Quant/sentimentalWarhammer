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

    # Initialize an empty DataFrame for aggregation
    aggregate_df = pd.DataFrame()
    
    # Concatenate each DataFrame side by side
    for idx, df in enumerate(data_frames):
        # Rename columns to avoid conflicts if needed
        df.columns = [f"{col}" for col in df.columns]
        
        # Join the current DataFrame to the aggregate DataFrame
        aggregate_df = pd.concat([aggregate_df, df], axis=1)

    # Save the aggregated DataFrame to the output file
    if not aggregate_df.empty:
        aggregate_df.to_csv(output_file, index=False)
        print(f"Aggregated data saved to {output_file}")
    else:
        print("No data to aggregate.")

if __name__ == "__main__":
    # Root directory where the data subdirectories are stored
    root_dir = "data"  # Adjust this to the path of your "data" directory
    
    # Output file for the aggregated data
    output_file = "output/aggregated_data.csv"  # Change this path if needed
    
    aggregate_csv_data(root_dir, output_file)
