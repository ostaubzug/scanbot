docker stop ScanBot
docker rm ScanBot

docker build --cache-from scan-bot:1.0 -t scan-bot:1.0 .

docker run -i --rm\
    --name ScanBot \
    -p 5400:5400 \
    scan-bot:1.0 