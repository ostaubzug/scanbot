FROM ubuntu:22.04

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    python3 \
    python-is-python3 \
    python3-pip \ 
    ocrmypdf \
    ghostscript \
    libtiff-tools \
    sane
 
RUN pip install jsonify
RUN pip install flask

COPY server.py ./
COPY templates/  templates/
COPY static static/
COPY scanRessources/scanDocument.sh scanRessources/

CMD [ "python", "./server.py" ]

