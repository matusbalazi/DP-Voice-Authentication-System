import requests
from general import log_file_builder as log


def check_internet_connection():
    try:
        requests.get("https://www.google.com", timeout=3)
        msg_info = "Internet connection is available."
        log.log_info(msg_info)
        return True
    except requests.ConnectionError:
        msg_error = "Internet connection is unavailable."
        log.log_error(msg_error)
        return False