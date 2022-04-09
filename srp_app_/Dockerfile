FROM python:latest

RUN dir
RUN ls
COPY requirements.txt .
COPY .env .
RUN pip install -r requirements.txt
COPY ./ .

CMD python app.py
