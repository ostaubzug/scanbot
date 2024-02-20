current_date=$(date +%Y-%m-%d_%H-%M-%S)
filename="${1:-scan_output${current_date}.tiff}"

scanimage -d genesys --resolution=600 --mode=Color --depth=8 --format=tiff -o scanRessources/${filename}.tiff
tiff2pdf -o scanRessources/${filename}.pdf scanRessources/${filename}.tiff
#ocrmypdf scanRessources/scan_output${current_date}.pdf scanRessources/scan_${current_date}.pdf

#rm scanRessources/scan_output${current_date}.pdf
rm scanRessources/${filename}.tiff

echo true
