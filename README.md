# FastAPI Postgres Async boilerplate template

## Description
Async FastAPI implementation using PostgresSQL as database, JWT and Oauth2 authntication, and Alembic auto-migrations.

## stack
- python
- fastapi
- SQLAlqemy
- pydantic
- alembic

- postgres

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

