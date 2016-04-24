#!/bin/bash 
for YEAR in {1950..2015}
do
	echo ------------$YEAR-------------
	#Remove all rows of stations not containing "US" in their station ID field or "SNWD" in the precipitation type field
	echo isolating observations to snow depth at U.S. stations
	awk '/^US.*SNWD/' $YEAR.csv > temp_SNWD_$YEAR.csv
	
	#Add latitude and longitude fields from ghcnd station file to yearly snow depth csv files
	echo joining with station data
	join -t, <(sort temp_SNWD_$YEAR.csv) <(sort ghcnd-stations.csv) > temp_SNWD_joined_$YEAR.csv
	
	#Remove whitespace
	echo clearing whitespace
	sed -i 's/[ ]*,[ ]*/,/g' temp_SNWD_joined_$YEAR.csv
	
	#Remove rows flagged for quality or outside continental ("lower 48") United States boundary.
	# i.e. those which satisfy both 25.118333<Lat.<49.384472 and -124.733056<Long.<-66.947028
	# See Table 2 of  http://www1.ncdc.noaa.gov/pub/data/cdo/documentation/GHCND_documentation.pdf for more information on quality flags
	echo filtering out boundary outliers and quality flags
	awk -F, '{if ($6=="" && $9>25.118333 && $9<49.384472 && $10>-124.733056 && $10<-66.949778) print}' temp_SNWD_joined_$YEAR.csv > temp_SNWD_joined_L48_$YEAR.csv
	
	#Sort files on date then on station id
	echo sorting by date and then by station id
	sort -t, -k2,2 -k1,1 temp_SNWD_joined_L48_$YEAR.csv > temp_SNWD_joined_L48_sorted_$YEAR.csv
	#Split in to daily csv files
	echo splitting into daily files
	mkdir -p daily
	awk -F, 'NR>1 {print > ("daily/"$2".csv")}' temp_SNWD_joined_L48_sorted_$YEAR.csv
	
	#Remove temp files
	echo removing temporary files
	rm temp_SNWD_$YEAR.csv
	rm temp_SNWD_joined_$YEAR.csv
	rm temp_SNWD_joined_L48_$YEAR.csv
	rm temp_SNWD_joined_L48_sorted_$YEAR.csv
done
echo --------------------------------
for file in daily/*.csv
do
	#Add a header (column names) to all daily csv files. Note: "Ignore" fields are not presently used in this visualization.
	echo Adding column name header to $file
	sed -i '1iStationID,Date,Type,Value,Ignore1,Ignore2,Ignore3,Ignore4,Latitude,Longitude,Elevation,State,Station,Ignore5,Ignore6' $file
done

echo ------------Done!-------------