from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_exponential


retry_with_backoff = retry(

    wait=wait_exponential(
        multiplier=1,
        min=1,
        max=10,
    ),

    stop=stop_after_attempt(5),

    reraise=True,
)