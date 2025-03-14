docker stop ScanBot 2>/dev/null || true
docker rm ScanBot 2>/dev/null || true

# Build the image locally
docker build -t scanbot:local .

sudo docker run -d \
    --name ScanBot \
    -p 5400:5400 \
    --privileged \
    --restart=always \
    scanbot:local