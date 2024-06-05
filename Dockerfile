FROM python:3.10-slim

WORKDIR /app

COPY lambda_function.py requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["lambda_function.lambda_handler"]
