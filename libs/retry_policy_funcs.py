from datetime import timedelta

from temporalio.common import RetryPolicy


def retry() -> RetryPolicy:
    return RetryPolicy(
                backoff_coefficient=2.0,
                maximum_attempts=2,
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=2),
            )