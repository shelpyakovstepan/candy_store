# STDLIB
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


formatter = logging.Formatter(
    "%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt="%H:%M:%S",
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger.addHandler(handler)

logger.info("START")