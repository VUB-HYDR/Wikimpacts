import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
from Database.scr.log_utils import Logging
import argparse
import pathlib
import re
import os
from pathlib import Path

if __name__ == "__main__":
    logger = Logging.get_logger("compare event with EM-DAT")
    
 

    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "-fed",
        "--filename_ed",
        dest="filename_ed",
        help="The name of the csv file of EM-DAT impact categories",
        type=str,
    )
    parser.add_argument(
        "-fp",
        "--filepath",
        dest="filepath",
        help="The path to save img",
        type=str,
    )

    parser.add_argument(
        "-fwiki",
        "--filename_wiki",
        dest="filename_wiki",
        help="The name of the csv file of Wikimpacts impact categories",
        type=str,
    )

    parser.add_argument(
        "-fl1",
        "--filename_wiki_L1",
        dest="filename_wiki_L1",
        help="The name of the csv file of Wikimpacts L1 ",
        type=str,
    )

    parser.add_argument(
        "-i",
        "--impact_category",
        dest="impact_category",
        help="The impact_category that need to compare, only 5 categories below allowed: injury, homeless, death, affected,damage ",
        type=str,
    )

    args = parser.parse_args()
    print(args)
    pathlib.Path(args.filepath).mkdir(parents=True, exist_ok=True)


    ed=pd.read_csv(f"{args.filename_ed}")
    wiki=pd.read_csv(f"{args.filename_wiki}")
    L1=pd.read_csv(f"{args.filename_wiki_L1}")
    # for bar chart, flood is all, but tropical storm etc is follow the same name, and storm including all the storms excluding sand storm 
    mapping = {
        'riverine flood': 'Flood',
        'tropical cyclone': 'Tropical Storm/Cyclone',
        'flood (general)': 'Flood',
        'storm (general)': 'Storm',
        'flash flood': 'Flood',
        'drought': 'Drought',
        'forest fire': 'Wildfire',
        'wildfire (general)': 'Wildfire',
        'cold wave': 'Extreme Temperature',
        'tornado': 'Tornado',
        'severe weather': 'Storm',
        'heat wave': 'Extreme Temperature',
        'blizzard/winter storm': 'Storm',
        'lightning/thunderstorms': 'Storm',
        'extra-tropical storm': 'Extratropical Storm/Cyclone',
        'hail': 'Storm',
        'land fire (brush, bush, pasture)': 'Wildfire',
        'coastal flood': 'Flood',
        'severe winter conditions': 'Extreme Temperature',
        'storm surge': 'Flood',
        'sand/dust storm': 'Other',
        'glacial lake outburst flood': 'Flood'
    }



    ed['Disaster Subtype'] = ed['Disaster Subtype'].str.lower()
    keywords = [word.lower() for word in [
        "flood", "storm", "tropical cyclone", "drought", "forest fire",
        "cold wave", "tornado", "severe weather", "heat wave", "blizzard/winter storm",
        "lightning/thunderstorms", "hail", "land fire (brush, bush, pasture)", 
        "severe winter conditions", "wildfire"
    ]]

    ed_filter = ed[
        ed['Disaster Subtype'].apply(lambda subtype: any(keyword in subtype for keyword in keywords))
    ]

    # Map the 'Disaster Subtype' to a new column using the mapping1 dictionary
    ed_filter["Disaster_Type_Map_Wiki"] = ed_filter["Disaster Subtype"].map(mapping)

    # OPTIONAL: To handle NaN values if any Disaster Subtype does not match the mapping
    ed_filter["Disaster_Type_Map_Wiki"].fillna("Other", inplace=True)

    wiki = wiki.merge(
    L1[['Event_ID', 'Main_Event']],  # Selecting the relevant columns
    on='Event_ID',  # Based on the common Event_ID
    how='left'  # Use left join to keep all rows in 'wiki'
)


    # Normalize event types
    wiki['Main_Event_norm'] = wiki['Main_Event'].astype(str).str.strip().str.lower()
    ed_filter['Disaster_Type_Map_Wiki_norm'] = ed_filter['Disaster_Type_Map_Wiki'].astype(str).str.strip().str.lower()

    # Extract ISO3 from wiki Administrative_Areas_GID
    def iso3_from_gid(gid):
        s = str(gid)
        if s.lower() == 'nan':
            return np.nan
        m = re.match(r'^([A-Za-z]{3})\.', s)
        if m:
            return m.group(1).upper()
        letters = re.findall(r'[A-Za-z]', s)
        return ''.join(letters[:3]).upper() if letters else np.nan

    def iter_flat(x):
        if isinstance(x, (list, tuple, set)):
            for i in x:
                yield from iter_flat(i)
        elif isinstance(x, np.ndarray):
            for i in x.ravel():
                yield from iter_flat(i)
        else:
            yield x

    def build_iso_list(x):
        isos = set()
        for g in iter_flat(x):
            if g is None:
                continue
            s = str(g).strip()
            if not s or s.lower() == 'nan':
                continue
            iso = iso3_from_gid(s)
            if isinstance(iso, str) and iso and iso.lower() != 'nan':
                isos.add(iso)
        return list(isos)

    wiki['ISO_list'] = wiki['Administrative_Areas_GID'].apply(build_iso_list)
    wiki_exp = wiki.explode('ISO_list').rename(columns={'ISO_list': 'ISO'})
    wiki_exp['ISO'] = wiki_exp['ISO'].astype(str).str.upper()
    wiki_exp = wiki_exp[wiki_exp['ISO'].notna() & (wiki_exp['ISO'] != 'NAN') & (wiki_exp['ISO'] != '')]

    # Normalize ISO in ed_filter
    ed_filter = ed_filter.copy()
    ed_filter['ISO'] = ed_filter['ISO'].astype(str).str.upper()
    # Build start and end year keys safely
    def build_year(df, start_col, end_col, start_out, end_out):
        start_y = pd.to_numeric(df[start_col], errors='coerce')
        end_y = pd.to_numeric(df[end_col], errors='coerce')
        df[start_out] = start_y.astype('Int64')
        df[end_out] = end_y.astype('Int64')

    # Apply to both datasets
    build_year(ed_filter, 'Start Year', 'End Year', 'start_year_key', 'end_year_key')
    build_year(wiki_exp, 'Start_Date_Year', 'End_Date_Year', 'start_year_key', 'end_year_key')

    # Keep IDs to deduplicate/trace
    wiki_exp = wiki_exp.reset_index(drop=True)
    ed_filter = ed_filter.reset_index(drop=True)
    wiki_exp['inj_idx'] = pd.array(np.arange(len(wiki_exp)), dtype='Int64')
    ed_filter['ed_idx'] = pd.array(np.arange(len(ed_filter)), dtype='Int64')

    # Year-level matches with start and end year
    inj_year = wiki_exp[wiki_exp['start_year_key'].notna() & wiki_exp['end_year_key'].notna()]
    ed_year = ed_filter[ed_filter['start_year_key'].notna() & ed_filter['end_year_key'].notna()]

    year_matches = inj_year.merge(
        ed_year,
        left_on=['Main_Event_norm', 'ISO', 'start_year_key', 'end_year_key'],
        right_on=['Disaster_Type_Map_Wiki_norm', 'ISO', 'start_year_key', 'end_year_key'],
        how='inner',
        suffixes=('_inj', '_ed')
    )

    # Build start and end year/month keys safely
    def build_year_month(df, start_year_col, end_year_col, start_month_col, end_month_col, start_out, end_out):
        start_y = pd.to_numeric(df[start_year_col], errors='coerce')
        end_y = pd.to_numeric(df[end_year_col], errors='coerce')
        start_m = pd.to_numeric(df[start_month_col], errors='coerce')
        end_m = pd.to_numeric(df[end_month_col], errors='coerce')
        
        df[start_out] = start_y.astype('Int64') * 100 + start_m.fillna(0).astype('Int64')
        df[end_out] = end_y.astype('Int64') * 100 + end_m.fillna(0).astype('Int64')

    # Apply to both datasets
    build_year_month(ed_filter, 'Start Year', 'End Year', 'Start Month', 'End Month', 'start_ym_key', 'end_ym_key')
    build_year_month(wiki_exp, 'Start_Date_Year', 'End_Date_Year', 'Start_Date_Month', 'End_Date_Month', 'start_ym_key', 'end_ym_key')

    # Keep IDs to deduplicate/trace
    wiki_exp = wiki_exp.reset_index(drop=True)
    ed_filter = ed_filter.reset_index(drop=True)
    wiki_exp['inj_idx'] = pd.array(np.arange(len(wiki_exp)), dtype='Int64')
    ed_filter['ed_idx'] = pd.array(np.arange(len(ed_filter)), dtype='Int64')

    # Year/Month-level matches with start and end year/month
    inj_ym = wiki_exp[wiki_exp['start_ym_key'].notna() & wiki_exp['end_ym_key'].notna()]
    ed_ym = ed_filter[ed_filter['start_ym_key'].notna() & ed_filter['end_ym_key'].notna()]

    ym_matches = inj_ym.merge(
        ed_ym,
        left_on=['Main_Event_norm', 'ISO', 'start_ym_key', 'end_ym_key'],
        right_on=['Disaster_Type_Map_Wiki_norm', 'ISO', 'start_ym_key', 'end_ym_key'],
        how='inner',
        suffixes=('_inj', '_ed')
    )
   # get the impact column from em-dat 
    def prepare_numeric_for_plot(df, impact_type):
        df = df.copy()
        
        # Map impact type to column names
        impact_column_map = {
            'injury': 'No. Injured',
            'death': 'Total Deaths',
            'affected': 'No. Affected',
            'damage': "Total Damage ('000 US$)",
            'homeless': 'No. Homeless'
        }
        
        impact_col = None
        if impact_type and impact_type in impact_column_map:
            col = impact_column_map[impact_type]
            if col in df.columns:
                impact_col = col
                print(f"impact_col is {impact_col}")
        
        if impact_col:
            df['impact_num'] = pd.to_numeric(df[impact_col], errors='coerce')
        
        for col in ['Num_Min', 'Num_Max']:
            if col in df.columns:
                df[col + '_num'] = pd.to_numeric(df[col], errors='coerce')
        
        return df.dropna(subset=['impact_num']) if 'impact_num' in df.columns else df
    def clean_title(title):
        # Replace special characters and spaces
        return title.replace(' ', '_').replace('/', '-')
    def scatter_impact_with_error_bars(df, title,impact_type,filepath):
        dfp = prepare_numeric_for_plot(df,impact_type)
        print(dfp.columns)
        if dfp.empty:
            print(f"No data to plot for: {title}")
            return
        
        plt.figure(figsize=(10, 8))

        # Plot ED No. Injured
        plt.scatter(dfp['impact_num'], dfp['impact_num'], alpha=0.5, label=f'EM-DAT {impact_type} values', color='tab:green', marker='^')

        # Calculate mid-point and error bars
        mid_point = (dfp['Num_Min_num'] + dfp['Num_Max_num']) / 2
        yerr = [mid_point - dfp['Num_Min_num'], dfp['Num_Max_num'] - mid_point]
        
        # Plot error bars for Num_Min and Num_Max
        plt.errorbar(
            dfp['impact_num'], 
            mid_point,
            yerr=yerr,
            fmt='o',
            color='darkblue',
            ecolor='lightblue',
            elinewidth=2,
            capsize=3,
            alpha=0.6,
            label=f'{impact_type.capitalize()} Range'
        )
        
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel(f"EM-DAT {impact_type} in log scale")
        plt.ylabel(f"Wikimpacts {impact_type} range in log scale")
        plt.title(title)
        plt.legend()
        plt.grid(True, which="both", linestyle='--', linewidth=0.5)
        plt.tight_layout()
        save_title=clean_title(title)
        plt.savefig(f'{filepath}/{save_title}.png')
        plt.close()

   
    # Plot scatter with the updated ym_matches
    unique_events_ym = ym_matches['Main_Event_norm'].unique()

    for event in unique_events_ym:
        filtered_df = ym_matches[ym_matches['Main_Event_norm'] == event]
        scatter_impact_with_error_bars(filtered_df, f"Wikimpacts vs EM-DAT (Year/Month-level matches) {args.impact_category} - {event.capitalize()}",args.impact_category,args.filepath)
    
    #plot only year match 
    unique_events_y = year_matches['Main_Event_norm'].unique()

    for event in unique_events_y:
        filtered_df = year_matches[year_matches['Main_Event_norm'] == event]
        scatter_impact_with_error_bars(filtered_df, f"Wikimpacts vs EM-DAT (Year-level matches) {args.impact_category} - {event.capitalize()}",args.impact_category,args.filepath)
    
