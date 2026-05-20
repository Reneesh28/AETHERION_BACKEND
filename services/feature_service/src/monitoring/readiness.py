from typing import Optional


class ReadinessCheck:
    redis_store = None
    producer = None
    consumer_supervisor = None

    @classmethod
    def initialize(cls, redis_store, producer, consumer_supervisor) -> None:
        cls.redis_store = redis_store
        cls.producer = producer
        cls.consumer_supervisor = consumer_supervisor

    @classmethod
    def status(cls) -> dict:
        redis_ready = False
        kafka_ready = False
        supervisor_running = False

        if cls.redis_store is not None:
            redis_ready = cls.redis_store._connected

        if cls.producer is not None:
            kafka_ready = cls.producer._connected

        if cls.consumer_supervisor is not None:
            supervisor_running = cls.consumer_supervisor._running

        ready = redis_ready and kafka_ready and supervisor_running

        return {
            "ready": ready,
            "components": {
                "redis_store": "connected" if redis_ready else "disconnected",
                "kafka_producer": "connected" if kafka_ready else "disconnected",
                "consumer_supervisor": "running" if supervisor_running else "stopped"
            }
        }
