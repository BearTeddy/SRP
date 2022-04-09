FROM python:latest

COPY ./srp_app_ .
RUN ls -la ./srp_app_
RUN pip install -r srp_app_/requirements.txt

CMD python srp_app_/app.py