# Dockerfile
FROM python:3.13-slim AS prod
RUN apt-get update && apt-get install -y \
  gcc \
  && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --upgrade pip poetry

# Configuring poetry
RUN poetry config virtualenvs.create false
RUN poetry config cache-dir /tmp/poetry_cache

# Copying requirements of a project
COPY pyproject.toml poetry.lock /app/src/
WORKDIR /app/src

# Installing requirements
RUN --mount=type=cache,target=/tmp/poetry_cache poetry install --only main
# Removing gcc
RUN apt-get purge -y \
  gcc \
  && rm -rf /var/lib/apt/lists/*

# Copying actuall application
COPY . /app/src/
RUN --mount=type=cache,target=/tmp/poetry_cache poetry install --only main

CMD ["/usr/local/bin/python", "-m", "huuva_backend"]

FROM prod AS dev

RUN --mount=type=cache,target=/tmp/poetry_cache poetry install
