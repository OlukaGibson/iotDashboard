FROM python:3.11.4-slim-buster
WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++ \
    && apt-get clean
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
EXPOSE 5000
ENV FLASK_APP=deviceManagement
ENV FLASK_ENV=development
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]