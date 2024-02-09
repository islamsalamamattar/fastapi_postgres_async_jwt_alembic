import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from app.routers.auth import router as auth_router
from app.routers.blog import router as blog_router
from app.routers.post import router as post_router
from app.core.config import settings
from app.core.database import sessionmanager
from fastapi import FastAPI

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()


app = FastAPI(lifespan=lifespan, title=settings.project_name, docs_url="/api/docs")


@app.get("/")
async def root():
    return {"message": "Async, FasAPI, PostgreSQL, JWT authntication, Alembic migrations Boilerplate"}

# Routers
app.include_router(auth_router)
app.include_router(blog_router)
app.include_router(post_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)
