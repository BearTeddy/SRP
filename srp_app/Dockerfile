FROM python:latest

RUN ls -la
COPY ./ .
RUN ls -la ./srp_app
RUN pip install -r srp_app/requirements.txt

CMD python srp_app/app.py
