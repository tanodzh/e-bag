
# E-Bag E-commerce Service

## 📖 Overview
This project is a RESTful API service designed to handle core E-commerce operations. It fulfills the specific technical requirements defined for the team assignment, providing robust data management for products and categories.

## 📋 Project Requirements

### 1. Models
The system defines two primary data models with the following attributes:

*   **Product Model**
    *   `title` (String)
    *   `description` (String)
    *   `image` (String/URL)
    *   `sku` (Unique Product Identifier)
    *   `price` (Decimal)
    *   `category` (Foreign Key linking to Category)

*   **Category Model**
    *   `name` (String)
    *   `parent` (Foreign Key linking to a parent Category, enabling hierarchical structure)

### 2. Operations
The API provides full lifecycle management and advanced querying capabilities:

*   **CRUD Operations:** Complete Create, Read, Update, and Delete endpoints for both Products and Categories.
*   **Search API:** A flexible endpoint (`GET /api/v1/search/`) designed to filter results dynamically.
    *   **Filters Available:**
        *   By Product Name (`name`) — partial match on title
        *   By SKU (`sku`) — partial match on SKU (`name` and `sku` are mutually exclusive)
        *   By Price Range (`min_price` / `max_price`)
        *   By Category (`category_id`)
    *   *Additional:* The implementation includes pagination (`limit` / `offset`) for handling large result sets.

## 🛠 Technology Stack

*   **Backend Framework:** FastAPI
*   **Database:** MariaDB (Dockerized)
*   **ORM & Async Support:** SQLAlchemy (Async)
*   **Migration Tool:** Alembic
*   **Data Validation:** Pydantic Settings
*   **Testing Framework:** Pytest
*   **Environment:** Python 3.14 (Virtual Environment)

## 🚀 Setup and Installation

1.  **Prerequisites**
    *   Python 3.14+
    *   Docker & Docker Compose
    *   Git

2.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd e-bag
    ```

3.  **Virtual Environment Setup**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

4.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Database Configuration**
    Ensure your `.env` file is configured with the necessary database credentials (DB_USERNAME, DB_PASSWORD, etc.).

6.  **Database Initialization**
    *   **Start the Database:**
        ```bash
        docker-compose up -d
        ```
    *   **Run Migrations:**
        ```bash
        alembic upgrade head
        ```

## 📝 Usage

### Running the Application
To start the server in development mode with auto-reload:
```bash
.venv/bin/uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Running Tests
```bash
.venv/bin/pytest
```

### Seeding the Database
To populate the database with test data (300 categories, 50 000 products by default):
```bash
.venv/bin/python scripts/seed.py

# Custom amounts
.venv/bin/python scripts/seed.py --categories 500 --products 100000 --batch 1000
```
Seed data is prefixed (`[SEED]` / `SEED-`) and can be safely re-run — existing seed data is cleared first.
