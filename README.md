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
### Local Setup
1. some instructions

## Using Docker Compose
1. **Run Docker compose**
A pre-configured docker-compose.yml is available for quick startup:
    ```bash
    docker-compose up --build
    ```
    This will build the FastAPI application and start a PostgreSQL database.
2. **Access the API**
   - The API will be available at `http://localhost:8000`.
   - The Swagger UI for API documentation can be accessed at `http://localhost:8000/docs`.
