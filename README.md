# Daily-Snow-Depth
This repo contains scripts to generate visualizations of daily U.S. snow depth.

The following guide explains how to download the underlying dataset, format it, import it into QGIS, and ultimately combine the resulting map frames into a timelapse video. 

1. Downloading the raw data **This step requires wget. On Windows, get it here: http://gnuwin32.sourceforge.net/packages/wget.htm
	1a. The data we want to use is located in the National Climate Data Center's FTP service: ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/by_year/ 
	1b. To download the `.gz` files (CAUTION: over 13 GB total!)
		1bi.  Edit `download_by_year.bat` to specify the year range to download
		1bii. Edit `download_by_year.bat` to specify the save directory
	1c. Extract the csv files within these `.gz` files using a utility like 7-zip

2. Formatting the raw data **This step requires a Unix shell. If you are on Windows, consider Cygwin, available here: https://www.cygwin.com/
	2a. These `.csv` files contain all weather data for every station in the Global Historical Climate Network (GHCN). We only need the snow depth data from U.S. stations.
	2b. From the terminal (on Windows, open Cygwin), navigate to the location of the csv files.
	2c. Run format_raw_data.sh from the Cygwin terminal. This will create a new directory containing daily csv files for snow depth data at continental U.S. stations. The files are named in the following way: `L48US_YYYYMMDD.csv`
3. Create spatially-interpolated snow depth maps **This step requires QGIS, available here: http://www.qgis.org/
	3a. Open QGIS
	3b. Click the Python logo to open the Python Console within QGIS.
	3b. Click "Show Editor"
	3c. Click "Open file", navigate to the location of `SNWD_full.py`, and open it.
	3d. In the ___ lines of the script, you will need to specify paths to the `.csv` files and required svg files used during map rendering
	3e. 
