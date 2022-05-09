import logging
import sys
from logging import StreamHandler

logger = logging.Logger('client')
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    '%m/%d/%Y %I:%M:%S %p',
)
stream_handler = StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)
