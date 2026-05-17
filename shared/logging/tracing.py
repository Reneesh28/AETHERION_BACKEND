from shared.logging.context import generate_trace_id


def build_trace(service_name: str):

    return {
        "trace_id": generate_trace_id(),
        "service_name": service_name,
    }