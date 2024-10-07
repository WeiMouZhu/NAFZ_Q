
###############################################################################
# Description:
# This script processes PhaseNet picks, filters and sorts them,
# It includes steps for:
# 1. Processing initial picks data
# 2. Filtering for valid P and S wave pairs
# 3. Copying relevant SAC files and PNG images to new directories
# NAFZ from 2012 to 2013
###############################################################################

import pandas as pd
import os
import shutil
###############################################################################
# Read the CSV file
df = pd.read_csv('./NAFZ_SAC/results/picks.csv')

# Convert begin_time and phase_time to datetime objects
df['begin_time'] = pd.to_datetime(df['begin_time'])
df['phase_time'] = pd.to_datetime(df['phase_time'])

# Group by file_name and apply filtering conditions
def filter_group(group):
    # Check if at least one phase_score is greater than 0.5
    if not group[group['phase_score'] > 0.3].empty:
        result = []
        for phase in ['P', 'S']:
            phase_group = group[group['phase_type'] == phase]
            if not phase_group.empty:
                # Select the record with the highest phase_score, regardless of whether it's above 0.5
                result.append(phase_group.loc[phase_group['phase_score'].idxmax()])
        return pd.DataFrame(result)
    else:
        # If no records have phase_score greater than 0.5, return an empty DataFrame
        return pd.DataFrame()

# Apply the filtering function
filtered_df = df.groupby('file_name').apply(filter_group).reset_index(drop=True)

# Sort by begin_time, then by file_name and phase_time if begin_time is the same
filtered_df = filtered_df.sort_values(['begin_time', 'file_name', 'phase_time'])

# Convert datetime columns back to original string format, keeping three zeros at the end
filtered_df['begin_time'] = filtered_df['begin_time'].dt.strftime('%Y-%m-%dT%H:%M:%S.%f').str[:-3]
filtered_df['phase_time'] = filtered_df['phase_time'].dt.strftime('%Y-%m-%dT%H:%M:%S.%f').str[:-3]

# Select and order the required columns
columns_order = ['station_id', 'begin_time', 'phase_index', 'phase_time', 'phase_score', 'phase_type', 'file_name']
filtered_df = filtered_df[columns_order]

# Save the results to a new CSV file
filtered_df.to_csv('NAFZ_SAC/results/filtered_picks.csv', index=False)

print("Initial processing complete, results saved to NAFZ_SAC/results/filtered_picks.csv")
print(f"Number of records after initial processing: {len(filtered_df)}")

# Read the newly generated CSV file
df = pd.read_csv('NAFZ_SAC/results/filtered_picks.csv')

# For each file_name, check if both P and S phases exist, and P phase is before S phase
def check_ps(group):
    if set(group['phase_type']) != {'P', 'S'}:
        return False
    
    p_time = group[group['phase_type'] == 'P']['phase_time'].iloc[0]
    s_time = group[group['phase_type'] == 'S']['phase_time'].iloc[0]
    
    return pd.to_datetime(p_time) < pd.to_datetime(s_time)

# Apply filtering, keep only SAC records with both P and S phases, and P before S
final_df = df.groupby('file_name').filter(check_ps)

# Apply sorting logic again
final_df['begin_time'] = pd.to_datetime(final_df['begin_time'])
final_df['phase_time'] = pd.to_datetime(final_df['phase_time'])
final_df = final_df.sort_values(['begin_time', 'file_name', 'phase_time'])

# Convert datetime columns back to original string format
final_df['begin_time'] = final_df['begin_time'].dt.strftime('%Y-%m-%dT%H:%M:%S.%f').str[:-3]
final_df['phase_time'] = final_df['phase_time'].dt.strftime('%Y-%m-%dT%H:%M:%S.%f').str[:-3]

# Save the final results to a new CSV file
final_df.to_csv('NAFZ_SAC/results/final_filtered_picks.csv', index=False)

print("Final processing complete, results saved to NAFZ_SAC/results/final_filtered_picks.csv")
print(f"Number of records after final processing: {len(final_df)}")

# Create new directories
new_sac_dir = 'NAFZ_filter_SAC'
new_figures_dir = os.path.join(new_sac_dir, 'figures')
os.makedirs(new_sac_dir, exist_ok=True)
os.makedirs(new_figures_dir, exist_ok=True)

# Copy SAC files and PNG images
copied_files = set()
for _, row in final_df.iterrows():
    file_name = row['file_name']
    
    # Avoid duplicate copying
    if file_name in copied_files:
        continue
    
    # Copy SAC file
    sac_src = os.path.join('NAFZ_SAC', file_name)
    sac_dst = os.path.join(new_sac_dir, file_name)
    if os.path.exists(sac_src):
        shutil.copy2(sac_src, sac_dst)
        print(f"Copied SAC file: {file_name}")
    else:
        print(f"SAC file not found: {file_name}")
    
    # Copy PNG image to figures subdirectory
    png_src = os.path.join('NAFZ_SAC', 'results', 'figures', file_name + '.png')
    png_dst = os.path.join(new_figures_dir, file_name + '.png')
    if os.path.exists(png_src):
        shutil.copy2(png_src, png_dst)
        print(f"Copied PNG file: {file_name}.png")
    else:
        print(f"PNG file not found: {file_name}.png")
    
    copied_files.add(file_name)

print(f"Copying complete. Copied {len(copied_files)} SAC files to {new_sac_dir} directory,")
print(f"and corresponding PNG images to {new_figures_dir} directory.")
