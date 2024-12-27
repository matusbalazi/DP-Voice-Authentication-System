import os
from datetime import datetime


class Logger:
    def __init__(self, filename):
        self.filename = filename

    def log_message(self, message, level):
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        with open(self.filename, "a") as log_file:
            log_file.write(f"[{timestamp}] [{level.upper()}] {message}\n")

    def log_info(self, message):
        self.log_message(message, "info")

    def log_warning(self, message):
        self.log_message(message, "warning")

    def log_error(self, message):
        self.log_message(message, "error")
