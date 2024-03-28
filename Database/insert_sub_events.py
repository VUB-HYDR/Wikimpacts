import sqlite3
import pandas as pd
import os

if __name__ == "__main__":

    output_path = "Database/output"
    sub_events = [f for f in os.listdir(output_path) if f.startswith("Specific_")]
    connection = sqlite3.connect(f"{output_path}/impact.db")
    cursor = connection.cursor()

    for i in sub_events:
        df = pd.read_parquet(f"{output_path}/{i}")
        sub_event_name = i.split(".")[0]
        df.to_sql(sub_event_name, con=connection, if_exists="replace", index=False)

    connection.close()