docker stop ScanBot 2>/dev/null || true
docker rm ScanBot 2>/dev/null || true

DOCKER_BUILDKIT=1 docker build \
    --cache-from scan-bot \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    -t scan-bot .

sudo docker run -d \
    --name ScanBot \
    -p 5400:5400 \
    --privileged \
    --restart=always \
    scan-bot