# Restaurant Management System

A backend REST API for managing restaurant operations, including menu items, tables, reservations, orders, inventory, and order processing.

The project is built using **Django, Django REST Framework, PostgreSQL, and JWT authentication**.

## Features

* Menu management
* View menu items
* Table management
* Check table availability
* Table reservations
* Cancel reservations
* Order placement
* Order history
* Order details
* Order status management
* Automatic inventory deduction when an order is placed
* Inventory management
* Low-stock alerts
* JWT authentication
* User-specific reservations and orders
* Admin/staff permissions
* Django admin panel

## Technologies Used

* Python
* Django
* Django REST Framework
* PostgreSQL
* Django REST Framework Simple JWT
* Postman
* pgAdmin

## Project Structure

```text
restaurant-management-system/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── restaurant/
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
│
├── manage.py
├── requirements.txt
└── README.md
```

## Database Models

The system contains the following main models:

### Menu Item

Stores restaurant menu items.

* Name
* Description
* Price
* Availability
* Related inventory

### Table

Stores restaurant tables.

* Table number
* Capacity
* Availability

### Reservation

Stores customer reservations.

* User
* Table
* Reservation date
* Reservation time
* Number of guests

### Order

Stores customer orders.

* User
* Table
* Order status
* Total amount
* Creation date

### Order Item

Stores individual items included in an order.

* Order
* Menu item
* Quantity

### Inventory

Stores stock information.

* Item name
* Quantity
* Unit
* Reorder level

## Installation

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd restaurant-management-system
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL database named:

```text
restaurant_management
```

Then configure the database credentials in:

```text
config/settings.py
```

Example:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'restaurant_management',
        'USER': 'your_postgresql_username',
        'PASSWORD': 'your_postgresql_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create an admin user

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

The Django admin panel is available at:

```text
http://127.0.0.1:8000/admin/
```

## Authentication

The project uses JWT authentication.

### Obtain Access and Refresh Tokens

```http
POST /api/login/
```

Example request:

```json
{
    "username": "your_username",
    "password": "your_password"
}
```

The response contains:

```json
{
    "refresh": "your_refresh_token",
    "access": "your_access_token"
}
```

Use the access token in protected API requests:

```text
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Refresh Access Token

```http
POST /api/token/refresh/
```

Example:

```json
{
    "refresh": "your_refresh_token"
}
```

## API Endpoints

### Menu

#### View all menu items

```http
GET /api/menu/
```

#### View a specific menu item

```http
GET /api/menu/<menu_id>/
```

### Tables

#### Check available tables

```http
GET /api/tables/available/?date=2026-10-05&time=20:00&guests=4
```

The API checks:

* Table availability
* Existing reservations
* Table capacity

### Reservations

#### Create a reservation

```http
POST /api/reservations/
```

Example:

```json
{
    "table": 1,
    "reservation_date": "2026-10-05",
    "reservation_time": "20:00:00",
    "number_of_guests": 4
}
```

#### View your reservations

```http
GET /api/reservations/list/
```

#### Cancel your reservation

```http
DELETE /api/reservations/<reservation_id>/cancel/
```

### Orders

#### Place an order

```http
POST /api/orders/
```

Example:

```json
{
    "table": 1,
    "items": [
        {
            "menu_item": 1,
            "quantity": 2
        },
        {
            "menu_item": 2,
            "quantity": 1
        }
    ]
}
```

When an order is placed, the system:

1. Checks whether the menu item is available.
2. Checks whether inventory is configured.
3. Checks whether enough stock is available.
4. Calculates the order total.
5. Creates the order and order items.
6. Automatically reduces inventory.
7. Returns a low-stock alert if stock reaches or falls below the reorder level.

#### View your orders

```http
GET /api/orders/list/
```

#### View order details

```http
GET /api/orders/<order_id>/
```

#### Update order status

```http
PATCH /api/orders/<order_id>/status/
```

Example:

```json
{
    "status": "preparing"
}
```

Order statuses:

* `pending`
* `preparing`
* `completed`
* `cancelled`

Only staff/admin users can update order status.

### Inventory

#### View inventory

```http
GET /api/inventory/
```

Only staff/admin users can access inventory.

#### Update inventory

```http
PATCH /api/inventory/<inventory_id>/
```

Example:

```json
{
    "quantity": 20
}
```

Only staff/admin users can update inventory.

## Order and Inventory Logic

The system automatically manages inventory when an order is placed.

For example:

```text
Initial stock = 10
Order quantity = 3

Remaining stock = 7
```

If the reorder level is:

```text
Reorder level = 8
```

the system returns a low-stock alert because:

```text
7 <= 8
```

However, reaching the reorder level does not prevent the order.

An order is rejected only when the requested quantity is greater than the available stock.

## Permissions

The application uses authentication and staff permissions to protect sensitive operations.

### Regular users can:

* View the menu
* Check table availability
* Create reservations
* View their reservations
* Cancel their own reservations
* Place orders
* View their own orders

### Staff/Admin users can additionally:

* View inventory
* Update inventory
* Update order status
* Access the Django admin panel

## Admin Panel

Django's built-in admin panel is used to manage:

* Menu items
* Tables
* Reservations
* Orders
* Order items
* Inventory
* Users

Access:

```text
http://127.0.0.1:8000/admin/
```

## Testing

The APIs can be tested using **Postman**.

For protected endpoints, first obtain a JWT access token and add it to the request:

```text
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Important test cases include:

* Successful menu retrieval
* Successful table availability check
* Successful reservation
* Duplicate reservation prevention
* Successful order placement
* Insufficient inventory rejection
* Automatic inventory deduction
* Low-stock alert
* Order status update
* Inventory update
* Unauthorized access to admin-only endpoints

## Future Improvements

The following features could be added in future versions:

* Daily sales reports
* Advanced reservation time-slot handling
* Payment integration
* Restaurant staff roles and permissions
* Order notifications
* Customer order tracking
* Stock history and reporting
* API documentation with Swagger/OpenAPI

## License

This project was developed as a backend restaurant management system for learning and internship assignment purposes.
