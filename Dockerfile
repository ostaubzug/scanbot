FROM ubuntu:latest

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    python3 \
    python-is-python3 \
    python3-pip \
    netpbm \
    ghostscript \
    poppler-utils \
    imagemagick \
    unpaper \
    util-linux \
    tesseract-ocr \
    parallel \
    units \
    bc

RUN pip install jsonify
RUN pip install flask

EXPOSE 5400

COPY server.py ./
COPY templates/index.html  templates/
COPY static static/

CMD [ "python", "./server.py" ]

