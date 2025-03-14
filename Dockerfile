FROM python:3.10-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.10-slim

WORKDIR /usr/src/app

COPY --from=builder /wheels /wheels

RUN apt-get update && apt-get install -y --no-install-recommends \
    ghostscript \
    libtiff-tools \
    ocrmypdf \
    sane \
    sane-utils \
    && pip install --no-cache-dir /wheels/* \
    && rm -rf /var/lib/apt/lists/* /wheels

COPY server.py ./
COPY templates/ templates/
COPY static/ static/
COPY scanRessources/scanDocument.sh scanRessources/

# Set execute permissions on the script
RUN chmod +x scanRessources/scanDocument.sh


EXPOSE 5400

CMD ["python3", "./server.py"]

