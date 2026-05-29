import datetime

from pydantic import BaseModel, ConfigDict


class SlotResponse(BaseModel):
    id: int
    date: datetime.date
    time_start: datetime.time
    is_booked: bool
    master_id: int

    model_config = ConfigDict(from_attributes=True)


class GenerateSlotsRequest(BaseModel):
    master_id: int
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    slot_duration_minutes: int = 60
