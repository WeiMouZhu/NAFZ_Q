###############################################################################
# This is for plotting and visual inspection of the earthquake catlog of NAFZ

###############################################################################
import pygmt
import pandas as pd

###############################################################################
pygmt.config(
    MAP_FRAME_TYPE="plain",
    MAP_GRID_PEN_PRIMARY="0.3p,dimgrey",
    MAP_ANNOT_OBLIQUE="30",
    MAP_ANNOT_OFFSET_PRIMARY="5p",
    MAP_ANNOT_OFFSET_SECONDARY="5p",
    FONT_ANNOT_PRIMARY="10p,5",
    FONT_LABEL="10p,28,black",
    MAP_FRAME_WIDTH="2p",
    MAP_FRAME_PEN="0.5p",
    MAP_TICK_LENGTH_PRIMARY="5p",
    MAP_LABEL_OFFSET="5.5p",
    FORMAT_GEO_MAP="ddd.x" 
)

# MINLAT = 40.25
# MAXLAT = 41.0
# MINLON = 29.95
# MAXLON = 30.7

MINLAT = 40.00
MAXLAT = 41.20
MINLON = 29.60
MAXLON = 31.00


# MINLAT = 40.00
# MAXLAT = 41.20
# MINLON = 29.50
# MAXLON = 31.00

region_Ana = [MINLON, MAXLON, MINLAT, MAXLAT]
##########################################################################
# visualizing the events
meta_Ana_events = pd.read_csv(
    # "events/NAFZ_20120515_20150910_IRIS.csv",
    "catlog/Poyraz_2015_catlog.csv",
    delimiter=",",
    usecols=[1, 2, 3, 4],
)
#
Ana_event_new = pd.DataFrame(
    {
        "latitude": meta_Ana_events.iloc[:, 0],
        "longitude": meta_Ana_events.iloc[:, 1],
        "depth": meta_Ana_events.iloc[:, 2],
        "mag": meta_Ana_events.iloc[:, 3],
    }
)
##############################################################################
# begin plot
fig = pygmt.Figure()

fig.basemap(region=region_Ana, projection="M15c", frame=["a0.1f0.05", f"WsNe"])

fig.coast(
    land="gray55",
    water="gray70",
)

fig.grdimage(
    grid="@earth_relief_03s",
    shading=True,
    region=region_Ana,
    projection="M15c",
    # cmap="snow",
)

fig.plot(
    data="fig/gem_active_faults.txt",
    style="qn1:+Lh+f6p",
    pen="0.5p,black",
)

pygmt.makecpt(
    cmap="batlow",
    series=[0, 20],
    # reverse=True,
)

fig.plot(
    x=Ana_event_new.longitude,
    y=Ana_event_new.latitude,
    size=0.075 * (2**Ana_event_new.mag),
    fill=Ana_event_new.depth,
    cmap=True,
    style="cc",
    pen="0.1p,black",
)

# fig.plot(
#     data="catlog/Poyraz_2015_catlog.par",
#     incols=[6, 5],
#     style="x0.2c",
#     pen="0.65p,red",
# )

fig.plot(
    data="fig/NAFZ_stats.txt",
    incols=[1, 2],
    style="i0.55c",
    fill="black",
    pen="1.5p,black",
)
# fig.plot(
#     x = [30.6133, 40.6775],
#     y = [30.0923, 40.2844],
#     pen="2.5p,black",
# )


# fig.plot(
#     data="fig/KO_CAP.csv",
#     incols=[1, 2],
#     style="i0.45c",
#     fill="blue",
#     pen="1.5p,black",
# )


# save figure
fig.savefig("fig/NAFZ_py.pdf", dpi=600, crop=True, show=True)
fig.savefig("fig/NAFZ_py.png", dpi=300, crop=True)
