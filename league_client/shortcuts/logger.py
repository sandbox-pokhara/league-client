import logging
import sys
from logging import Formatter
from logging import LogRecord
from logging import StreamHandler
from typing import Any


class ColorFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    colors = {
        logging.DEBUG: grey,
        logging.INFO: blue,
        logging.WARNING: yellow,
        logging.ERROR: red,
        logging.CRITICAL: bold_red,
    }

    def format(self, record: LogRecord):
        color = self.colors.get(record.levelno, self.grey)
        message = super().format(record)
        return color + message + self.reset


# intialize logger
root = logging.getLogger("league_client")
root.setLevel(logging.DEBUG)


# formatter
fmt = "%(asctime)s - %(levelname)s - %(message)s"
datefmt = "%m/%d/%Y %I:%M:%S %p"
formatter = Formatter(fmt, datefmt)
color_formatter = ColorFormatter(fmt, datefmt)

# stream handler
stream_handler = StreamHandler(sys.stdout)
stream_handler.setFormatter(color_formatter)
stream_handler.setLevel(logging.INFO)
root.addHandler(stream_handler)


# ---------------------------------------------------------------------------
# Utility functions at module level.
# Basically delegate everything to the root logger.
# ---------------------------------------------------------------------------
def critical(msg: Any):
    root.critical(msg)


def error(msg: Any):
    root.error(msg)


def exception(msg: Any):
    root.exception(msg)


def warning(msg: Any):
    root.warning(msg)


def info(msg: Any):
    root.info(msg)


def debug(msg: Any):
    root.debug(msg)
