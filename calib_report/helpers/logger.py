import logging
import colorlog


logger = None

def get_logger():
    global logger
    if logger is None:
        logger = setup_logger()
    return logger

def setup_logger():
    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(bold_purple)s%(asctime)s%(reset)s %(log_color)s[%(levelname)s]%(reset)s %(message)s",
            log_colors={
                "DEBUG": "white",
                "INFO": "cyan",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
    )

    global logger
    logger= logging.getLogger("calibration")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger

def add_file_handler(log_file_path: str):
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s"
        )
    )
    logger = get_logger()
    logger.addHandler(file_handler)