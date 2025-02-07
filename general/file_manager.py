import os
from general import constants as const
from general import log_file_builder as log

logger = log.Logger(const.FILE_MANAGER_LOGS_FILENAME)


def move_and_rename_audio(original_filename, new_filename, destination_dir) -> bool:
    try:
        original_file_path = os.path.abspath(original_filename)
        new_file_path = os.path.join(destination_dir, new_filename)
        os.rename(original_file_path, new_file_path)
        msg_info = f"Audio {original_file_path} was succesfully moved and renamed to {new_file_path}."
        logger.log_info(msg_info)
        return True

    except FileNotFoundError:
        msg_error = "Original or destination file path does not exist."
        logger.log_error(msg_error)
        return False

    except Exception as e:
        msg_error = f"Moving or renaming audio {original_filename} failed. An error occurred: {str(e)}"
        logger.log_error(msg_error)
        return False


def remove_dir_with_files(dir):
    try:
        for root, dirs, files in os.walk(dir, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                os.rmdir(dir_path)

        os.rmdir(dir)
        msg_info = f"Directory {dir} and all its contents removed successfully."
        logger.log_info(msg_info)
        return True

    except FileNotFoundError:
        msg_error = f"Directory {dir} does not exist."
        logger.log_error(msg_error)
        return False

    except PermissionError:
        msg_error = f"You do not have permission to remove the directory {dir}."
        logger.log_error(msg_error)
        return False

    except Exception as e:
        msg_error = f"Removing the directory {dir} failed. An error occurred: {str(e)}"
        logger.log_error(msg_error)
        return False


def get_subdirectory_names(dir):
    subdir_names = []

    for entry in os.listdir(dir):
        full_path = os.path.join(dir, entry)

        if os.path.isdir(full_path) and not os.path.islink(full_path):
            subdir_names.append(entry)

    return subdir_names
