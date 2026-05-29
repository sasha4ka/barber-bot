import datetime

from pydantic import BaseModel, ConfigDict


class SlotResponse(BaseModel):
    slot_id: int
    date: datetime.date
    time_start: datetime.time
    is_booked: bool
    master_id: int

    model_config = ConfigDict(from_attributes=True)
