from fastapi import FastAPI
from .database import create_db_and_tables
from .routers import login, votes, proposals
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(login.router)
app.include_router(proposals.router)
app.include_router(votes.router)


@app.get("/")
async def ping():
    return {"message": "OK"}
