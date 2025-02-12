import json
import os
from general import constants as const
from general import log_file_builder as log

logger = log.Logger(const.USERS_LOGS_FILENAME)


def load_json_file(filename):
    try:
        with open(filename, "r") as file:
            data = file.read().strip()
            if not data:
                return {}
            data = json.loads(data)
            msg_success = f"File {filename} loaded successfully."
            logger.log_info(msg_success)
            return data
    except FileNotFoundError:
        msg_error = f"File {filename} not found, load operation failed."
        logger.log_error(msg_error)
        return {}


def save_json_file(elements, filename):
    if not os.path.exists(filename):
        msg_warning = f"File {filename} does not exist. File will be created."
        logger.log_warning(msg_warning)

    with open(filename, "w") as file:
        json.dump(elements, file)


def add_user_to_json_file(users, new_user_key, new_user_values, filename):
    success = False

    if new_user_key not in users:
        users[new_user_key] = new_user_values
        save_json_file(users, filename)
        success = True
        msg_success = f"User {new_user_key} added successfully."
        logger.log_info(msg_success)
    else:
        msg_error = f"User {new_user_key} already exists, add operation failed."
        logger.log_error(msg_error)

    return success


def remove_user_from_json_file(users, user_key, filename):
    success = False

    if user_key in users:
        del users[user_key]
        save_json_file(users, filename)
        success = True
        msg_success = f"User {user_key} removed successfully."
        logger.log_info(msg_success)
    else:
        msg_error = f"User {user_key} not found, remove operation failed."
        logger.log_error(msg_error)

    return success


def compare_json_files(filename_1, filename_2) -> bool:
    with open(filename_1, 'r') as file_1:
        data_1 = json.load(file_1)

    with open(filename_2, 'r') as file_2:
        data_2 = json.load(file_2)

    if data_1 == data_2:
        return True
    else:
        return False
