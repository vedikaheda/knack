import time


class RetryError(Exception):
    pass


def retry(func, retries: int = 3, delay_seconds: int = 2):
    last_error = None
    for _ in range(retries):
        try:
            return func()
        except Exception as exc:
            last_error = exc
            time.sleep(delay_seconds)
    raise RetryError(str(last_error))
