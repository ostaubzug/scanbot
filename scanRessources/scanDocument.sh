#!/bin/bash

current_date=$(date +%Y-%m-%d_%H-%M-%S)
filename="${1:-scan_output${current_date}.tiff}"

# Get the selected scanner from the configuration
if [ -f "scanRessources/scanner_config" ]; then
    selected_scanner=$(cat scanRessources/scanner_config)
else
    selected_scanner="genesys"
fi

scanimage -d "$selected_scanner" --resolution=600 --mode=Color --depth=8 --format=tiff -o scanRessources/${filename}.tiff
tiff2pdf -o scanRessources/${filename}.pdf scanRessources/${filename}.tiff

rm scanRessources/${filename}.tiff

echo true
