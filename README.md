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

<img width="1863" height="957" alt="image" src="https://github.com/user-attachments/assets/ae652fbb-cb2f-419a-98a5-643fe15a0e4a" />
<img width="1712" height="892" alt="image" src="https://github.com/user-attachments/assets/e72f7080-ea8b-4b55-be93-3e626a787322" />
<img width="1716" height="872" alt="image" src="https://github.com/user-attachments/assets/8a877f42-7525-4c7c-a0ef-26fd779bd238" />
<img width="1822" height="895" alt="image" src="https://github.com/user-attachments/assets/bdbc77df-0023-42e5-b034-8788bc6b757e" />
<img width="1732" height="930" alt="image" src="https://github.com/user-attachments/assets/4f4688bb-195f-45ee-bee6-5f38e95f10b6" />





