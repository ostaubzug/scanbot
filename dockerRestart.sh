docker stop ScanBot
docker rm ScanBot

docker build --cache-from scan-bot -t scan-bot .

docker run -i --rm\
    --name ScanBot \
    --network=host \
    --privileged \
    scan-bot


    # falls nötig den USB Port durchgeben