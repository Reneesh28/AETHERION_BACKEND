from src.monitoring.counters import counters


class MetricsCollector:

    @staticmethod
    def collect() -> dict:
        return {
            "pipeline": {
                "ticks_consumed": counters.ticks_consumed,
                "orderbooks_consumed": counters.orderbooks_consumed,
                "features_computed": counters.features_computed,
            },
            "cache": {
                "redis_writes_success": counters.redis_writes_success,
                "redis_writes_failed": counters.redis_writes_failed,
            },
            "kafka": {
                "kafka_pub_success": counters.kafka_pub_success,
                "kafka_pub_failed": counters.kafka_pub_failed,
            }
        }
