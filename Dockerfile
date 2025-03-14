FROM ubuntu:22.04

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ghostscript \
    libtiff-tools \
    ocrmypdf \
    python-is-python3 \
    python3 \
    python3-pip \
    sane \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py ./
COPY templates/ templates/
COPY static/ static/
COPY scanRessources/scanDocument.sh scanRessources/

CMD [ "python3", "./server.py" ]

