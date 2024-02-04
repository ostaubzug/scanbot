FROM python:3

WORKDIR /usr/src/app

RUN pip install jsonify
RUN pip install flask

EXPOSE 5400

COPY server.py ./
COPY templates/index.html  templates/
COPY static static/

CMD [ "python", "./server.py" ]

