# Deliberately insecure Dockerfile for security correlation POC
# DO NOT USE IN PRODUCTION

# Using older image with known CVEs
FROM python:3.8-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

# INSECURE: Container runs as root
USER root

EXPOSE 5000

CMD ["python", "app.py"]
