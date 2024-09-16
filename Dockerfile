FROM python:3.12-slim
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN pip install poetry

RUN poetry config installer.max-workers 10
RUN poetry install --without dev,ingestion --no-interaction --no-ansi

COPY src/core ./src/core
COPY src/dash ./src/dash

ENV PYTHONPATH=/app

EXPOSE 8051

CMD poetry run python src/dash/main.py

