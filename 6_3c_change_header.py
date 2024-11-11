

###############################################################################
# Description:
# This script processes SAC (Seismic Analysis Code) files based on filtered picks data.
# It performs the following main tasks:
# 1. Reads filtered seismic phase picks from a CSV file
# 2. Calculates time differences for P and S waves
# 3. Copies SAC files to a new directory
# 4. Updates SAC header variables (t1 for P wave, t2 for S wave) based on calculated times
# 5. Calculates and updates the actual distance (user2) considering both epicentral distance and event depth
# 6. Saves the updated SAC files
#
# This script is part of the seismic data processing pipeline for the NAFZ project.
###############################################################################

import pandas as pd
from obspy import read
import os
import shutil

# Read the filtered_picks.csv file
df = pd.read_csv('NAFZ_5Filter_3SAC/final_filtered_picks.csv')

# Convert begin_time and phase_time to datetime objects
df['begin_time'] = pd.to_datetime(df['begin_time'])
df['phase_time'] = pd.to_datetime(df['phase_time'])

# Calculate t_P and t_S (ensure they are numeric type)
df['time_diff'] = (df['phase_time'] - df['begin_time']).dt.total_seconds().astype(float)
df_p = df[df['phase_type'] == 'P'].set_index('file_name')
df_s = df[df['phase_type'] == 'S'].set_index('file_name')

# Create a new directory
new_sac_folder = './NAFZ_6Outlier_3SAC'
if not os.path.exists(new_sac_folder):
    os.makedirs(new_sac_folder)
    
# Create the results subdirectory  
results_folder = os.path.join(new_sac_folder, 'results')  
if not os.path.exists(results_folder):  
    os.makedirs(results_folder) 
    
# Iterate through the SAC folder
sac_folder = './NAFZ_5Filter_3SAC'
for root, dirs, files in os.walk(sac_folder):
    for file in files:
        if file.endswith('.SAC'):
            file_path = os.path.join(root, file)
            new_file_path = os.path.join(new_sac_folder, file)
            
            # Copy SAC file to the new directory
            shutil.copy2(file_path, new_file_path)
            
            # Read the newly copied SAC file
            st = read(new_file_path)
            tr = st[0]
            
            # Update t1 (P wave)
            if file in df_p.index:
                tr.stats.sac.t1 = 2*float(df_p.loc[file, 'time_diff'])
            
            # Update t2 (S wave)
            if file in df_s.index:
                tr.stats.sac.t2 = 2*float(df_s.loc[file, 'time_diff'])

            
            # Save the updated SAC file
            tr.write(new_file_path, format='SAC')

print("All SAC files have been copied and header variables updated. New files are saved in the NAFZ_outlier_SAC directory.")

