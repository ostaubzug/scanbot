# Scanbot

[![Build and Test](https://github.com/ostaubzug/scanbot/actions/workflows/build.yml/badge.svg)](https://github.com/ostaubzug/scanbot/actions)
[![Docker Image](https://img.shields.io/docker/image-size/oli1115/scanbot/latest?logo=docker)](https://hub.docker.com/r/oli1115/scanbot)
[![Docker Pulls](https://img.shields.io/docker/pulls/oli1115/scanbot?logo=docker)](https://hub.docker.com/r/oli1115/scanbot)

## Quick Start

Pull and run the Docker image:

```bash
docker pull oli1115/scanbot:latest
docker run -d --name ScanBot --privileged --restart=always --network host -v /var/run/dbus:/var/run/dbus -v /dev/bus/usb:/dev/bus/usb oli1115/scanbot:latest
```

Once the container is running, access the web interface at:

```
http://localhost:5400
```

## System Compatibility

This project is primarily designed for Linux/Unix systems as it relies on SANE (Scanner Access Now Easy) for scanner communication.

### Windows Users

To run Scanbot on Windows, you will need:

- Windows Subsystem for Linux 2 (WSL2)
- Docker Desktop with WSL2 backend
- USB device passthrough configured in WSL2

The native Windows environment is not supported due to SANE's dependency on Unix-like systems.
