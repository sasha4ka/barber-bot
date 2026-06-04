from api.v1.endpoints.appointments import router as appointments_router
from api.v1.endpoints.authenticate import router as authentication_router
from api.v1.endpoints.masters import router as masters_router
from api.v1.endpoints.slots import router as slots_router
from fastapi import APIRouter

router = APIRouter(prefix="/v1")
router.include_router(appointments_router)
router.include_router(slots_router)
router.include_router(masters_router)
router.include_router(authentication_router)
