import datetime
from enum import Enum

from sqlalchemy import BigInteger, Date, ForeignKey, String, Time, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from book_bot.core.database import Base


class AppointmentStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(64))
    phone: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', NOW())")
    )

    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment", back_populates="user", cascade="all, delete-orphan"
    )


class Slot(Base):
    __tablename__ = "slots"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    time_start: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    is_booked: Mapped[bool] = mapped_column(default=False, server_default="false")

    appointment: Mapped["Appointment"] = relationship(back_populates="slot")


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(User.id, ondelete="CASCADE"), nullable=False
    )
    slot_id: Mapped[int] = mapped_column(
        ForeignKey(Slot.id, ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', NOW())")
    )
    status: Mapped[AppointmentStatus] = mapped_column(
        String(20), default=AppointmentStatus.ACTIVE, server_default="active"
    )

    user: Mapped["User"] = relationship(back_populates="appointments")
    slot: Mapped["Slot"] = relationship(back_populates="appointment")
