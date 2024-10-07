
###############################################################################
# Description:
# This script sets the theoretical P and S wave arrival times for SAC files.
# It prepares SAC files for further AI-based picking methods like PhaseNet.
# CAP (Cut and Paste) from 2013 to 2015
###############################################################################
import os
import glob
import subprocess
import shutil
import csv

###############################################################################

def process_events(base_dir):
    # Get the absolute path of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Read the event parameter file
    with open(os.path.join(script_dir, "log", "Poyraz_2015_catlog_updated.par"), "r") as elf:
        event_lines = elf.read().splitlines()

    # Create CAP_SAC directory and its subdirectory for results
    cap_sac_dir = os.path.join(script_dir, "NAFZ_SAC")
    cap_sac_results_dir = os.path.join(cap_sac_dir, "results")
    os.makedirs(cap_sac_dir, exist_ok=True)
    os.makedirs(cap_sac_results_dir, exist_ok=True)

    # Prepare CSV file
    csv_file = os.path.join(cap_sac_results_dir, "sac.csv")
    copied_files = []

    for line in event_lines:
        event = line.split()
        event_dir = event[0]

        event_path = os.path.join(base_dir, event_dir)
        if not os.path.isdir(event_path):
            print(f"The records of {event_dir} have been deleted or do not exist, skipping.")
            continue

        # Get all SAC files
        sac_files = glob.glob(os.path.join(event_path, "*.SAC"))
        if not sac_files:
            print(f"No SAC files found in {event_dir}, skipping.")
            continue

        # Call taup setsac command to set theoretical arrival times
        try:
            subprocess.run(
                ["taup", "setsac", "-mod", "prem", "-evdpkm", "-ph", "P-1,S-2"] + sac_files,
                check=True
            )
            print(f"Processed SAC files in {event_dir}.")
        except subprocess.CalledProcessError as e:
            print(f"Error processing SAC files in {event_dir}: {e}")

        # Copy SAC files to CAP_SAC directory
        for sac_file in sac_files:
            dest_path = os.path.join(cap_sac_dir, os.path.basename(sac_file))
            shutil.copy2(sac_file, dest_path)
            copied_files.append(os.path.basename(sac_file))
            print(f"Copied: {os.path.basename(sac_file)}")

    # Write the list of copied files to sac.csv
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["fname"])  # Header
        for file in copied_files:
            writer.writerow([file])

    print(f"Copied {len(copied_files)} SAC files to {cap_sac_dir}")
    print(f"Created {csv_file} with the list of copied files")

if __name__ == "__main__":
    # Use absolute path
    base_directory = os.path.abspath("local_vel_data_BHZ")  # Base path for event directories
    process_events(base_directory)




# python phasenet/predict.py --model=model/190703-214543 --data_list=NAFZ_SAC/results/sac.csv --data_dir=NAFZ_SAC --format=sac --batch_size=1 --plot_figure --result_dir=NAFZ_SAC/results 