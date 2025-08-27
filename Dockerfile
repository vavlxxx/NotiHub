FROM python:3.11.9

WORKDIR /app

RUN pip install poetry
ENV PATH="/root/.local/bin:$PATH"
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-interaction --no-cache

COPY . .

CMD poetry run alembic upgrade head; poetry run python src/main.py
