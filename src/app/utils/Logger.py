import logging
import os


class Logger:
    """Lekki dostawca loggera — wzorzec współdzielony w całej aplikacji.

    Użycie: ``self.log = Logger.get()`` w konstruktorze każdej klasy.
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
