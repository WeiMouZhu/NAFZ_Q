###############################################################################
# Description:
# This script is for:
# 1. Deleting event directories with fewer than 5 SAC files
# 2. Extracting station lists from SAC files
# 3. Updating event catalogs
# For CAP (Cut and Paste) data from2013 to 2015
###############################################################################
import glob
import os
from obspy import read, UTCDateTime

###############################################################################
class Station:
    # Represents a seismic station with its attributes
    def __init__(self, name, lat, lon, dep):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.dep = dep

    def __repr__(self):
        return repr((self.name, self.lat, self.lon, self.dep))


def load_event_catalog(file_path):
    # Load the event catalog from a file
    with open(file_path, "r") as file:
        return file.read().splitlines()


def process_event_directory(event_dir, event_info, station_flag):
    # Process an event directory:
    # - Check if directory exists
    # - Count SAC files (excluding KO network)
    # - Delete directory if fewer than 5 SAC files
    # - Extract station info if needed
    try:
        os.chdir(f"local_vel_data/{event_dir}/")
    except FileNotFoundError:
        print(f"The records of {event_info[0]}-{event_dir} have been deleted, skipping")
        return False, 0

    # Get all SAC files and filter out KO network
    all_sac_files = glob.glob("*.SAC")
    sac_files = [f for f in all_sac_files if not f.split('.')[6] == 'KO']

    if len(sac_files) < 9:
        print(f"The records of {event_info[0]}-{event_dir} is less than 9 (excluding KO network), deleting")
        os.chdir("../")
        os.system(f"rm -r {event_dir}")
        os.chdir("../")
        return False, 0

    if station_flag:
        extract_station_info(sac_files)

    # Update sacfiles.txt with non-KO files
    if not os.path.exists("sacfiles.txt"):
        with open("sacfiles.txt", "w") as f:
            for sac_file in sac_files:
                if sac_file.endswith(".BH?.SAC"):
                    f.write(f"{sac_file}\n")

    return True, len(sac_files)


def extract_station_info(sac_files):
    # Extract station information from SAC files
    for file_name in sac_files:
        try:
            header = read(file_name)[0].stats
            # Skip KO network stations
            if header.network == "KO":
                continue
                
            net_sta_name = f"{header.network}.{header.station}"

            if net_sta_name not in station_names:
                station_names.add(net_sta_name)
                station_data.append(
                    Station(
                        net_sta_name,
                        header.sac.stla,
                        header.sac.stlo,
                        header.sac.stel,
                    )
                )
        except AttributeError:
            print(f"[ERROR3] Header info wrong: {file_name}")

def write_updated_event_par_files(event_lines, all_sac, left_event, deleted_events):
    # Write updated event parameter files
    with open("log/Poyraz_2015_catlog_updated.par", "w") as new_elf, open(
        "log/Poyraz_2015_catlog_updated-2.par", "w"
    ) as new_elf2:
        for line in event_lines:
            # Write original format to the first file
            new_elf.write(line + "\n")
            # Parse event details and write to the second file with specific formatting
            event = line.split()
            origin_time = UTCDateTime(
                f"{event[1]} {event[2]}:{event[3]}:{event[4]}"
            )
            
            new_elf2.write(
                f"{event[1]:<9} {origin_time.year:<5} {origin_time.julday:<4} "
                f"{event[2]:<3} {event[3]:<3} {event[4]:<8} "
                f"{event[5]:<10} {event[6]:<10} {event[7]:<4} 8.4 25.6 {event[10]:<3} MB\n"
            )

    print(f"Deleted {deleted_events} event(s) because SAC files were less than 5")
    print(f"Total event number: {left_event}; SAC file count: {all_sac}")


def main():
    # Main function to process events and update catalogs
    global station_names, station_data
    station_names = set()
    station_data = []

    # Load the event catalog
    events = load_event_catalog("catlog/Poyraz_2015_catlog.par")

    # Check if station info needs to be extracted
    station_flag = not os.path.exists("log/NAFZ_stats.txt")
    print(
        f"\033[1;31m The Program will: a. delete the event_dir for sac less than 5; "
        f"b. renew the events.par{' ; c. extract station info' if station_flag else ''} \033[0m"
    )

    m = 0  # Counter for deleted events
    all_sac = 0
    left_event = 0
    updated_event_lines = []

    # Process each event
    for line in events:
        event_info = line.split()
        event_dir = event_info[0]

        continue_processing, n_sac = process_event_directory(
            event_dir, event_info, station_flag
        )
        if not continue_processing:
            m += 1
            continue

        updated_event_lines.append(line)
        os.chdir("../../")
        all_sac += n_sac
        left_event += 1

    # Sort and print station data
    station_data_sorted = sorted(station_data, key=lambda x: x.name, reverse=True)
    print(f"Total station count: {len(station_data_sorted)}")

    # Write station data if needed
    if station_flag:
        with open("log/NAFZ_stats.txt", "w") as outfile:
            for station in station_data_sorted:
                outfile.write(
                    f"{station.name:<10} {station.lon:<8.4f} {station.lat:<8.4f} {station.dep:<3.1f}\n"
                )

    # Write updated event parameter files
    write_updated_event_par_files(updated_event_lines, all_sac, left_event, m)


if __name__ == "__main__":
    main()