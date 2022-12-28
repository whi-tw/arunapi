FROM python:3.10-slim

RUN pip install poetry

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY arunapi /app/arunapi
COPY docker-entrypoint.sh /

EXPOSE 8000

CMD ["/docker-entrypoint.sh"]
