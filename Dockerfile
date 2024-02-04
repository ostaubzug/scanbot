FROM python:3

WORKDIR /usr/src/app
RUN mkdir templates

RUN pip install jsonify
RUN pip install flask

EXPOSE 5400

COPY server.py ./
COPY templates/index.html templates/css templates/


CMD [ "python", "./server.py" ]

