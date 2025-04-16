# Huuva Backend Homework Assignment

This project implements a backend system for managing kitchen orders at Huuva. The system is built with Python 3.13.2,
FastAPI, SQLAlchemy, and Pydantic. It models orders, order items, and their respective status changes with history
tracking. The API supports creating orders, retrieving orders, and updating the status of both the entire order and
individual order items.

---

## Table of Contents

* [Overview](#overview)
* [How to Run the Code](#how-to-run-the-code)
  * [Local Setup](#local-setup)
  * [Using Docker Compose](#using-docker-compose)
* [Design Decisions and Assumptions](#design-decisions-and-assumptions)
* [Time Spent](#time-spent)
* [Future Enhancements](#future-enhancements)

---

## Overview

The system consists of the following main components:
- **Order Model:**
Represents an order with attributes such as the customer account (UUID), brand ID, channel order ID, customer details,
pickup time, overall order status, delivery address, nested order items, and status history.

- **Order Item Model:**
  Represents individual order items with:
    - **PLU (Product Look-Up code):** Used to uniquely identify an item within an order.
    - **Quantity and Status:** Each item has a quantity (validated to be 1 or greater) and its own status using enumerated types (ORDERED, PREPARING, READY).

- **Status History:**
  Both orders and items maintain history entries recording the timestamp of every status update. This is used for computing analytics such as:
    - Average time spent in each status.
    - Order throughput per hour.
    - Number of orders per customer lifetime.

- **Repository and Mapping Layers:**
  The repository pattern abstracts all database operations while a dedicated mapping module converts between Pydantic schemas and SQLAlchemy models (especially to bridge differences in enum definitions).

- **API Endpoints:**
  Built with FastAPI, endpoints include:
    - **POST `/orders`:** Create a new order (with nested items and optional status history).
    - **GET `/orders/{order_id}`:** Retrieve an order by its UUID.
    - **PATCH `/orders/{order_id}/status`:** Update the overall order status.
    - **PATCH `/orders/{order_id}/items/{plu}/status`:** Update the status of an individual order item (identified by its PLU).
      *Note:* Although a more generic update endpoint could be used, this design uses a dedicated status update endpoint for clarity, and it is documented in the README.

---

## How to Run the Code
## Poetry

This project uses poetry. It's a modern dependency management
tool.

To run the project use this set of commands:

```bash
poetry install
poetry run python -m huuva_backend
```

This will start the server on the configured host.

You can find swagger documentation at `/api/docs`.

You can read more about poetry here: https://python-poetry.org/

## Docker

You can start the project with docker using this command:

```bash
docker-compose up --build
```

If you want to develop in docker with autoreload and exposed ports add `-f deploy/docker-compose.dev.yml` to your docker command.
Like this:

```bash
docker-compose -f docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up --build
```

This command exposes the web application on port 8000, mounts current directory and enables autoreload.

But you have to rebuild image every time you modify `poetry.lock` or `pyproject.toml` with this command:

```bash
docker-compose build
```

## Configuration

This application can be configured with environment variables.

You can create `.env` file in the root directory and place all
environment variables here.

All environment variables should start with "HUUVA_BACKEND_" prefix.

For example if you see in your "huuva_backend/settings.py" a variable named like
`random_parameter`, you should provide the "HUUVA_BACKEND_RANDOM_PARAMETER"
variable to configure the value. This behaviour can be changed by overriding `env_prefix` property
in `huuva_backend.settings.Settings.Config`.

An example of .env file:
```bash
HUUVA_BACKEND_RELOAD="True"
HUUVA_BACKEND_PORT="8000"
HUUVA_BACKEND_ENVIRONMENT="dev"
```

## Pre-commit

To install pre-commit simply run inside the shell:
```bash
pre-commit install
```

pre-commit is very useful to check your code before publishing it.
It's configured using .pre-commit-config.yaml file.

By default it runs:
* black (formats your code);
* mypy (validates types);
* ruff (spots possible bugs);


You can read more about pre-commit here: https://pre-commit.com/

## Migrations

If you want to migrate your database, you should run following commands:
```bash
# To run all migrations until the migration with revision_id.
alembic upgrade "<revision_id>"

# To perform all pending migrations.
alembic upgrade "head"
```

### Reverting migrations

If you want to revert migrations, you should run:
```bash
# revert all migrations up to: revision_id.
alembic downgrade <revision_id>

# Revert everything.
 alembic downgrade base
```

### Migration generation

To generate migrations you should run:
```bash
# For automatic change detection.
alembic revision --autogenerate

# For empty file generation.
alembic revision
```


## Running tests

If you want to run it in docker, simply run:

```bash
docker-compose run --build --rm api pytest -vv .
docker-compose down
```

For running tests on your local machine.
1. you need to start a database.

I prefer doing it with docker:
```
docker run -p "5432:5432" -e "POSTGRES_PASSWORD=huuva_backend" -e "POSTGRES_USER=huuva_backend" -e "POSTGRES_DB=huuva_backend" postgres:16.3-bullseye
```


2. Run the pytest.
```bash
pytest -vv .
```
