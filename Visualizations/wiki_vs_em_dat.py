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
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import MaxNLocator
from matplotlib import rcParams
# Define custom colors for each event
custom_colors = {
    "Flood": "#76b947",  #  A navy blue.
    "Drought": "#FFD29D",  #  A light peach or pastel orange.
    "Wildfire": "#ff8882",  # A light pink.
    "Tornado": "#918450",  # A muted khaki or olive color.
    "Extratropical Storm/Cyclone": "#00619c",  # A vivid turquoise or teal.
    "Tropical Storm/Cyclone": "#00AFB9",  # A medium blue-gray or steel blue.-green
    "Extreme Temperature": "#A41623",  # A deep, dark red or crimson.
}
# Set the font path
font_path = "/user/brussel/106/vsc10684/bvo00012/vsc10684/WikimpactsV1/Wikimpacts/Visualizations/fonts/DejaVuSerif.ttf"


font_prop = FontProperties(fname=font_path)

# Set Seaborn aesthetics
#sns.set(style="whitegrid")
# Set font style and size globally
plt.rcParams['font.family'] = font_prop.get_name()


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
        # Get unique records from inj_ym that are not in the inner merge result
    unique_inj = inj_ym[~inj_ym.set_index(['Main_Event_norm', 'ISO', 'start_ym_key', 'end_ym_key']).index.isin(
        ym_matches.set_index(['Main_Event_norm', 'ISO', 'start_ym_key', 'end_ym_key']).index)]
    
    # Get unique records from ed_ym that are not in the inner merge result
    unique_ed = ed_ym[~ed_ym.set_index(['Disaster_Type_Map_Wiki_norm', 'ISO', 'start_ym_key', 'end_ym_key']).index.isin(
        ym_matches.set_index(['Disaster_Type_Map_Wiki_norm', 'ISO', 'start_ym_key', 'end_ym_key']).index)]
    
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
                #print(f"impact_col is {impact_col}")
        
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
    """
    def event_impact_with_error_bars(df, title, impact_type, filepath):
        dfp = prepare_numeric_for_plot(df,impact_type)
                
        if dfp.empty:
            print(f"No data to plot for: {title}")
            return
        
        plt.figure(figsize=(14, 8)) # Make it wide to accommodate many events

        # Sort the dataframe for a cleaner plot
        df_sorted = dfp.sort_values('impact_num').reset_index()
        
        for i, row in df_sorted.iterrows():
            min_val = row['Num_Min_num']
            max_val = row['Num_Max_num']
            em_dat_val = row['impact_num']
            
            plt.plot([i, i], [min_val, max_val], 'blue', alpha=1)
            
            # Use different marker for perfect matches
            if min_val == max_val == em_dat_val:
                plt.plot(i, em_dat_val, 's', color='green', markersize=8, markeredgewidth=2, markeredgecolor='black')  # Square marker
            else:
                plt.plot(i, em_dat_val, 'o', color='orange', markersize=6)

        plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        plt.xlabel(f'Event Index (Sorted by EM-DAT {impact_type} Value)')
        plt.ylabel(f'{impact_type} Value')
        #plt.yscale('log') # Add this line to your plotting code
        plt.title(title)
        plt.legend([f'Wikimpacts {impact_type.capitalize} Min-Max Range', f'EM-DAT {impact_type.capitalize} Value'])
        plt.grid(True)
        plt.xticks([]) # Hide the x-axis ticks as they are just indices
        plt.tight_layout()
        save_title=clean_title(title)
        plt.savefig(f'{filepath}/{save_title}.png')
        plt.close()
    
    def event_impact_with_error_bars(df, title, impact_type, filepath):
        dfp = prepare_numeric_for_plot(df,impact_type)
                
        if dfp.empty:
            print(f"No data to plot for: {title}")
            return
        
        #plt.figure(figsize=(14, 8)) # Make it wide to accommodate many events
        # only filter rows where the Num_Unit is USD 
        #df_USD=dfp[dfp["Num_Unit"]=="USD"]
        df_sorted = dfp.sort_values('impact_num').reset_index(drop=True)
        print(f"lenth of matched events {len(df_sorted)}")
      

        fig, ax = plt.subplots(figsize=(14, 8))
        range_lbl_shown = False
        single_lbl_shown = False
        em_lbl_shown = False
        perfect_lbl_shown = False
        mins = df_sorted['Num_Min_num'].to_numpy(dtype=float)
        maxs = df_sorted['Num_Max_num'].to_numpy(dtype=float)
        em   = df_sorted['impact_num'].to_numpy(dtype=float)
        mn = np.minimum(mins, maxs)
        mx = np.maximum(mins, maxs)
        dist = np.where((em >= mn) & (em <= mx), 0.0, np.minimum(np.abs(em - mn), np.abs(em - mx)))
        rmse = float(np.sqrt(np.mean(dist**2)))
        print(f"rmse for {impact_type} {rmse}")
       
        for i, row in df_sorted.iterrows():
            min_val = int(row['Num_Min_num'])
            max_val = int(row['Num_Max_num'])
            em_val  = int(row['impact_num'])
        
            # Skip bad rows
            if not (np.isfinite(min_val) and np.isfinite(max_val) and np.isfinite(em_val)):
                continue

            # Ensure correct order
            if max_val < min_val:
                min_val, max_val = max_val, min_val

            # Draw Wiki min–max range or single-value dot
            if max_val > min_val:
                ax.vlines(
                    i, min_val, max_val, color='blue', alpha=0.9, linewidth=2, zorder=3,
                    label=(f'Wikimpacts {impact_type.capitalize()} Min–Max Range' if not range_lbl_shown else None)
                )
                range_lbl_shown = True
            else:
                # min == max: show a Wiki dot
                ax.scatter(
                    i, min_val, color='royalblue', s=25, zorder=3,
                    label=(f'Wikimpacts {impact_type.capitalize()} Value' if not single_lbl_shown else None)
                )
                single_lbl_shown = True

            # Highlight perfect matches (optional)
            # Highlight perfect matches (optional)
            if min_val == max_val == em_val:
                    ax.scatter(
                    i, em_val, marker='s', color='green', s=45,
                    edgecolor='black', linewidth=1, zorder=5,
                    label='Perfect Match' if not perfect_lbl_shown else None
                    )
                    perfect_lbl_shown = True
            # EM-DAT point
            ax.scatter(
                i, em_val, color='orange', s=25, zorder=4,
                label=(f'EM-DAT {impact_type.capitalize()} Value' if not em_lbl_shown else None)
            )
            em_lbl_shown = True
           

        ax.axhline(0, color='k', linestyle='-', alpha=0.3)
        linthresh_value = np.percentile(df_sorted['impact_num'], 50)  # 50th percentile = median
        ax.set_xlabel(f'Event Index (Sorted by EM-DAT {impact_type.capitalize()} Value, symlog, line scale threshold {linthresh_value})')
        ax.set_ylabel(f'{impact_type.capitalize()} Value (symlog, line scale threshold {linthresh_value} )')
        #ax.axhline(rmse, color='crimson', linestyle='--', linewidth=2, label=f'RMSE = {rmse:.2f}')
        ax.set_title(title)
        #ax2 = ax.twinx()
        #x = np.arange(len(em))
       # ax2.bar(x, dist, color='crimson', alpha=0.25, width=0.8, label=f'Distance to Wikimpacts {impact_type.capitalize()} range')
        #ax2.axhline(rmse, color='crimson', linestyle='--', linewidth=2, label=f'RMSE = {rmse:.2f}')
        #ax2.set_ylabel(f'Distance to Wikimpacts {impact_type.capitalize()} range')
        #ax2.set_ylim(0, np.nanpercentile(dist, 99) * 1.1)
        # Make small ranges visible:
        
        ax.set_yscale('symlog', linthresh=linthresh_value,linscale=1.0)  # or use ax.set_ylim(top=np.nanpercentile(df_sorted[['Num_Max_num','impact_num']].to_numpy(), 99))
        # ax.set_ylim(0, np.nanpercentile(np.r_[df_sorted['Num_Max_num'], df_sorted['impact_num']], 99))
        ax.set_ylim(bottom=0.1)  # Set minimum to a small positive value
        ax.grid(True)
        ax.set_xticks([])
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.tight_layout()
        #h1, l1 = ax.get_legend_handles_labels()
        #h2, l2 = ax2.get_legend_handles_labels()
        #ax2.legend(h1 + h2, l1 + l2, loc='upper left')
        save_title = clean_title(title)
        plt.savefig(f'{filepath}/{save_title}.png')
        plt.close()
    
    def event_impact_with_error_bars(df, title, impact_type, filepath):
        dfp = prepare_numeric_for_plot(df, impact_type)

        if dfp.empty:
            print(f"No data to plot for: {title}")
            return

        # Check if impact type is "Damage" and filter for USD
        if impact_type.lower() == "damage":
            dfp = dfp[dfp["Num_Unit"] == "USD"]
            if dfp.empty:
                print(f"No USD data to plot for: {title}")
                return

        # Sort the filtered data
        df_sorted = dfp.sort_values('impact_num').reset_index(drop=True)
        print(f"Length of matched events: {len(df_sorted)}")

        fig, ax = plt.subplots(figsize=(14, 8))
        em_lbl_shown = False
        perfect_lbl_shown = False

        # Calculate mean for Wiki values
        wiki_mean = (df_sorted['Num_Min_num'] + df_sorted['Num_Max_num']) / 2

        # Calculate RMSE using the mean instead of range
        em = df_sorted['impact_num'].to_numpy(dtype=float)
        dist = np.abs(em - wiki_mean.to_numpy(dtype=float))
        rmse = float(np.sqrt(np.mean(dist**2)))
        print(f"RMSE for {impact_type}: {rmse}")

        for i, row in df_sorted.iterrows():
            em_val = int(row['impact_num'])
            wiki_val = (row['Num_Min_num'] + row['Num_Max_num']) / 2

            if not np.isfinite(wiki_val) or not np.isfinite(em_val):
                continue

            # Plot Wiki mean value
            ax.scatter(
                i, wiki_val, color='royalblue', s=25, zorder=3,
                label=f'Wikimpacts {impact_type.capitalize()} Value Average' if i == 0 else None
            )

            # Highlight perfect matches
            if wiki_val == em_val:
                ax.scatter(
                    i, em_val, marker='s', color='green', s=45,
                    edgecolor='black', linewidth=1, zorder=5,
                    label='Perfect Match' if not perfect_lbl_shown else None
                )
                perfect_lbl_shown = True

            # Plot EM-DAT value
            ax.scatter(
                i, em_val, color='orange', s=25, zorder=4,
                label=f'EM-DAT {impact_type.capitalize()} Value' if not em_lbl_shown else None
            )
            em_lbl_shown = True

        # Label and plot configuration
        ax.axhline(0, color='k', linestyle='-', alpha=0.3)
        linthresh_value = np.percentile(df_sorted['impact_num'], 50)
        ax.set_xlabel(f'Event Index (Sorted by EM-DAT {impact_type.capitalize()} Value, symlog, scale threshold {linthresh_value})')
        ax.set_ylabel(f'{impact_type.capitalize()} Value{" ($)" if impact_type == "Damage" else ""} (symlog, scale threshold {linthresh_value})')
        ax.set_title(title)

        ax.set_yscale('symlog', linthresh=linthresh_value, linscale=1.0)
        ax.set_ylim(bottom=0.1)
        ax.grid(True)
        ax.set_xticks([])
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.tight_layout()

        save_title = clean_title(title)
        plt.savefig(f'{filepath}/{save_title}.png')
        plt.close()
    
  
    def event_impact_benchmark_comparison(df, title, impact_type, filepath):
        dfp = prepare_numeric_for_plot(df, impact_type)

        if dfp.empty:
            print(f"No data to plot for: {title}")
            return

        # Filter for USD if impact type is "Damage"
        if impact_type.lower() == "damage":
            dfp = dfp[dfp["Num_Unit"] == "USD"]
            if dfp.empty:
                print(f"No USD data to plot for: {title}")
                return

        # Sort the filtered data
        df_sorted = dfp.sort_values('impact_num').reset_index(drop=True)
        wiki_means = (df_sorted['Num_Min_num'] + df_sorted['Num_Max_num']) / 2

        # Calculate differences
        em = df_sorted['impact_num']
        differences = (wiki_means - em) / em

        # Categorize differences
        categories = {
            'Perfect match': (differences == 0),
            '5% more': (differences > 0.05) & (differences <= 0.10),
            '10% more': (differences > 0.10) & (differences <= 0.15),
            '15% more': (differences > 0.15),
            '5% less': (differences < -0.05) & (differences >= -0.10),
            '10% less': (differences < -0.10) & (differences >= -0.15),
            '15% less': (differences < -0.15)
        }

        counts = {label: df_sorted[mask].shape[0] for label, mask in categories.items()}

        # Plot bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(counts.keys(), counts.values(), color='orange')

        # Configure plot aesthetics
        ax.set_title(title)
        ax.set_ylabel('Count of events')
        ax.set_xlabel(f'Level of Wikimpacts {impact_type} impact difference, based on EM-DAT values')
        ax.set_xticklabels(counts.keys(), rotation=45, ha='right')
        ax.grid(False)

        save_title = clean_title(title)
        plt.tight_layout()
        plt.savefig(f'{filepath}/{save_title}.png')
        plt.close()
"""
     # Define colors as per the event type
    custom_colors = {
            "flood": "#76b947",
            "drought": "#FFD29D",
            "wildfire": "#ff8882",
            "tornado": "#918450",
            "extratropical storm/cyclone": "#00619c",
            "tropical storm/cyclone": "#00AFB9",
            "extreme temperature": "#A41623",
        }
    


    cmap_colors = [
        '#16488f',  #  blue for 15% less
        '#4393c3',  # Medium blue for 10% less
        '#d9e4ec',  # Lighter blue for 5% less
        '#D3D3D3',  # Grey for Perfect Match
        '#f6a096',  # Light salmon for 5% more
        '#d92d2b',  # Strong red for 10% more
        '#800000'   #  red for 15% more
    ]

    def event_impact_benchmark_comparison(df, title, impact_type, filepath):
        dfp = prepare_numeric_for_plot(df, impact_type)

        if dfp.empty:
            print(f"No data to plot for: {title}")
            return

        # Filter for USD if impact type is "Damage"
        if impact_type.lower() == "damage":
            dfp = dfp[dfp["Num_Unit"] == "USD"]
            if dfp.empty:
                print(f"No USD data to plot for: {title}")
                return

        # Sort the filtered data
        df_sorted = dfp.sort_values('impact_num').reset_index(drop=True)
        wiki_means = (df_sorted['Num_Min_num'] + df_sorted['Num_Max_num']) / 2

        # Calculate differences
        em = df_sorted['impact_num']
        differences = (wiki_means - em) / em

        # Categorize differences
        categories = {
            '50% less': (differences < -0.50),
            '30% less': (differences < -0.30) & (differences >= -0.50),
            '10% less': (differences < -0.1) & (differences >= -0.30),
            'Perfect match': (differences == 0),
            '10% more': (differences > 0.1) & (differences <= 0.30),
            '30% more': (differences > 0.30) & (differences <= 0.50),
            '50% more': (differences > 0.50),
        }

        counts = {label: df_sorted[mask].shape[0] for label, mask in categories.items()}

        # Map colors to categories
        category_colors = {
            '50% less': cmap_colors[0],
            '30% less': cmap_colors[1],
            '10% less': cmap_colors[2],
            'Perfect match': cmap_colors[3],
            '10% more': cmap_colors[4],
            '30% more': cmap_colors[5],
            '50% more': cmap_colors[6],
        }

        # Plot bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(counts.keys(), counts.values(), color=[category_colors[label] for label in counts.keys()])

        # Configure plot aesthetics
        ax.set_title(title)
        ax.set_ylabel('Count of events')
        ax.set_xlabel(f'Level of Wikimpacts {impact_type} impact difference, based on EM-DAT values')
        ax.set_xticks(range(len(counts)))
        ax.set_xticklabels(counts.keys(), rotation=0, ha='center')
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(False)

        save_title = clean_title(title)
        plt.tight_layout()
        plt.savefig(f'{filepath}/{save_title}.png')
        plt.close()

# Example usage
# for event in unique_events_ym:
#     filtered_df = ym_matches[ym_matches['Main_Event_norm'] == event]
#     event_impact_benchmark_comparison(filtered_df, f"Wikimpacts 1.0 vs EM-DAT {args.impact_category} impact comparison - {event}", args.impact_category, args.filepath)
    """
    def event_impact_benchmark_comparison(df, title, impact_type, filepath):
        dfp = prepare_numeric_for_plot(df, impact_type)

        if dfp.empty:
            print(f"No data to plot for: {title}")
            return

        # Filter for USD if impact type is "Damage"
        if impact_type.lower() == "damage":
            dfp = dfp[dfp["Num_Unit"] == "USD"]
            if dfp.empty:
                print(f"No USD data to plot for: {title}")
                return

        # Sort the filtered data
        df_sorted = dfp.sort_values('impact_num').reset_index(drop=True)
        wiki_means = (df_sorted['Num_Min_num'] + df_sorted['Num_Max_num']) / 2

        # Calculate differences
        em = df_sorted['impact_num']
        differences = (wiki_means - em) / em

        # Categorize differences
        categories = {
            '15% less': (differences < -0.15),
            '10% less': (differences < -0.10) & (differences >= -0.15),
            '5% less': (differences < -0.05) & (differences >= -0.10),
            'Perfect match': (differences == 0),
            '5% more': (differences > 0.05) & (differences <= 0.10),
            '10% more': (differences > 0.10) & (differences <= 0.15),
            '15% more': (differences > 0.15),
            
            
            
        }

        counts = {label: df_sorted[mask].shape[0] for label, mask in categories.items()}

   

        # Determine event type for setting the color
        event_type = dfp.iloc[0]['Main_Event_norm'] if not dfp.empty else "default"

        # Get color for the specific event type
        event_color = custom_colors.get(event_type, '#333333')

        # Plot bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(counts.keys(), counts.values(), color=event_color)

        # Configure plot aesthetics
        ax.set_title(title)
        ax.set_ylabel('Count of events')
        ax.set_xlabel(f'Level of Wikimpacts {impact_type} impact difference, based on EM-DAT values')
        ax.set_xticklabels(counts.keys(), rotation=0, ha='center')
        ax.grid(False)
        # Ensure only integer values on y-axis
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        save_title = clean_title(title)
        plt.tight_layout()
        plt.savefig(f'{filepath}/{save_title}.png')
        plt.close()
    """
# Example usage
# for event in unique_events_ym:
#     filtered_df = ym_matches[ym_matches['Main_Event_norm'] == event]
#     event_impact_benchmark_comparison(filtered_df, f"Wikimpacts 1.0 vs EM-DAT {args.impact_category} impact comparison - {event}", args.impact_category, args.filepath)
# Example usage
# event_impact_benchmark_comparison(your_dataframe, "Title of Plot", "Damage", "path/to/save")
    # Plot scatter with the updated ym_matches
    #unique_events_ym = ym_matches['Main_Event_norm'].unique()
    
    def plot_dismatch(filepath, impact_type, title):
        selected_event_types = [
            "Flood",
            "Drought",
            "Wildfire",
            "Tornado",
            "Extratropical Storm/Cyclone",
            "Tropical Storm/Cyclone",
            "Extreme Temperature"
        ]
        selected_event_types_x_lable = [
            "Flood",
            "Drought",
            "Wildfire",
            "Tornado",
            "Extrat. Cycl",
            "Trop. Cycl",
            "Extr. Temp."
        ]
        # Count occurrences for unique events in inj_ym
        count_inj = unique_inj['Main_Event_norm'].value_counts().reset_index()
        count_inj.columns = ['Event_Type', 'Count_Wikimpacts']

        # Count occurrences for unique events in ed_ym
        count_ed = unique_ed['Disaster_Type_Map_Wiki_norm'].value_counts().reset_index()
        count_ed.columns = ['Event_Type', 'Count_EM-DAT']

        # Merge the counts on Event_Type
        combined_counts = pd.merge(count_inj, count_ed, on='Event_Type', how='outer').fillna(0)

        # Set the Event_combined_counts = pd.merge(count_inj, count_ed, on='Event_Type', how='outer').fillna(0)

        # Filter to keep only event types present in the Wiki dataset
        main_event_types = count_inj['Event_Type']
        filtered_counts = combined_counts[combined_counts['Event_Type'].isin(main_event_types)]

        filtered_counts.set_index('Event_Type', inplace=True)

        # Plotting
        ax = filtered_counts.plot(kind='bar', figsize=(12, 6), width=0.8)

        # Adding titles and labels
        plt.title(title)
        #plt.xlabel('Event Type')
        plt.ylabel('Number of events')
        plt.xticks(rotation=45)
        plt.legend(title='Data Source', loc='upper right')

        # Show plot
        plt.tight_layout()
        plt.savefig(f'{filepath}/{impact_type}_dismatch.png')
    

   
    def plot_dismatch(filepath, impact_type, title):
        selected_event_types = [
            "flood",
            "drought",
            "wildfire",
            "tornado",
            "extratropical storm/cyclone",
            "tropical storm/cyclone",
            "extreme temperature"
        ]

        selected_event_types_x_label = [
            "Flood",
            "Drought",
            "Wildfire",
            "Tornado",
            "Extrat. Cycl",
            "Trop. Cycl",
            "Extr. Temp."
        ]
        
        

        # Create a mapping for event types to labels
        label_map = dict(zip(selected_event_types, selected_event_types_x_label))

        # Count occurrences for unique events in inj_ym
        count_inj = unique_inj['Main_Event_norm'].value_counts().reset_index()
        count_inj.columns = ['Event_Type', 'Count_Wikimpacts']

        # Count occurrences for unique events in ed_ym
        count_ed = unique_ed['Disaster_Type_Map_Wiki_norm'].value_counts().reset_index()
        count_ed.columns = ['Event_Type', 'Count_EM-DAT']

        # Merge the counts on Event_Type
        combined_counts = pd.merge(count_inj, count_ed, on='Event_Type', how='outer').fillna(0)

        # Filter to keep only event types present in the Wiki dataset
        
        filtered_counts = combined_counts[combined_counts['Event_Type'].isin(selected_event_types)]

        filtered_counts.set_index('Event_Type', inplace=True)

        # Plotting
        fig, ax = plt.subplots(figsize=(12, 6))

        index = np.arange(len(filtered_counts))
        bar_width = 0.4
 # Plot for EM-DAT with white hatching
        bars = ax.bar(
            index - bar_width / 2, 
           
            filtered_counts['Count_EM-DAT'], 
            width=bar_width, 
            color=[custom_colors.get(et, '#555555') for et in filtered_counts.index],  # Transparent face
            edgecolor="white",
            hatch="//",
            label='EM-DAT'
        )
        # Plot for Wikimpacts
        ax.bar(
             index + bar_width / 2, 
            filtered_counts['Count_Wikimpacts'], 
            width=bar_width, 
            color=[custom_colors.get(et, '#333333') for et in filtered_counts.index],
            label='Wikimpacts 1.0',
             edgecolor="black",
        )

       



       


        # Setting custom x-tick labels
        ax.set_xticklabels([label_map.get(et, et) for et in filtered_counts.index])

        # Adding titles and labels
        plt.title(title)
        plt.ylabel('Number of events')
        plt.xticks(rotation=0)
        plt.legend(title='Data Source', loc='upper right')

        # Show plot
        plt.tight_layout()
        plt.savefig(f'{filepath}/{impact_type}_dismatch.png')

        # Clean up
        plt.close()

# Use the function
# plot_dismatch(filepath, impact_type, title)
        
    #for event in unique_events_ym:
     #   filtered_df = ym_matches[ym_matches['Main_Event_norm'] == event]
    #    scatter_impact_with_error_bars(filtered_df, f"Wikimpacts vs EM-DAT (Year/Month-level matches) {args.impact_category} - {event.capitalize()}",args.impact_category,args.filepath)
    
    #plot only year match 
    #unique_events_y = year_matches['Main_Event_norm'].unique()

    #for event in unique_events_y:
    #    filtered_df = year_matches[year_matches['Main_Event_norm'] == event]
    #    scatter_impact_with_error_bars(filtered_df, f"Wikimpacts vs EM-DAT (Year-level matches) {args.impact_category} - {event.capitalize()}",args.impact_category,args.filepath)
     
     # Plot event impact comparison with the updated ym_matches
    #unique_events_ym = ym_matches['Main_Event_norm'].unique()

    #for event in unique_events_ym:
      #  print(f"for event {event}, print the matched impact values")
      #  filtered_df = ym_matches[ym_matches['Main_Event_norm'] == event]
      #  event_impact_with_error_bars(filtered_df, f"Wikimpacts 1.0 vs EM-DAT {args.impact_category} impact Comparison per Event  - {event.capitalize()}",args.impact_category,args.filepath)
    
   # for event in unique_events_ym:
      #  print(f"for event {event}, print the matched impact values")
      #  filtered_df = ym_matches[ym_matches['Main_Event_norm'] == event]
      #  event_impact_benchmark_comparison(filtered_df, f"Wikimpacts 1.0 vs EM-DAT {args.impact_category} impact comparison - {event}",args.impact_category,args.filepath)
    
    event_impact_benchmark_comparison(ym_matches, f"Wikimpacts 1.0 vs EM-DAT {args.impact_category} impact comparison",args.impact_category,args.filepath)
    
    #plot_dismatch(args.filepath, args.impact_category,f"Number of dismatch event entries between Wikimpacts 1.0 and EM-DAT in {args.impact_category} category")
    #plot only year match 
    #unique_events_y = year_matches['Main_Event_norm'].unique()

   # for event in unique_events_y:
      #  filtered_df = year_matches[year_matches['Main_Event_norm'] == event]
       # event_impact_with_error_bars(filtered_df, f"Wikimpacts vs EM-DAT (Year-level matches) per Event {args.impact_category} - {event.capitalize()}",args.impact_category,args.filepath)
    
