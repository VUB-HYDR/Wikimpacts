import pandas as pd

# List of columns to create individual DataFrames for
target_columns = [
    "Total Deaths",
    "No. Injured",
    "No. Affected",
    "No. Homeless",
    "Total Affected",
    "Insured Damage ('000 US$)",
    "Total Damage ('000 US$)",
]


def filter_and_save_dataframes(df, target_columns):
    """
    Filters the given DataFrame based on specified columns, saves each filtered DataFrame to a CSV,
    and appends them into a single DataFrame.

    Parameters:
    - df (pd.DataFrame): The input DataFrame to be filtered.
    - target_columns (list): List of columns to filter on and create individual DataFrames.

    Returns:
    - dict: A dictionary containing the resulting filtered DataFrames.
    - pd.DataFrame: A concatenated DataFrame of all filtered DataFrames.
    """
    resulting_dfs = {}

    # Loop through each column and create a new DataFrame where the column value is not None/NaN
    for column in target_columns:
        filtered_df = df[df[column].notna()].copy()
        # Generate a DataFrame name from the column name
        df_name = column.lower().replace(" ", "_").replace("('000_us$)", "").replace(".", "").replace(",", "")
        resulting_dfs[df_name] = filtered_df

        # Save each DataFrame to a CSV file
        filtered_df.to_csv(f"{df_name}.csv", index=False)

    # Append all filtered DataFrames together
    appended_df = pd.concat(resulting_dfs.values(), ignore_index=True)

    return resulting_dfs, appended_df
