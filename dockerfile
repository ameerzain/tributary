FROM python:3.11

COPY ./requirements.txt .

COPY ./entrypoint.py .

RUN pip install -r requirements.txt

CMD exec gunicorn entrypoint:app