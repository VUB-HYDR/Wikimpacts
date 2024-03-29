import os
import sqlite3

import pandas as pd

if __name__ == "__main__":
    data_path = "Database/output"
    sub_events = [f for f in os.listdir(data_path) if f.startswith("Specific_")]
    connection = sqlite3.connect(f"{data_path}/impact.db")
    cursor = connection.cursor()

    for i in sub_events:
        df = pd.read_parquet(f"{data_path}/{i}")
        sub_event_name = i.split(".")[0]

        # change if_exists to "append" to avoid overwriting the database
        # choose "replace" to overwrite the database with a fresh copy of the data
        df.to_sql(sub_event_name, con=connection, if_exists="append", index=False)

    connection.close()
