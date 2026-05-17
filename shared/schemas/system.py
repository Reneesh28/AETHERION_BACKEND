from datetime import datetime
from pydantic import BaseModel


class BaseEvent(BaseModel):

    trace_id: str

    event_time: datetime

    service_name: str