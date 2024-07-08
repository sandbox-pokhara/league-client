import logging
import os
import sys
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from typing import Optional

# register in pylance auto import
__all__ = ["logger"]


def create_logger(
    file_path: str,
    name: str,
    formatter: Optional[logging.Formatter] = None,
    stream: bool = True,
    rotating_file: bool = True,
):
    dirname = os.path.dirname(file_path)
    os.makedirs(dirname, exist_ok=True)

    logger = logging.getLogger(name)
    if formatter is None:
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            "%m/%d/%Y %I:%M:%S %p",
        )
    logger.setLevel(logging.DEBUG)

    if stream:
        stream_handler = StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.INFO)
        logger.addHandler(stream_handler)

    if rotating_file:
        file_handler = RotatingFileHandler(
            file_path, maxBytes=1_048_576, backupCount=100
        )  # 100 x 1 MB

        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    return logger


file_path = os.path.join("logs", "league-client.log")
logger = create_logger(file_path, "league-client")
