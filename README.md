# Scanbot

[![Build and Test](https://github.com/ostaubzug/scanbot/actions/workflows/build.yml/badge.svg)](https://github.com/ostaubzug/scanbot/actions)
[![Docker Image](https://img.shields.io/docker/v/oli1115/scanbot?logo=docker)](https://hub.docker.com/r/oli1115/scanbot)
[![Docker Pulls](https://img.shields.io/docker/pulls/oli1115/scanbot)](https://hub.docker.com/r/oli1115/scanbot)

A not so ugly UI Interface for your old Scanner

## Quick Start

Pull and run the Docker image:

```bash
docker pull oli1115/scanbot:latest
docker run -d --name ScanBot -p 5400:5400 --privileged --restart=always oli1115/scanbot:latest
```
