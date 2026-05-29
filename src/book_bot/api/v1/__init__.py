from fastapi import APIRouter

from book_bot.api.v1.endpoints.appointments import router as appointments_router
from book_bot.api.v1.endpoints.masters import router as masters_router
from book_bot.api.v1.endpoints.slots import router as slots_router

router = APIRouter(prefix="/v1")
router.include_router(appointments_router)
router.include_router(slots_router)
router.include_router(masters_router)
