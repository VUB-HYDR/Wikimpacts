import logging


class Logging:
    @staticmethod
    def get_logger(name: str, level: str = logging.INFO) -> logging.Logger:
        """
        A function that handles logging in all database src functions.
        Change the level to logging.DEBUG when debugging.
        """
        logging.basicConfig(
            format="%(name)s: %(asctime)s %(levelname)-8s %(message)s",
            level=level,
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        return logging.getLogger(name)
