current_date=$(date +%Y-%m-%d_%H-%M-%S)
filename="${1:-scan_output${current_date}.tiff}"

scanimage -d genesys --resolution=4800 --mode=Color --depth=8 --format=tiff -o scanRessources/${filename}.tiff

echo true
