FROM python:3.11.1-alpine

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app
COPY . /app/
RUN pip install -r requirements.txt
CMD ["python3", "main.py"]
