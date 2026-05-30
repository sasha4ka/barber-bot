from contextlib import asynccontextmanager

from core_shared.services.notification import init_notification_service
from fastapi import FastAPI

from api.settings import settings
from api.v1 import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_notification_service(settings.RABBITMQ_URL)
    print("Web Panel API started successfully.")

    yield

    print("Web Panel API stopped.")


app = FastAPI(title="Web Panel", lifespan=lifespan)

app.include_router(v1_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
