import hashlib
import os
from general import constants as const
from general import log_file_builder as log

logger = log.Logger(const.ENCODING_LOGS_FILENAME)


def encode_string(string, salt=None):
    if salt is None:
        salt = os.urandom(16)
    else:
        salt = bytes.fromhex(salt)

    sha256 = hashlib.sha256()
    sha256.update(salt)
    sha256.update(string.encode('utf-8'))
    encoded_string = sha256.hexdigest()
    msg_info = f"String encoded successfully. Encoded string: {encoded_string}. Salt: {salt.hex()}"
    logger.log_info(msg_info)
    return encoded_string, salt.hex()


def check_string(input_string, encoded_string, salt) -> bool:
    sha256 = hashlib.sha256()
    sha256.update(bytes.fromhex(salt))
    sha256.update(input_string.encode('utf-8'))

    if sha256.hexdigest() == encoded_string:
        msg_info = "Compared strings are equal."
        logger.log_info(msg_info)
        return True
    else:
        msg_warning = "Compared strings aren't equal."
        logger.log_info(msg_warning)
        return False
