#!/bin/bash

current_date=$(date +%Y-%m-%d_%H-%M-%S)
filename="${1:-scan_output${current_date}.tiff}"

filename="${filename%.pdf}"

if [ -f "scanRessources/scanner_config" ]; then
    selected_scanner=$(cat scanRessources/scanner_config)
else
    selected_scanner="genesys"
fi

if [ -f "scanRessources/dpi_config" ]; then
    selected_dpi=$(cat scanRessources/dpi_config)
else
    selected_dpi="600"  # Default to 600 DPI if not configured
fi

scanimage -d "$selected_scanner" --resolution=$selected_dpi --mode=Color --depth=8 --format=tiff -o scanRessources/${filename}.tiff
tiff2pdf -o scanRessources/${filename}.pdf scanRessources/${filename}.tiff

rm scanRessources/${filename}.tiff

echo true
