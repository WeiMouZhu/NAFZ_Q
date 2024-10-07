
import os
import shutil
import csv
from obspy import read

def get_sac_header_values(sac_file_path):
    try:
        st = read(sac_file_path)
        tr = st[0]
        depth_value = tr.stats.sac.evdp
        evla = tr.stats.sac.evla
        evlo = tr.stats.sac.evlo
        return depth_value, evla, evlo
    except Exception as e:
        print(f"Error processing file {sac_file_path}: {e}")
        return None, None, None

def process_sac_files(input_folder, output_folder, depth_range, lat_range, lon_range, csv_output):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    total_files = 0
    copied_files = 0
    saved_files_info = []

    for filename in os.listdir(input_folder):
        if filename.endswith('.SAC'):
            total_files += 1
            input_file_path = os.path.join(input_folder, filename)
            depth_value, evla, evlo = get_sac_header_values(input_file_path)

            if depth_value is not None and evla is not None and evlo is not None:
                if (depth_range[0] <= depth_value <= depth_range[1] and
                    lat_range[0] <= evla <= lat_range[1] and
                    lon_range[0] <= evlo <= lon_range[1]):
                    
                    output_file_path = os.path.join(output_folder, filename)
                    shutil.copy2(input_file_path, output_file_path)
                    copied_files += 1
                    saved_files_info.append([filename, depth_value, evla, evlo])
                    print(f"Copied {filename} to {output_folder}")
                else:
                    print(f"Skipped {filename} (out of range)")
            else:
                print(f"Skipped {filename} (missing data)")

    print(f"\nProcessed {total_files} files, copied {copied_files} files.")

    # Write saved file information to CSV
    with open(csv_output, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Filename', 'Depth (km)', 'Latitude', 'Longitude'])
        csvwriter.writerows(saved_files_info)

    print(f"Saved file information has been written to {csv_output}")

if __name__ == "__main__":
    input_folder = "NAFZ_final_SAC"
    output_folder = "NAFZ_F_SAC"
    depth_range = (0, 15)  # Depth range: 0-15 km
    lat_range = (40.25, 41.0)  # Latitude range: 40.25-41.0 degrees
    lon_range = (29.95, 30.7)  # Longitude range: 29.95-30.7 degrees
    csv_output = "saved_sac_files_info.csv"
    
    process_sac_files(input_folder, output_folder, depth_range, lat_range, lon_range, csv_output)
