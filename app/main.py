from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.routes.auth import router as auth_router
from app.routes.auth import router as auth_router
from app.routes.market import router as market_router
from app.services.instrument_loader import download_instruments
from app.services.scheduler import scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # download_instruments()
    print("Starting scheduler...")
    scheduler.start()

    yield

    print("Stopping scheduler...")
    scheduler.shutdown()


app = FastAPI(
    title="Trading Bot",
    lifespan=lifespan
)

app.include_router(auth_router)
app.include_router(market_router)