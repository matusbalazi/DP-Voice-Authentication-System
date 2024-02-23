from datetime import datetime
from general import constants as const

def log_message(message, level, filename=const.LOGS_FILENAME):
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    with open(filename, "a") as log_file:
        log_file.write(f"[{timestamp}] [{level.upper()}] {message}\n")


def log_info(message):
    log_message(message, "info")


def log_warning(message):
    log_message(message, "warning")


def log_error(message):
    log_message(message, "error")