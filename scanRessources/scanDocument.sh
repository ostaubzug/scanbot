current_date=$(date +%Y-%m-%d_%H-%M-%S)
scanimage --ip-address=192.168.1.31 --format=pdf -o scan_output${current_date}.pdf 
ocrmypdf scan_output${current_date}.pdf scan_${current_date}.pdf

rm scan_output${current_date}.pdf

echo true
