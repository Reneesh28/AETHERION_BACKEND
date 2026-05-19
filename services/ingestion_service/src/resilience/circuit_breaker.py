import logging
import time


logger = logging.getLogger(__name__)


class CircuitBreaker:

    def __init__(
        self,
        failure_threshold=5,
        recovery_timeout=30,
    ):

        self.failure_threshold = (
            failure_threshold
        )

        self.recovery_timeout = (
            recovery_timeout
        )

        self.failure_count = 0

        self.last_failure_time = None

        self.state = "CLOSED"

    def record_failure(self):

        self.failure_count += 1

        self.last_failure_time = time.time()

        if (
            self.failure_count
            >= self.failure_threshold
        ):

            self.state = "OPEN"

            logger.warning(
                "Circuit breaker OPEN"
            )

    def reset(self):

        self.failure_count = 0

        self.state = "CLOSED"

    def can_execute(self):

        if self.state == "CLOSED":
            return True

        if self.state == "OPEN":

            elapsed = (
                time.time()
                - self.last_failure_time
            )

            if elapsed >= self.recovery_timeout:

                self.state = "HALF_OPEN"

                return True

            return False

        return True