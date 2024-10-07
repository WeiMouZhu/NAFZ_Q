Structure of the earthquake catalog used in "Microseismic Constraints on the State of the North Anatolian Fault Thirteen Years after the 1999 M7.4 Izmit Earthquake" by Beauce et al., 2022

The catalog file is a csv file with 14 columns and one row per event. For python users, it can easily be read with pandas as:

catalog = pandas.read_csv('catalog_Beauce_2022.csv', sep='\t', index_col=0)

Definition of the columns:

- origin_times: strings with the date and time of the events
- tids: integer ids of the templates that detected the earthquakes, these can be used to make groups of similar earthquakes
- latitudes: decimal latitudes
- longitudes: decimal longitudes
- depths: depths in km
- max_hor_uncertainty: maximum span of the uncertainty ellipsoid in the horizontal plane, in km
- azimuth_max_hor_unc: angle from north of the direction of maximum horizontal uncertainty
- max_ver_uncertainty: maximum span of the uncertainty ellipsoid in the vertical directiopn, in km
- magnitudes: local magnitudes
- fractal_dimensions: measure of strength of temporal clustering in the sequence the earthquake belongs to
- mining_activity: boolean, is True if the event is associated to mining activity
- location_quality: 2 = good location, 1 = large uncertainties but still give a good approximation of the location, 0 = cannot be trusted
- rel_error_hor: horizontal uncertainty of the relative location, in km
- rel_error_ver: vertical uncertainty of the relative location, in km

 ----------------------------------------------------------------------------
Notes: - Entries are NaN when the values are not available.

Contact info: Any questions? Check https://ebeauce.github.io/ for an up-to-date email address.
