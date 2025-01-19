import os

def delete_files_in_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

if __name__ == "__main__":
    data_directory = os.path.join(os.path.dirname(__file__), 'SEC', 'data')
    delete_files_in_directory(data_directory)
    print("Finished deleting files in the data directory.")