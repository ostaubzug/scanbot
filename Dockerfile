FROM ubuntu:22.04

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    ghostscript \
    libtiff-tools \
    ocrmypdf \
    python-is-python3 \
    python3 \
    python3-pip \
    sane \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install jsonify flask

COPY server.py ./
COPY templates/  templates/
COPY static static/
COPY scanRessources/scanDocument.sh scanRessources/

CMD [ "python", "./server.py" ]

