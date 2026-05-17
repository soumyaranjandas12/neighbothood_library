# Neighborhood Library Management System

A Django-based library management system for managing books, readers, librarians, borrowing records, returns, and fines.

## Features

- User registration and login
- Role-based access for:
  - Librarians
  - Readers
- Book catalog management
- Book search by title, author, or ISBN
- Borrowing and returning books
- Fine calculation for overdue books
- Fine collection tracking
- Reader and librarian dashboards
- Pytest-based unit testing

## Tech Stack

- Python
- Django
- PostgreSQL
- HTML/CSS
- Bootstrap
- Pytest
- pytest-django
- python-dotenv

## Project Structure

text neighborhood_library/ ├── library/ │ ├── migrations/ │ ├── admin.py │ ├── apps.py │ ├── forms.py │ ├── mixins.py │ ├── models.py │ ├── tests.py │ ├── urls.py │ └── views.py ├── library_project/ │ ├── **init**.py │ ├── asgi.py │ ├── settings.py │ ├── urls.py │ └── wsgi.py ├── static/ ├── templates/ ├── manage.py ├── pytest.ini ├── requirements.txt ├── seeds.py ├── .env └── README.md


## Prerequisites

Make sure the following are installed on your system:

- Python 3.10 or higher
- PostgreSQL
- pip
- virtualenv

## Installation

### 1. Clone the Repository
bash git clone <your-repository-url> cd neighborhood_library


### 2. Create a Virtual Environment

On Windows:

bash python -m venv venv``` 

Activate it:
```

bash venv\Scripts\activate``` 

On macOS/Linux:
```

bash python3 -m venv venv``` 

Activate it:
```

bash source venv/bin/activate``` 

### 3. Install Dependencies
```

bash pip install -r requirements.txt``` 

