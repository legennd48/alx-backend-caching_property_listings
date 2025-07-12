# ALX Backend Caching Property Listings

A Django application for property listings with PostgreSQL database and Redis caching, all containerized with Docker.

## Project Structure

```
alx-backend-caching_property_listings/
├── property_listings/          # Django project settings
│   ├── __init__.py
│   ├── settings.py            # Main settings with PostgreSQL and Redis config
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── properties/                # Django app for property management
│   ├── __init__.py
│   ├── models.py             # Property model definition
│   ├── admin.py              # Admin interface configuration
│   ├── views.py
│   ├── tests.py
│   └── migrations/
├── docker-compose.yml        # Docker services configuration
├── requirements.txt          # Python dependencies
├── manage.py                # Django management script
└── test_setup.py            # Setup verification script
```

## Features

- **Property Model** with fields:
  - `title` (CharField, max_length=200)
  - `description` (TextField)
  - `price` (DecimalField, max_digits=10, decimal_places=2)
  - `location` (CharField, max_length=100)
  - `created_at` (DateTimeField, auto_now_add=True)

- **PostgreSQL Database** (port 5433)
- **Redis Cache Backend** (port 6380)
- **Django Admin Interface** with Property management

## Setup Instructions

### Prerequisites
- Python 3.8+
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd alx-backend-caching_property_listings
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Docker services:**
   ```bash
   sudo docker-compose up -d
   ```

5. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Django development server:**
   ```bash
   python manage.py runserver
   ```

### Testing the Setup

Run the setup verification script:
```bash
python test_setup.py
```

## Configuration

### Database Settings
- **Host:** localhost (or 'postgres' when running in Docker network)
- **Port:** 5433
- **Database:** property_listings_db
- **User:** postgres
- **Password:** postgres123

### Redis Cache Settings
- **Host:** localhost (or 'redis' when running in Docker network)
- **Port:** 6380
- **Database:** 1

### Docker Services

The `docker-compose.yml` defines two services:

1. **PostgreSQL:**
   - Image: postgres:latest
   - Port: 5433:5432
   - Environment variables set for database configuration

2. **Redis:**
   - Image: redis:latest
   - Port: 6380:6379

## Usage

### Admin Interface
Access the Django admin at `http://localhost:8000/admin/` to manage properties.

### API Development
The project is ready for API development. You can add Django REST Framework views and serializers to create a full API for property management.

## Dependencies

- Django 5.2.4
- django-redis 6.0.0
- psycopg2-binary 2.9.10
- redis 6.2.0

## Development Notes

- The project uses custom ports (5433 for PostgreSQL, 6380 for Redis) to avoid conflicts with existing services
- Redis is configured as the default cache backend
- The Property model includes proper string representation and admin configuration
- All migrations have been applied and the database schema is ready

## Repository Information

- **GitHub repository:** alx-backend-caching_property_listings
- **Key files:** 
  - `property_listings/settings.py` - Django configuration
  - `docker-compose.yml` - Docker services
  - `properties/models.py` - Property model definition
