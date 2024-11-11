
###############################################################################
# Description:
# This is for dealing with the seismic event catalog for NAFZ
# Catlog study from http://dx.doi.org/10.1016/j.tecto.2015.06.022
###############################################################################
import pandas as pd  
import csv  
from datetime import datetime, timedelta  
import re  
import time  
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt

###############################################################################
# Read the data using appropriate separator (assuming space or tab)
data = pd.read_csv(
    "catlog/Poyraz_2015_catlog_original.txt", sep="\s+", header=None, skiprows=1
)

# Assuming the file format is as follows:
# [Date] [Time] [Latitude] [Longitude] [Depth] [ML]

# Name the columns for the DataFrame
data.columns = ["Date", "Time", "Latitude", "Longitude", "Depth", "Magnitude"]

# Merge date and time, then format to ISO 8601
data["Time"] = pd.to_datetime(data["Date"] + " " + data["Time"])

# Select and rename required columns
DANA_seismicity_updated = data[
    ["Time", "Latitude", "Longitude", "Depth", "Magnitude"]
].copy()
DANA_seismicity_updated["Magnitude_type"] = "ML"  # Add Magnitude type column and set to "ML"

# Define time range
start_time = pd.to_datetime("2012-05-01")
end_time = pd.to_datetime("2013-09-20")

# Define the polygon for geographical filtering
# polygon = Polygon([
#     (29.95, 40.25), (30.7, 40.25), (30.7, 41.0), (29.95, 41.0)
# ])

polygon = Polygon([
    (29.6, 40.0), (29.6, 41.2), (31.0, 41.2), (31.0, 40.0)
])

# Function to check if a point is inside the polygon
def is_inside_polygon(lat, lon):
    point = Point(lon, lat)
    return polygon.contains(point)

# Filter data based on geographical (polygon), magnitude, and time criteria
DANA_seismicity_updated = DANA_seismicity_updated[
    (DANA_seismicity_updated.apply(lambda row: is_inside_polygon(row['Latitude'], row['Longitude']), axis=1))
    & (DANA_seismicity_updated["Magnitude"] >= 1.0)
    & (DANA_seismicity_updated["Magnitude"] <= 3.5)
    & (DANA_seismicity_updated["Depth"] <= 15.0)
    & (DANA_seismicity_updated["Time"] >= start_time)
    & (DANA_seismicity_updated["Time"] <= end_time)
]

# Sort by time
DANA_seismicity_updated = DANA_seismicity_updated.sort_values(by="Time")

# Convert Time column to string format
DANA_seismicity_updated["Time"] = DANA_seismicity_updated["Time"].dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

class Event:  
    # Define an Event class to hold earthquake event catalog details  
    def __init__(self, time, name, ymd, year, nsd, h, m, s, lat, lon, dep, mb):  
        self.time = time  
        self.name = name  
        self.ymd = ymd  
        self.year = year  
        self.nsd = nsd  # Day of the year  
        self.h = h  
        self.m = m  
        self.s = s  
        self.lat = lat  
        self.lon = lon  
        self.dep = dep  
        self.mb = mb  

    def __repr__(self):  
        # Representation of the Event object for debugging  
        return repr(  
            (  
                self.time,  
                self.name,  
                self.ymd,  
                self.year,  
                self.nsd,  
                self.h,  
                self.m,  
                self.s,  
                self.lat,  
                self.lon,  
                self.dep,  
                self.mb,  
            )  
        )  

def convert_csv_to_custom_format(input_file, output_file):  
    # Convert the CSV file to a custom output format with correct time filtering  
    data = []  
    with open(input_file, "r", encoding="utf-8") as infile:  
        csvreader = csv.reader(infile)  
        next(csvreader)  # Skip headers in the input CSV  

        events = []  
        for row in csvreader:  
            time_str, lat, lon, depth, magnitude, mag_type = row  
            try:  
                time_obj = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")  
                events.append((time_obj, row))  
            except ValueError as e:  
                print(f"Time format error for row: {row}, error: {e}")  
                continue  

    # Sort events chronologically  
    events.sort(key=lambda x: x[0])  

    last_kept_time = None  
    for time_obj, row in events:  
        if last_kept_time is None or (time_obj - last_kept_time) >= timedelta(minutes=2):  
            time_str, lat, lon, depth, magnitude, mag_type = row  
            new_time_str = time_obj.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  
            # This my custom catlog format following the our group tradition  
            # Change and replace the placeholders if you want  
            output_row = [  
                "xxxxx",  # Placeholder for the first column  
                new_time_str,  # Formatted time  
                lat,  
                lon,  
                depth,  
                "xxxx",  # Placeholder  
                "yyyyy",  # Placeholder  
                mag_type,  
                magnitude,  
                " ",  # Placeholder  
            ]  
            data.append((time_obj, output_row))  
            last_kept_time = time_obj  

    # Sort the kept data in reverse chronological order  
    data.sort(key=lambda x: x[0], reverse=True)  

    with open(output_file, "w", newline="", encoding="utf-8") as outfile:  
        csvwriter = csv.writer(outfile)  
        for _, output_row in data:  
            csvwriter.writerow(output_row)  # Write formatted rows to the output file  

def parse_custom_format(input_file, output_file):  
    # Parse the custom formatted input file and save it to a new output file  
    # This my custom catlog format following the our group tradition  
    # Change and replace the placeholders if you want  
    with open(input_file, "r") as el:  
        evps = el.read().splitlines()  

    event_tuples = []  
    for evp in evps:  
        parameters = evp.split(",")  
        t = re.findall("\d+", parameters[1])  # Extract numerical values from the time string  
        ymd = t[0] + t[1] + t[2]  # Create a string YYYYMMDD  
        h = t[3]  # Hour  
        m = t[4]  # Minute  
        s = t[5] + "." + t[6]  # Second with fractions  
        edir = ymd + "." + h + "." + m  # Create directory-like naming  
        timeArray = time.strptime(ymd + "." + h + m, "%Y%m%d.%H%M")  # Convert to time struct  
        year = t[0]  # Year  
        nsd = timeArray.tm_yday  # Day of the year  
        evtime = int(time.mktime(timeArray))  # Convert time struct to timestamp  
        lat = parameters[2]  
        lon = parameters[3]  
        dep = parameters[4]  
        mb = parameters[8]  
        event_tuples.append(  
            Event(evtime, edir, ymd, year, nsd, h, m, s, lat, lon, dep, mb)  
        )  

    sort_event_tuples = sorted(  
        event_tuples, key=lambda event: int(event.time), reverse=True  
    )  # Sort by event time  

    with open(output_file, "w") as out:  
        for event in sort_event_tuples:  
            # Write each event to the output file in the specified format  
            # This my custom catlog format following the our group tradition  
            # Change and replace the placeholders if you want  
            out.write(  
                "%-11s %-9s %-3s %-3s %-8s %-10s %-10s %-4s  8.4 25.6   %3s  ML\n"  
                % (  
                    event.name,  
                    event.ymd,  
                    event.h,  
                    event.m,  
                    event.s,  
                    event.lat,  
                    event.lon,  
                    event.dep,  
                    event.mb,  
                )  
            )

def create_magnitude_histogram(data, output_file):  
    plt.figure(figsize=(10, 6))  
    
    # 使用更好看的颜色和透明度  
    plt.hist(data['Magnitude'], bins=20, edgecolor='black', color='skyblue', alpha=0.7)  
    
    # # 添加平均值线  
    # mean_magnitude = data['Magnitude'].mean()  
    # plt.axvline(mean_magnitude, color='red', linestyle='dashed', linewidth=2, label=f'Mean: {mean_magnitude:.2f}')  
    
    plt.title('Magnitude Distribution of Seismic Events', fontsize=16)  
    plt.xlabel('Magnitude', fontsize=12)  
    plt.ylabel('Count', fontsize=12)  
    plt.grid(True, linestyle='--', alpha=0.5)  
    
    # 添加图例  
    plt.legend()  
    
    # 调整布局  
    plt.tight_layout()  
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')  
    plt.close()  


# Output paths  
output_csv = "catlog/Poyraz_2015_catlog.csv"  
output_txt = "catlog/Poyraz_2015_catlog.txt"  
output_par = "catlog/Poyraz_2015_catlog.par"  

# Save the final data as a CSV file, using comma as separator
DANA_seismicity_updated.to_csv(output_csv, index=False, sep=",")
convert_csv_to_custom_format(output_csv, output_txt)  
parse_custom_format(output_txt, output_par)
print("Data processing completed.")


# 创建震级分布直方图  
histogram_output = "catlog/Magnitude_Distribution_Histogram.jpg"  
create_magnitude_histogram(DANA_seismicity_updated, histogram_output)  

print("Data processing completed.")  
print(f"Magnitude distribution histogram saved as {histogram_output}") 