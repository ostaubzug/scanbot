docker stop ScanBot
docker rm ScanBot

docker build --cache-from scan-bot -t scan-bot .

docker run -i --rm\
    --name ScanBot \
    --network=host \
    --privileged \
    scan-bot


    # falls nötig den USB Port durchgeben


    #https://blog.oddbit.com/post/2014-08-11-four-ways-to-connect-a-docker/
    #docker macvlan

    #https://github.com/sbs20/scanservjs/issues/202
    #https://publications.lexmark.com/publications/pdfs/network_scan_drivers/ger/d0e1116.html