docker stop ScanBot
docker rm ScanBot

docker build --cache-from scan-bot -t scan-bot .

sudo docker run -d \
    --name ScanBot \
    --network=host \
    --privileged \
    scan-bot