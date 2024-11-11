
###############################################################################
# Description:
# This script is for pre-processing seismic event waveform data
# CAP from 2013 to 2015
###############################################################################
import os
import subprocess
from obspy import read, read_inventory, UTCDateTime
import multiprocessing as mp
from tqdm.auto import tqdm

def create_directories(*dirs):
    for dir in dirs:
        os.makedirs(dir, exist_ok=True)

def process_mseed(event_dir, mseed, origin_time, evla, evlo, evdp, hour, mini, msec, error_resp_station):
    st = read(f"data/{event_dir}/{mseed}")
    head = st[0]
    
    station_id = f"{head.stats.network}.{head.stats.station}"
    
    resp = f"response/{event_dir}/{station_id}.xml"
    try:
        inv = read_inventory(resp)
    except FileNotFoundError:
        return f"{event_dir}: {station_id}.{head.stats.channel}", None
    
    if station_id in error_resp_station:
        return None, None
    
    stla, stlo, stel = inv.networks[0].stations[0].latitude, inv.networks[0].stations[0].longitude, inv.networks[0].stations[0].elevation
    
    st.detrend(type="demean")
    st.detrend(type="linear")
    st.taper(max_percentage=0.05)
    
    try:
        st.remove_response(inventory=inv, output="VEL", pre_filt=[0.8, 1, 20, 22])
    except Exception:
        return None, f"{event_dir}: {station_id}.{head.stats.channel}"
    
    newsacname = f"{origin_time.year}.{origin_time.julday:03d}.{hour}.{mini}.{msec}.{station_id}..{head.stats.channel}.SAC"
    output_path = f"vel_data/{event_dir}/{newsacname}"
    st.write(output_path, format="SAC")
    
    update_sac_headers(output_path, evlo, evla, evdp, stlo, stla, stel, origin_time, hour, mini, msec)
    
    local_st = read(output_path)
    if 2 <= local_st[0].stats.sac.dist <= 100:
        local_st.write(f"local_vel_data/{event_dir}/{newsacname}", format="SAC")
        if newsacname.endswith(".BHZ.SAC"):
            local_st.write(f"local_vel_data_BHZ/{event_dir}/{newsacname}", format="SAC")
    
    return None, None

def update_sac_headers(sac_file, evlo, evla, evdp, stlo, stla, stel, origin_time, hour, mini, msec):
    s = f"""
    wild echo off
    r {sac_file}
    ch LCALDA True
    ch evlo {evlo} evla {evla} evdp {evdp}
    ch stlo {stlo} stla {stla} stel {stel}
    ch t1 0.0 t2 0.0 t3 0.0 t4 0.0
    ch o gmt {origin_time.year} {origin_time.julday} {hour} {mini} {msec.split('.')[0]} {msec.split('.')[1]}
    wh
    q
    """
    subprocess.run(["sac"], input=s.encode(), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def process_event(event_line):
    event = event_line.split()
    event_dir, ymd, hour, mini, msec, evla, evlo, evdp = event[:8]
    origin_time = UTCDateTime(f"{ymd} {hour}:{mini}:{msec}")
    
    create_directories(f"vel_data/{event_dir}", f"local_vel_data/{event_dir}", f"local_vel_data_BHZ/{event_dir}")
    
    os.system(f"ls data/{event_dir}/*.mseed > data/{event_dir}/mseedfiles.txt")
    
    with open(f"data/{event_dir}/mseedfiles.txt", "r") as mseedlf:
        mseedl = mseedlf.read().splitlines()
    
    error_resp_station = set()
    no_resp_station = []
    
    for mseed in mseedl:
        no_resp, error_resp = process_mseed(event_dir, os.path.basename(mseed), origin_time, evla, evlo, evdp, hour, mini, msec, error_resp_station)
        if no_resp:
            no_resp_station.append(no_resp)
        if error_resp:
            error_resp_station.add(error_resp)
    
    return no_resp_station, list(error_resp_station)

def main():
    create_directories("vel_data", "local_vel_data", "local_vel_data_BHZ")
    
    with open("catlog/Poyraz_2015_catlog.par", "r") as eplf:
        epls = eplf.read().splitlines()
    
    pool = mp.Pool(processes=mp.cpu_count())
    
    results = list(tqdm(
        pool.imap(process_event, epls),
        total=len(epls),
        desc="Processing events",
        unit="event",
        smoothing=0.1
    ))
    
    pool.close()
    pool.join()
    
    no_resp_station = []
    error_resp_station = set()
    for no_resp, error_resp in results:
        no_resp_station.extend(no_resp)
        error_resp_station.update(error_resp)

    with open("1_remove_resp_log.txt", "w") as log:
        log.write("--------------------------------------------------------------------------\n")
        log.write(f"{len(no_resp_station)} stations have no response file, listed as follows:\n")
        log.write("\n".join(no_resp_station) + "\n")
        log.write(f"{len(error_resp_station)} stations have wrong response file, listed as follows:\n")
        log.write("\n".join(error_resp_station) + "\n")

if __name__ == "__main__":
    main()
