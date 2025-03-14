docker stop ScanBot 2>/dev/null || true
docker rm ScanBot 2>/dev/null || true

# Pull the latest image from DockerHub
docker pull oli1115/scanbot:latest

sudo docker run -d \
    --name ScanBot \
    -p 5400:5400 \
    --privileged \
    --restart=always \
    oli1115/scanbot:latest