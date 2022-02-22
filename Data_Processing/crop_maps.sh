#!/bin/bash 
for YEAR in {1950..2015}
do
echo cropping $YEAR maps
convert ./$YEAR/*.png[1920x962+0+118] ./maps/$YEAR\_%05d_map.png
done