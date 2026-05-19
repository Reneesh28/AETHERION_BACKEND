import json
from pathlib import Path


BUFFER_FILE = Path(
    "buffered_events.jsonl"
)


class DiskBuffer:

    @staticmethod
    def write_event(event: dict):

        with open(
            BUFFER_FILE,
            "a",
            encoding="utf-8",
        ) as f:

            f.write(
                json.dumps(event)
            )

            f.write("\n")