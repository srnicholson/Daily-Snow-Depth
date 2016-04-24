@echo off

SETLOCAL ENABLEEXTENSIONS
SETLOCAL ENABLEDELAYEDEXPANSION

for /l %%i IN (1950,1,2015) DO (
    wget ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/by_year/%%i.csv.gz -O C:\[enter]\[save]\[directory]\[path]\[here]\%%i.csv.gz
)