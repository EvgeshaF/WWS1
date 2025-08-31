import sys
import logging
from datetime import timedelta

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def setup_logger():
    logger.remove()

    # Консольный лог
    logger.add(
        sys.stdout,
        level="DEBUG",
        backtrace=True,
        diagnose=True,
        format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # Лог-файл
    logger.add(
        "logs/wws_{time:YYYYMMDD}.log",  # лог будет автоматически сжат в zip
        rotation="1 days",  # новый лог раз в 1 дней
        retention=timedelta(days=7),  # удаляет архивы старше 7 дней
        compression="zip",  # архивировать
        level="INFO",  # только INFO и выше (без DEBUG)
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {message}",
    )
    # logger.add("logs/{time:YYYYMMDD_HH:mm:ss}_wws.log", rotation="10 MB", retention="10 days", compression="zip", level="DEBUG")

    logging.basicConfig(handlers=[InterceptHandler()], level=logging.DEBUG, force=True)

    for name in logging.root.manager.loggerDict:
        logging.getLogger(name).handlers = [InterceptHandler()]
