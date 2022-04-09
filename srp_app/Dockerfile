FROM python:latest

RUN echo "$PWD"
COPY requirements.txt /tmp
RUN pip install -r requirements.txt
COPY ./ .

CMD python app.py
