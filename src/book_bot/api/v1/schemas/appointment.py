import datetime

from pydantic import BaseModel, ConfigDict

from book_bot.api.v1.schemas.slot import SlotResponse
from book_bot.models import AppointmentStatus


class ClientInfo(BaseModel):
    id: int
    full_name: str
    phone: str


class AppointmentShortResponse(BaseModel):
    id: int
    user_id: int
    slot_id: int
    slot: SlotResponse
    created_at: datetime.datetime
    status: AppointmentStatus

    model_config = ConfigDict(from_attributes=True)


class AppointmentResponse(BaseModel):
    id: int
    user_id: int
    user: ClientInfo
    slot_id: int
    slot: SlotResponse
    created_at: datetime.datetime
    status: AppointmentStatus

    model_config = ConfigDict(from_attributes=True)


class UpdateAppointmentStatusRequest(BaseModel):
    status: AppointmentStatus


class RescheduleAppointmentRequest(BaseModel):
    new_slot_id: int
