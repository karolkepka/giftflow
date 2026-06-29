import logging
import os


class Logger:
    """Lightweight logger provider — shared pattern across the application.

    Usage: ``self.log = Logger.get()`` in each class constructor.
    """

    @staticmethod
    def get() -> logging.Logger:
        logging_level = os.getenv("LOG_LEVEL", logging.INFO)
        log = logging.getLogger("giftflow")
        if len(log.handlers) > 0:
            log.setLevel(logging_level)
        else:
            logging.basicConfig(level=logging_level)
        return log
