FROM python:latest

RUN echo "$PWD"
COPY requirements.txt /tmp
COPY .env .
RUN pip install -r tmp/requirements.txt
COPY ./ .

CMD python app.py
