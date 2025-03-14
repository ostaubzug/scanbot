docker stop ScanBot 2>/dev/null || true
docker rm ScanBot 2>/dev/null || true

docker build -t scanbot:local .

sudo docker run -d \
    --name ScanBot \
    -p 5400:5400 \
    --privileged \
    --restart=always \
    --network host \
    -v /var/run/dbus:/var/run/dbus \
    -v /dev/bus/usb:/dev/bus/usb \
    scanbot:local