FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY ./app.py /app/app.py

RUN pip install aws-xray-sdk boto3

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
