# Usa l'immagine base di Python 3.9
FROM python:3.9-slim-buster

# Installa i pacchetti necessari per build-essential e PostgreSQL
RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get install -y libpq-dev

# Installa Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file dei requisiti del backend e del frontend nella directory di lavoro
COPY backend/requirements.txt /app/backend/
COPY frontend/package.json /app/frontend/
COPY frontend/yarn.lock /app/frontend/

# Installa le dipendenze del backend e del frontend
RUN pip install -r /app/backend/requirements.txt && \
    cd /app/frontend && yarn install

# Copia tutti i file del backend nella directory di lavoro
COPY backend/ /app/backend/

# Copia tutti i file del frontend nella directory di lavoro
COPY frontend/ /app/frontend/

# Imposta le variabili d'ambiente per SQLite e Redis
ENV DATABASE_URL=sqlite:///db.sqlite3
ENV REDIS_URL=redis://redis-14301.c135.eu-central-1-1.ec2.cloud.redislabs.com:14301
ENV REDIS_PASSWORD=9L27MC6wimmm9gVViL2Z8GarZ0LRx22D

# Avvia il server Django con Redis come cache
CMD ["sh", "-c", "redis-server --daemonize yes && python manage.py runserver 0.0.0.0:8000  & yarn start"]
