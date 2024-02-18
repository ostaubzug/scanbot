docker stop ScanBot
docker rm ScanBot

docker build --cache-from scan-bot -t scan-bot .

docker run -d --rm\
    --name ScanBot \
    --network=host \
    --privileged \
    scan-bot