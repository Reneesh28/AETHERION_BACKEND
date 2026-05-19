import orjson


class EventSerializer:

    @staticmethod
    def serialize(event) -> str:

        return orjson.dumps(
            event.model_dump(
                mode="json"
            )
        ).decode()