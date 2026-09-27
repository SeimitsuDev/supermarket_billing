# ⚙️ Services Module

This module contains the core business logic and MongoDB integration layers. These services act as controllers bridging the `views` and the database.

## Key Services

- **`inventory_service.py`**: Manages connection to MongoDB. Handles CRUD operations for products and calculating dashboard analytics.
- **`billing_service.py`**: Manages the active shopping cart, calculates sub-totals, discounts, GST, and finalizes transactions by saving it into the database.
- **`auth_service.py`**: Handles user authentication and session management.

## Architecture
Services maintain a direct connection to MongoDB using `pymongo.MongoClient`. They abstract database queries into high-level python methods that the UI can call safely without writing raw queries.
