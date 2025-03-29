# E-Commerce API

This is a Django-based REST API for an e-commerce platform. It includes features such as user authentication, category and product management, cart system, order processing, coupon system, and background task execution using Celery.

## Features
- User authentication with JWT
- Category management (Add, Edit, Delete, Fetch)
- Product management (Add, Edit, Delete, Fetch)
- Cart and order system
- Coupon system (Add, Apply)
- Redis caching for performance improvement
- Rate limiting to prevent API abuse
- Celery for background task processing

## Installation
1. Clone the repository:
   ```sh
   git clone <repository_url>
   cd e_commerce_api
   ```

2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Install and start Redis (for caching and Celery):
   - Download Redis for Windows: https://github.com/tporadowski/redis/releases
   - Start Redis server:
     ```sh
     redis-server
     ```

5. Run database migrations:
   ```sh
   python manage.py migrate
   ```

6. Start the Django development server:
   ```sh
   python manage.py runserver
   ```

## Running Celery
Start a Celery worker to process background tasks:
```sh
celery -A e_commerce_api worker --loglevel=info
```

## API Endpoints
The API includes endpoints for:
- Authentication
- Categories
- Products
- Cart & Orders
- Coupons

Use Postman or any API testing tool to interact with the API.

## License
This project is licensed under the MIT License.

