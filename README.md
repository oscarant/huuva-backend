# Huuva Backend Homework Assignment

This project implements a backend system for managing kitchen orders at Huuva. The system is built with Python 3.13.2,
FastAPI, SQLAlchemy, and Pydantic. It models orders, order items, and their respective status changes with history
tracking. The API supports creating orders, retrieving orders, and updating the status of both the entire order and
individual order items.

---

## How to Run the Code

## Docker Compose

You can start the project with docker using this command:

```bash
docker-compose up --build
```

If you want to develop in docker with autoreload add `-f deploy/docker-compose.dev.yml` to your docker command.
Like this:

```bash
docker-compose -f docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up --build
```

This command mounts current directory and enables autoreload.

But you have to rebuild image every time you modify `poetry.lock` or `pyproject.toml` with this command:

```bash
docker-compose build
```

You can find swagger documentation at `localhost:8000/api/docs`.


## Configuration

This application can be configured with environment variables.

You can create `.env` file in the root directory and place all
environment variables here.

All environment variables should start with "HUUVA_BACKEND_" prefix.

For this project, I didn't use any environment variables, as I set up everything by
default in configs for practical purposes. But in a real-world application,
you would want to use them for configuration.


## Running tests

### Docker
If you want to run it in docker, simply run:

```bash
docker-compose run --build --rm api pytest -vv .
docker-compose down
```

### Local + Docker
For running tests on your local machine.
1. You need to start a database (or have the docker-compose running).

```
docker run -p "5432:5432" -e "POSTGRES_PASSWORD=huuva_backend" -e "POSTGRES_USER=huuva_backend" -e "POSTGRES_DB=huuva_backend" postgres:17-bullseye
```


2. Run the pytest.
```bash
pytest -vv .
```

### API Endpoints

- Core Order Management

  - POST /orders — Create a new order

  - GET /orders/{order_id} — Retrieve an order by ID

  - PATCH /orders/{order_id} — Update overall order status

  - PATCH /orders/{order_id}/items/{plu} — Update individual item status

- Analytics

  - GET /analytics/order-status-durations — Get average time (in seconds) spent in each order status

  - GET /analytics/item-status-durations — Get average time (in seconds) spent in each item status

  - GET /analytics/hourly-throughput — Get hourly order throughput (last 24 hours by default)

  - GET /analytics/customer-order-counts — Get number of orders per customer (top 100)

  - GET /analytics/refresh-materialized-views — Manually refresh materialized views

## Design Decisions and Assumptions
There's a lot of design decisions and assumptions made in this project. So it is not possible
to cover all of them in detail. But I will try to cover the most important ones.

- **Domain simplifications**
    - We’re a **pickup‑only** kitchen; there is no *dine‑in* or “served” step, so the final order status is **READY→PICKED_UP**.
    - **Refunds are out of scope**. They would require a separate model and status flow.
    - Items can **only exist inside an order**; therefore, item creation and deletion are handled transactionally together with the parent order.

- **Identifiers & keys**
    - Generated primary keys are **UUID(v4) strings** (stored as `String` in Postgres).
      This guarantees uniqueness across shards and avoids insert hot‑spots.
    - `items` use a **composite primary key** `(order_id, plu)` because a PLU is only unique inside its order.

- **Status modelling**
  - We keep history in the *status_history* tables instead of mutating the live row; that gives us an immutable event log that is cheap to aggregate later.
  - Only the *transient* statuses are considered in time‑gap analytics:
    **ORDERED(1) → PREPARING(2) → READY(3)**.
    `PICKED_UP` and `CANCELLED` are terminal and do not participate in average‑duration metrics.

- **Order status and item status**
    - Whenever an order is updated, all items are updated to the same status.
      This is a simplification that avoids the complexity of item‑level status changes.
    - Even tho, this is just assumption, it is a good idea to keep the item status in sync with the order status.
      This way, we can avoid having items in a different state than the order itself.

- **Repository vs Service layer**
    - The history write happens inside the repository to keep the **order + items +  histories** insert strictly atomic (single transaction).
    - As soon as more business rules (pricing, refunds, stock checks, …) are added, the update logic can be lifted into a dedicated *service* layer without breaking the API.

- **Configuration**
    - Defaults are hard‑coded for an easy “clone → docker‑compose up” experience.
      In prod you’d define them in a `.env` file – all vars are prefixed with `HUUVA_BACKEND_`.

- **Testing approach**
    - Each test spins up an **in‑memory Postgres** in Docker, runs inside a SAVEPOINT and rolls back, so tests remain isolated and fast.
    - Async SQLAlchemy sessions are injected via `dependency_overrides` to keep the API code untouched.

- **Scheduler vs Orchestration**
    - I used a simple **APScheduler** to run the analytics job every hour.
    - This is a simple solution that works for this project. In a real-world application, you would want to use a more robust solution like Airflow or Celery.
    - I chose APScheduler over Airflow for simplicity and speed. It is easy to set up and doesn't require a lot of configuration.

- **Analytics**
    - I used a simple SQL query to calculate the average time spent in each status.
    - There's a simple API endpoint to get the analytics data.

- **Balance between make production quality and speed**
    - I tried to find a balance between production quality and speed.
    - I added some production-like features (Sentry, OpenAPI, Linters, CI, etc.) but didn't go too deep into it.
    - I think that the current state of the code it's in the middle between a production-ready code and a MVP.
    As it feels a bit wrong when you skip some things that you would do in a real production environment. Graphic description below:
      <img src="https://github.com/user-attachments/assets/6e877236-c3b6-4d71-b072-8de32c75c580" width="480" height="360">


## Time Spent
~16-18 hours, even tho, this still being an estimate.
* **Core Modeling and API**: 10h
* **Testing, CI, Pre-commit**: 3h
* **Analytics**: 2h
* **Documentation**: 1h



## What I'd add with more time
- End‑to‑end **status transition validation** (only legal hops allowed, e.g. PREPARING → CANCELLED is OK, READY → PREPARING is not).
- **Pagination & cursor API** for `/orders` list.
- **Frontend** to visualize the order and items.
- More **tests** for the Analytics specifically. And more love in general.
- Better **error handling** and logging.
