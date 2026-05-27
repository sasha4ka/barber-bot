from fastapi.routing import APIRouter

router = APIRouter(prefix="/hello")


@router.get("/world")
async def hello_world_handler():
    return {"text": "Hello world"}
