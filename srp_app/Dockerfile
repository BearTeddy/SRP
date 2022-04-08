FROM python:latest

COPY ./directory/requirements.txt /dir/
COPY ./directory/.env /dir/
RUN pip install -r requirements.txt
COPY ./directory /dir/

CMD python app.py
