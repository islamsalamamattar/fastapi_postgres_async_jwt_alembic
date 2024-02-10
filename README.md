# Async FastAPI, JWT Authentication, PostgreSQL DB, Alembic Migrations boilerplate template

## Description

This project offers an asynchronous FastAPI implementation with robust authentication APIs, including user registration, login, email verification, and comprehensive password management (forgot, reset, and update).  
Leveraging asynchronous processing for improved performance, it seamlessly integrates JWT (JSON Web Tokens) authentication for secure user authentication and authorization.  
Furthermore, the application utilizes PostgreSQL as the database backend, managed asynchronously with SQLAlchemy ORM.  
To ensure database schema evolution is hassle-free, Alembic auto-migrations are incorporated into the project.


## Installation

#### clone repository
```bash
git clone https://github.com/islamsalamamattar/fastapi_postgres_async_alembic.git
```

#### create venv & install requirements
```bash
cd fastapi_postgres_async_alembic
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### create postgres DB
```
psql -U postgres
```
```
CREATE DATABASE fastapidb;
CREATE USER dbadmin WITH PASSWORD 'dbpassword';
ALTER ROLE dbadmin SET client_encoding TO 'utf8';
ALTER ROLE dbadmin SET default_transaction_isolation TO 'read committed';
ALTER ROLE dbadmin SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE fastapidb TO dbadmin;
GRANT ALL PRIVILEGES ON SCHEMA public TO dbadmin;
\q
```

#### create a secret key for hashing passwords
```bash
openssl rand -hex 32
```

#### create .env to store enviroment variables
```bash
nano .env
```
```python
PROJECT_NAME="FastAPI Postgres Async Boilerplate"
DATABASE_URL=postgresql+asyncpg://dbadmin:dbpassword@localhost:5432/fastapidb
debug_logs="log.txt"

SECRET_KEY = "Use output of openssl rand -hex 32"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRES_MINUTES = 30
```

#### Intiate alembic migrations and update script
```bash
alembic init app/alembic
cat env.py.example > app/alembic/env.py
```
#### Generate intial migration and upgrade head
```bash
alembic revision --autogenerate -m "Create User, BlackListToken, Blog, and Post Tables"
alembic upgrade head
```

#### Start the app
```
uvicorn app.main:app
```

## Project structure
```
fastapi_postgres_async_alembic
├─ app
│  ├─ alembic
│  │  ├─ README
│  │  ├─ env.py
│  │  └─ script.py.mako
│  ├─ core
│  │  ├─ __init__.py
│  │  ├─ config.py
│  │  ├─ database.py
│  │  ├─ exceptions.py
│  │  └─ jwt.py
│  ├─ models
│  │  ├─ __init__.py
│  │  ├─ blog.py
│  │  ├─ jwt.py
│  │  ├─ post.py
│  │  └─ user.py
│  ├─ routers
│  │  ├─ __init__.py
│  │  ├─ auth.py
│  │  └─ blog.py
│  ├─ schemas
│  │  ├─ blog.py
│  │  ├─ jwt.py
│  │  ├─ mail.py
│  │  ├─ post.py
│  │  └─ user.py
│  ├─ utils
│  │  ├─ __init__.py
│  │  ├─ hash.py
│  │  ├─ mail.py
│  │  └─ utcnow.py
│  ├─ __init__.py
│  └─ main.py
├─ .gitignore
├─ README.md
├─ env.py.example
└─ requirements.txt
```


## Stack
[Python:](https://www.python.org/) The programming language used for development.  
[FastAPI:](https://fastapi.tiangolo.com/) A modern, fast (high-performance) web framework for building APIs with Python.  
[SQLAlchemy:](https://www.sqlalchemy.org/) A powerful and flexible ORM (Object-Relational Mapping) library for working with relational databases.  
[Pydantic:](https://docs.pydantic.dev/latest/) A data validation and settings management library, used for defining schemas and validating data in FastAPI applications.  
[Alembic:](https://alembic.sqlalchemy.org/) A lightweight database migration tool for SQLAlchemy, facilitating easy management of database schema changes.  
[PostgreSQL:](https://www.postgresql.org/) A robust open-source relational database management system.  
[Asyncpg:](https://github.com/MagicStack/asyncpg) An asynchronous PostgreSQL database driver for Python.  
[Passlib:](https://pypi.org/project/passlib/) A password hashing library for secure password storage.  
[Pydantic-settings:](https://pypi.org/project/pydantic-settings/) A Pydantic extension for managing settings and configurations.  
[Python-jose:](https://pypi.org/project/python-jose/) A JWT (JSON Web Tokens) implementation for Python.  
[Python-multipart:](https://pypi.org/project/python-multipart/) A library for parsing multipart/form-data requests, often used for file uploads in FastAPI applications.  
[Uvicorn:](https://www.uvicorn.org/) ASGI server implementation used to run FastAPI applications.

## License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## Acknowledgements
Special thanks to the authors and contributors of  
[FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy](https://www.sqlalchemy.org/), and [Alembic](https://pypi.org/project/alembic/) for their fantastic work and contributions.  
Additionally, I acknowledge the following project for providing inspiration and insights:  
[sabuhibrahim/ FastAPI JWT Authentication Full Example](https://github.com/sabuhibrahim/fastapi-jwt-auth-full-example)  
[ThomasAitken/ demo-fastapi-async-sqlalchemy](https://github.com/ThomasAitken/demo-fastapi-async-sqlalchemy)
