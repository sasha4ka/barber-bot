import datetime
from typing import List, Optional

from fastapi import HTTPException, Query
from fastapi.routing import APIRouter

from book_bot.api.v1.schemas.appointment import (
    AppointmentResponse,
    AppointmentShortResponse,
    RescheduleAppointmentRequest,
    UpdateAppointmentStatusRequest,
)
from book_bot.services.appointment import (
    CanceledBy,
    SlotAlreadyBookedException,
    SlotNotFoundException,
    cancel_appointment,
    complete_appointment,
    get_appointment,
    get_appointments,
    reschedule_appointment,
)

router = APIRouter(prefix="/appointments")


@router.get("/", response_model=List[AppointmentShortResponse])
async def get_appointments_handler(
    start_date: datetime.date = Query(..., description="Начало диапазона (YYYY-MM-DD)"),
    end_date: datetime.date = Query(..., description="Конец диапазона (YYYY-MM-DD)"),
    master_id: Optional[int] = Query(
        None, description="ID мастера (при отсутствии возвращает для всех)"
    ),
):
    return await get_appointments(
        start_date=start_date, end_date=end_date, master_id=master_id, only_active=False
    )


@router.get("/{id}", response_model=AppointmentResponse)
async def get_appointment_handler(id: int):
    if result := await get_appointment(appointment_id=id):
        return result
    raise HTTPException(status_code=404, detail="Item not found")


@router.patch("/{id}/status", response_model=AppointmentResponse)
async def patch_appointment_status_handler(
    id: int, model: UpdateAppointmentStatusRequest
):
    if not await get_appointment(appointment_id=id):
        raise HTTPException(status_code=404, detail="Item not found")

    if model.status == "cancelled":
        return await cancel_appointment(appointment_id=id, by=CanceledBy.ADMIN)

    elif model.status == "completed":
        return await complete_appointment(appointment_id=id)


@router.patch("/{id}/reschedule", response_model=AppointmentResponse)
async def reschedule_appointment_handler(id: int, model: RescheduleAppointmentRequest):
    if not (appointment := await get_appointment(appointment_id=id)):
        raise HTTPException(status_code=404, detail="Item not found")

    if appointment.slot_id == model.new_slot_id:
        return appointment

    try:
        return await reschedule_appointment(
            appointment_id=id, new_slot_id=model.new_slot_id, by=CanceledBy.ADMIN
        )

    except SlotNotFoundException:
        raise HTTPException(status_code=404, detail="Slot not found")

    except SlotAlreadyBookedException:
        raise HTTPException(status_code=409, detail="Slot is already booked")
