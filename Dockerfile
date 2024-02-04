FROM python:3

WORKDIR /usr/src/app

RUN pip install jsonify
RUN pip install flask

EXPOSE 5400

COPY server.py index.html ./
COPY css/style.css ./css/


CMD [ "python", "./server.py" ]

