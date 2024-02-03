# FastAPI Postgres Async boilerplate template

## Description

This project offers an asynchronous FastAPI implementation with robust authentication APIs, including user registration, login, email verification, and comprehensive password management (forgot, reset, and update).
Leveraging asynchronous processing for improved performance, it seamlessly integrates JWT (JSON Web Tokens) authentication for secure user authentication and authorization.
Furthermore, the application utilizes PostgreSQL as the database backend, managed asynchronously with SQLAlchemy ORM.
To ensure database schema evolution is hassle-free, Alembic auto-migrations are incorporated into the project.

## Stack
- Python: The programming language used for development.
- FastAPI: A modern, fast (high-performance) web framework for building APIs with Python.
- SQLAlchemy: A powerful and flexible ORM (Object-Relational Mapping) library for working with relational databases.
- Pydantic: A data validation and settings management library, used for defining schemas and validating data in FastAPI applications.
- Alembic: A lightweight database migration tool for SQLAlchemy, facilitating easy management of database schema changes.
- PostgreSQL: A robust open-source relational database management system.
- Asyncpg: An asynchronous PostgreSQL database driver for Python.
- Passlib: A password hashing library for secure password storage.
- Pydantic-settings: A Pydantic extension for managing settings and configurations.
- Python-jose: A JWT (JSON Web Tokens) implementation for Python.
- Python-multipart: A library for parsing multipart/form-data requests, often used for file uploads in FastAPI applications.
- Uvicorn: ASGI server implementation used to run FastAPI applications.


## Instalation

- clone repository
```bash
git clone https://github.com/islamsalamamattar/fastapi_postgres_async_alembic.git
```
- Project structure
```
fastapi_postgres,
├─ .env,
├─ README.md,
├─ alembic.ini,
├─ app,
│  ├─ __init__.py,
│  ├─ alembic,
│  │  ├─ README,
│  │  ├─ env.py,
│  │  ├─ script.py.mako,
│  │  └─ versions,
│  ├─ core,
│  │  ├─ __init__.py,
│  │  ├─ config.py,
│  │  ├─ database.py,
│  │  ├─ exceptions.py,
│  │  └─ jwt.py,
│  ├─ main.py,
│  ├─ models,
│  │  ├─ __init__.py,
│  │  ├─ jwt.py,
│  │  └─ user.py,
│  ├─ routers,
│  │  ├─ __init__.py,
│  │  └─ auth.py,
│  ├─ schemas,
│  │  ├─ email.py,
│  │  ├─ jwt.py,
│  │  └─ user.py,
│  └─ utils,
│     ├─ __init__.py,
│     ├─ emails.py,
│     ├─ hash.py,
│     └─ utcnow.py,
└─ requirements.txt,

```
- create venv & install requirements
```bash
cd fastapi_postgres
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

- create postgres DB
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

- create a secret key for hashing passwords
```bash
openssl rand -hex 32
```

- create .env to store enviroment variables
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

- Intiate alembic migrations
```bash
alembic init app/alembic
```

- update alembic script by replacing the content of app/alembic/env.py with the following:
```bash
nano app/alembic/env.py
```
```python
# app/alembic/env.py

import asyncio
import os
from dotenv import load_dotenv
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from app.models import Base
from asyncpg import Connection
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

load_dotenv()
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)  # type: ignore

# add your model's MetaData object here
target_metadata = Base.metadata

def get_url():
    return os.getenv("DATABASE_URL")

def run_migrations_offline():
    """Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    Calls to context.execute() here emit the given string to the
    script output.
    """
    # url = config.get_main_option("sqlalchemy.url")
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

- create migration intial migration and upgrade head
```bash
alembic revision --autogenerate -m "Create User and BlackListToken"
alembic upgrade head
```

- Start the app
```
uvicorn app.main:app
```

## License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## Acknowledgements
Special thanks to the authors and contributors of FastAPI, SQLAlchemy, and Alembic for their fantastic work and contributions. Additionally, I acknowledge the following project for providing inspiration and insights: 
- [FastAPI JWT Authentication Full Example](https://github.com/sabuhibrahim/fastapi-jwt-auth-full-example).

