from typing import Optional
from pydantic import BaseModel, Field, field_validator
from . import config


class QueueCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=config.QUEUE_NAME_MAX_LENGTH)
    avg_service_min: int = Field(default=config.AVG_SERVICE_MIN_DEFAULT,
                                 ge=config.AVG_SERVICE_MIN_MIN,
                                 le=config.AVG_SERVICE_MIN_MAX)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Название не может быть пустым")
        return v


class TicketCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=config.NAME_MAX_LENGTH)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Имя не может быть пустым")
        return v


class PushSubscribe(BaseModel):
    type: str = "webpush"
    endpoint: str
    keys: dict