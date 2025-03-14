FROM ubuntu:22.04 as builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM ubuntu:22.04

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ghostscript \
    libtiff-tools \
    ocrmypdf \
    python-is-python3 \
    python3 \
    sane \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.*/site-packages/ /usr/local/lib/python3/dist-packages/

COPY server.py ./
COPY templates/ templates/
COPY static/ static/
COPY scanRessources/scanDocument.sh scanRessources/

CMD [ "python3", "./server.py" ]

