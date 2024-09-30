import pandas as pd


def print_csv_columns(file_path):
    try:
        # Read only the first row of the CSV to get the columns
        df = pd.read_csv(file_path, nrows=0)
        columns = df.columns.tolist()
        print("Columns in the CSV file:")
        for col in columns:
            print(col)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
