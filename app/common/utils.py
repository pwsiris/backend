import getopt
import logging
import sys
from datetime import date, datetime
from types import SimpleNamespace

UNIX_ZERO_DATETIME = datetime.fromisoformat("1970-01-01 00:00+00:00")
UNIX_BELOW_ZERO_DATETIME = datetime.fromisoformat("1969-12-31 23:59:59+00:00")
UNIX_BELOW_ZERO_DATE = date.fromisoformat("1969-12-31")
NON_STEAM_ID_BORDER = 1000 * 1000 * 1000 * 1000
NON_MAL_ID_BORDER = 1000 * 1000 * 1000 * 1000


levelDEBUG = logging.DEBUG
# levelDEBUG = logging.INFO
levelINFO = logging.INFO
FORMAT = "%(levelname)-8s\t%(asctime)s\t\t%(message)s"


def get_args() -> SimpleNamespace:
    args = SimpleNamespace(env="dev", host="0.0.0.0", port=8040)
    opts, _ = getopt.getopt(sys.argv[1:], "H:P:E:", ["host=", "port=", "env="])
    for name, value in opts:
        if name in ("-H", "--host"):
            args.host = value
        if name in ("-P", "--port"):
            args.port = int(value)
        if name in ("-E", "--env"):
            args.env = value
    return args


def get_logger(level: int) -> logging.Logger:
    logger = logging.getLogger()
    logging.basicConfig(format=FORMAT, level=level)
    return logger


def disable_unnecessary_loggers() -> None:
    urllib3_logger = logging.getLogger("urllib3")
    urllib3_logger.setLevel(logging.CRITICAL)

    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.CRITICAL)


def check_empty(value: str | None) -> str | None:
    if value == "":
        raise ValueError("Can't be empty string")
    return value
