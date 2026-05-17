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
- PostgreSQL is install and database 'library_databse' is created.
- pip
- virtualenv

## Installation

### 1. Clone the Repository
>> git init
>> git clone https://github.com/soumyaranjandas12/neighbothood_library.git


### 2. Create a Virtual Environment
>> cd neighborhood_library
>> python -m venv venv


### 3. Activate the virtual environment
>> .\venv\Scripts\activate

### 4. Install the dependencies
>> pip install -r requirements.txt

### 5. Migrate the database
>> python manage.py makemigrations
>> python manage.py migrate

### 6. Create Superuser
>> python manage.py createsuperuser

### 7. Start the Application
>> python manage.py runserver

Once started you can use the IP and port provided in the startup to use the webpage.
Asper the sample screenshots below you get separate dashboards for both reader and librarian. Only Librarian can add, delete, update and issue and return books.
In the reader dashborad,the reader can view all the books with the available copies and there is also one tab to tell the user the books that has been issue to him/her.

<img width="1821" height="776" alt="image" src="https://github.com/user-attachments/assets/eb6e511d-7870-493d-9826-87bdf4ce60bf" />
<img width="1706" height="792" alt="image" src="https://github.com/user-attachments/assets/21ee0e68-82b6-4ea1-b637-0a5f68a44ebb" />
<img width="1737" height="875" alt="image" src="https://github.com/user-attachments/assets/2f5a2564-0e64-46a6-93f4-d09947efbdfa" />
<img width="1742" height="857" alt="image" src="https://github.com/user-attachments/assets/4bad4c18-df50-4798-b3da-800e882da376" />
<img width="1713" height="911" alt="image" src="https://github.com/user-attachments/assets/80b68aaa-f964-4c38-be03-c4aaeae81084" />










