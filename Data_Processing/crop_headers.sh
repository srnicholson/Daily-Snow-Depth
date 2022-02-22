#!/bin/bash 
for YEAR in {1950..2015}; do echo $YEAR; convert ./$YEAR/*.png[1920x118+0+0] ./headers/$YEAR\_%05d_header.png; done