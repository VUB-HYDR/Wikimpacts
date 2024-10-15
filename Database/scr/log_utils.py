import logging


class Logging:
    @staticmethod
    def get_logger(name: str, level: str = logging.INFO, filename: str | None = None) -> logging.Logger:
        """
        A function that handles logging in all database src functions.
        Change the level to logging.DEBUG when debugging.
        """
        logging.basicConfig(
            format="%(name)s: %(asctime)s %(levelname)-8s %(message)s",
            level=level,
            datefmt="%Y-%m-%d %H:%M:%S",
            filename=filename,
        )
        return logging.getLogger(name)
