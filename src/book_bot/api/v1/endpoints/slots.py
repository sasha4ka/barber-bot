import datetime
from typing import Optional

from fastapi import APIRouter, Query

from book_bot.api.v1.schemas.slot import GenerateSlotsRequest, SlotResponse
from book_bot.services.slot import generate_slots_for_date, get_slots

router = APIRouter(prefix="/slots")


@router.get("", response_model=list[SlotResponse])
async def get_slots_handler(
    start_date: datetime.date = Query(..., description="Начало диапазона (YYYY-MM-DD)"),
    end_date: datetime.date = Query(..., description="Конец диапазона (YYYY-MM-DD)"),
    master_id: Optional[int] = Query(
        None, description="ID мастера (при отсутствии возвращает для всех)"
    ),
):
    return await get_slots(
        start_date=start_date, end_date=end_date, master_id=master_id
    )


@router.post("/generate", response_model=list[SlotResponse])
async def generate_slots_handler(model: GenerateSlotsRequest):
    return await generate_slots_for_date(
        master_id=model.master_id,
        target_date=model.date,
        work_start=model.start_time,
        work_end=model.end_time,
        slot_duration_minutes=model.slot_duration_minutes,
    )
