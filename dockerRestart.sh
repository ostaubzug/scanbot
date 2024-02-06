docker stop ScanBot
docker rm ScanBot

docker build --cache-from scan-bot -t scan-bot .

docker run -i --rm\
    --name ScanBot \
    -p 5400:5400 \
    scan-bot