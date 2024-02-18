current_date=$(date +%Y-%m-%d_%H-%M-%S)
scanimage -d genesys:libusb:001:003 --format=tiff -o scanRessources/scan_output${current_date}.tiff
tiff2pdf -o scanRessources/scan_output${current_date}.pdf scanRessources/scan_output${current_date}.tiff 
ocrmypdf scanRessources/scan_output${current_date}.pdf scanRessources/scan_${current_date}.pdf

rm scan_output${current_date}.pdf

echo true
