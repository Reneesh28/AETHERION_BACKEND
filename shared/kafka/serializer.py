import json


def serialize_event(event):

    return json.dumps(
        event.model_dump(),
        default=str
    ).encode("utf-8")