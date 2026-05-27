FROM python:3.11-slim

WORKDIR /app

# Abhängigkeiten zuerst (Layer-Caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App-Code
COPY . .

# Daten-Ordner anlegen
RUN mkdir -p data

EXPOSE 5000

CMD ["python", "app.py"]
