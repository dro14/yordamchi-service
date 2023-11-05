FROM python:3.10.12-slim

RUN apt-get update -y && apt-get install -y \
    firefox-esr \
    wget \
    gcc \
    tar \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

RUN wget https://github.com/mozilla/geckodriver/releases/latest/download/geckodriver-v0.33.0-linux64.tar.gz \
    && tar -zxf geckodriver-v0.33.0-linux64.tar.gz -C /usr/local/bin \
    && rm geckodriver-v0.33.0-linux64.tar.gz

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "project.py"]
