from contextlib import asynccontextmanager

from api.authenticator import init_jwt_authenticator
from api.settings import settings
from api.v1 import router as v1_router
from core_shared.services.notification import init_notification_service
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_notification_service(settings.RABBITMQ_URL)
    init_jwt_authenticator(settings.JWT_SECRET_KEY)

    print("Web Panel API started successfully.")

    yield

    print("Web Panel API stopped.")


app = FastAPI(title="Web Panel", lifespan=lifespan)

app.include_router(v1_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
