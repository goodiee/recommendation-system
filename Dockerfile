FROM pgvector/pgvector:pg17

RUN apt-get update && \
    apt-get install -y postgresql-17-postgis-3

COPY db/main.sql /docker-entrypoint-initdb.d/02_set_db.sql
