import uuid


def generate_event_id() -> str:

    return str(uuid.uuid4())


def generate_trace_id() -> str:

    return str(uuid.uuid4())