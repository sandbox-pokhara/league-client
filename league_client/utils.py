import httpx
from tenacity import retry
from tenacity import retry_if_exception_type
from tenacity import stop_after_attempt

retry_on_read_timeout = retry(
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(httpx.ReadTimeout),
)
