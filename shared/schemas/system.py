from datetime import datetime
from pydantic import BaseModel
from pydantic import Field

class BaseEvent(BaseModel):

    event_id: str

    trace_id: str

    event_type: str

    schema_version: str = "v1"

    service_name: str

    source: str

    event_time: datetime

    processing_time: datetime = Field(
        default_factory=datetime.utcnow
    )