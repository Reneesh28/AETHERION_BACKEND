class PipelineCounters:
    ticks_consumed = 0
    orderbooks_consumed = 0
    features_computed = 0
    redis_writes_success = 0
    redis_writes_failed = 0
    kafka_pub_success = 0
    kafka_pub_failed = 0


counters = PipelineCounters()
