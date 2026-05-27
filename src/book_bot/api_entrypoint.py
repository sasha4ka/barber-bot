from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from book_bot.api.v1.endpoints.hello_world import router as hello_router
from book_bot.core.settings import settings
from book_bot.tkq import broker


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.startup()

    redis_client = Redis.from_url(url=settings.REDIS_URL)  # type:ignore
    app.state.redis = redis_client
    print("Web Panel API started successfully.")

    yield

    await redis_client.close()
    await broker.shutdown()
    print("Web Panel API stopped.")


app = FastAPI(title="Web Panel", lifespan=lifespan)

app.include_router(hello_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
