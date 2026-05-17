from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_exponential


kafka_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)