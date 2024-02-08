FROM ubuntu:latest

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    python3 \
    python-is-python3 \
    python3-pip \ 
    ocrmypdf \
    sane
 
RUN pip install jsonify
RUN pip install flask

EXPOSE 5400

COPY server.py ./
COPY templates/index.html  templates/
COPY static static/
COPY scanRessources/scanDocument.sh scanRessources/

CMD [ "python", "./server.py" ]

