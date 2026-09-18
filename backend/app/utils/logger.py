"""
Logging setup using Python's standard logging module (with loguru compatibility).
"""

import sys
import logging

try:
    from loguru import logger
    def setup_logging():
        logger.remove()
        logger.add(
            sys.stdout,
            level="INFO",
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
            colorize=True,
        )
        return logger
    app_logger = logger
except ImportError:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    class LoggerCompat:
        def __init__(self):
            self._log = logging.getLogger("customer_support_ai")
        def info(self, msg, *args, **kwargs):
            if args:
                try: msg = msg.format(*args)
                except Exception: pass
            self._log.info(msg)
        def warning(self, msg, *args, **kwargs):
            if args:
                try: msg = msg.format(*args)
                except Exception: pass
            self._log.warning(msg)
        def error(self, msg, *args, **kwargs):
            if args:
                try: msg = msg.format(*args)
                except Exception: pass
            self._log.error(msg)
        def debug(self, msg, *args, **kwargs):
            if args:
                try: msg = msg.format(*args)
                except Exception: pass
            self._log.debug(msg)

    app_logger = LoggerCompat()
    def setup_logging():
        return app_logger
