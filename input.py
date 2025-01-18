import subprocess
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

def main():
    # Get the query from the user
    query = input("Enter the search query: ")

    # Define paths to the scripts
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # google_script = os.path.join(base_dir, "googleAPI.py")
    youtube_script = os.path.join(base_dir, "APIs", "youtube_api", "youtubeAPI.py")

    # Check if the scripts exist
    # if not os.path.exists(google_script):
    #     print(f"Error: {google_script} not found.")
    #     return

    if not os.path.exists(youtube_script):
        print(f"Error: {youtube_script} not found.")
        return

    # Run the Google script
    # google_process = subprocess.Popen(
    #     ["python", google_script, query],
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE
    # )

    # Run the YouTube script
    youtube_process = subprocess.Popen(
        ["python", youtube_script, query],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for both scripts to complete
    # google_stdout, google_stderr = google_process.communicate()
    youtube_stdout, youtube_stderr = youtube_process.communicate()

    # Print the outputs from both scripts
    # print("\n--- Google API Output ---")
    # print(google_stdout.decode())
    # if google_stderr:
    #     print("\nErrors:")
    #     print(google_stderr.decode())

    print("\n--- YouTube API Output ---")
    print(youtube_stdout.decode())
    if youtube_stderr:
        print("\nErrors:")
        print(youtube_stderr.decode())

    # Aggregate CSV files
    print("\nAggregating CSV files...")
    root_dir = os.path.join(base_dir, "data")  # Directory containing CSV files
    output_file = os.path.join(base_dir, "aggregated_data.csv")  # Output file path
    aggregate_csv_data(root_dir, output_file)

if __name__ == "__main__":
    main()
