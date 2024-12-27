import os
from database import connection_controller as conn
from database import json_file_builder as json
from general import constants as const
from general import log_file_builder as log

logger = log.Logger(const.DATABASE_LOGS_FILENAME)


def find_user(users, login_name):
    user_exists = False

    for key, value in users.items():
        if key == login_name:
            user_exists = True
            break

    return user_exists


def sync_with_local():
    users = json.load_json_file(const.USERS_FILENAME)

    db_connection = conn.connect_to_database()
    cursor = db_connection.cursor()

    sql_query = "SELECT * FROM users"

    try:
        cursor.execute(sql_query)
        records = cursor.fetchall()

        for record in records:
            login_name = record[1]
            user_folder = f"{const.SPEAKER_VOICEPRINTS_DIR}{login_name}/"

            if not find_user(users, login_name):
                json.add_user_to_json_file(users, record[1], (record[2], record[3], record[4]),
                                           const.USERS_FILENAME)

            voiceprint_columns = record[5:]

            if not os.path.isdir(user_folder):
                os.makedirs(user_folder, exist_ok=True)

            if not os.listdir(user_folder):
                for i, voiceprint_data in enumerate(voiceprint_columns, start=0):
                    if voiceprint_data is not None:
                        voiceprint_filename = f"{login_name}_{i}.pt"
                        voiceprint_path = os.path.join(user_folder, voiceprint_filename)
                        with open(voiceprint_path, "wb") as file:
                            file.write(voiceprint_data)
                        msg_info = f"Voiceprint {i} saved successfully to {voiceprint_path}."
                        logger.log_info(msg_info)

    except Exception as e:
        msg_error = f"Error during sync with database: {e}"
        logger.log_error(msg_error)
    finally:
        cursor.close()
        db_connection.close()


def insert_user_to_db(login_name):
    users = json.load_json_file(const.USERS_FILENAME)

    if find_user(users, login_name):
        db_connection = conn.connect_to_database()
        cursor = db_connection.cursor()

        unique_phrase_hash = list(users[login_name])[0]
        unique_phrase_salt = list(users[login_name])[1]
        registration_w_internet = int(list(users[login_name])[2])

        voiceprints_folder = f"{const.SPEAKER_VOICEPRINTS_DIR}{login_name}/"
        voiceprints = []

        for filename in os.listdir(voiceprints_folder):
            if filename.endswith(".pt"):
                voiceprint_file = os.path.join(voiceprints_folder, filename)

                with open(voiceprint_file, "rb") as file:
                    voiceprint_data = file.read()

                voiceprints.append(voiceprint_data)

        user_id = None
        columns = ["user_id", "login_name", "unique_phrase_hash", "unique_phrase_salt", "registration_w_internet"]
        data = [user_id, login_name, unique_phrase_hash, unique_phrase_salt, registration_w_internet]

        for i, voiceprint_data in enumerate(voiceprints, start=1):
            column_name = f"voiceprint_{i}"
            columns.append(column_name)
            data.append(voiceprint_data)

        placeholders = ', '.join(['%s'] * len(columns))
        sql_query = f"INSERT INTO users ({', '.join(columns)}) VALUES ({placeholders})"

        try:
            cursor.execute(sql_query, data)
            db_connection.commit()
            msg_info = f"User {login_name} inserted successfully into database."
            logger.log_info(msg_info)
        except Exception as e:
            msg_error = f"Error inserting user {login_name} into database: {e}"
            logger.log_error(msg_error)
        finally:
            cursor.close()
            db_connection.close()
    else:
        msg_warning = f"User {login_name} can't be inserted to database."
        logger.log_warning(msg_warning)


def delete_user_from_db(login_name):
    db_connection = conn.connect_to_database()
    cursor = db_connection.cursor()

    sql_query = "DELETE FROM users WHERE login_name = %s"

    try:
        cursor.execute(sql_query, (login_name,))
        db_connection.commit()

        deleted_rows = cursor.rowcount

        if deleted_rows > 0:
            msg_info = f"User {login_name} successfully deleted from database."
            logger.log_info(msg_info)
        else:
            msg_info = f"No records found for user {login_name} in the database."
            logger.log_info(msg_info)
    except Exception as e:
        msg_error = f"Error deleting user {login_name} from database: {e}"
        logger.log_error(msg_error)
    finally:
        cursor.close()
        db_connection.close()


def select_user_from_db(login_name):
    records = None
    users = json.load_json_file(const.USERS_FILENAME)

    if find_user(users, login_name):
        db_connection = conn.connect_to_database()
        cursor = db_connection.cursor()

        sql_query = "SELECT * FROM users WHERE login_name = %s"

        try:
            cursor.execute(sql_query, (login_name,))
            records = cursor.fetchall()

            if records:
                msg_info = f"User {login_name} successfully found in the database."
                logger.log_info(msg_info)
            else:
                msg_warning = f"No records were found for the user {login_name} in the database."
                logger.log_warning(msg_warning)
        except Exception as e:
            msg_error = f"Error selecting user {login_name} from database: {e}"
            logger.log_error(msg_error)
        finally:
            cursor.close()
            db_connection.close()
            return records
    else:
        msg_warning = f"User {login_name} can't be selected from database."
        logger.log_warning(msg_warning)


def get_all_users_from_db():
    records = None
    users = json.load_json_file(const.TMP_USERS_FILENAME)

    db_connection = conn.connect_to_database()
    cursor = db_connection.cursor()

    sql_query = "SELECT * FROM users"

    try:
        cursor.execute(sql_query)
        records = cursor.fetchall()

        if records:
            for record in records:
                json.add_user_to_json_file(users, record[1], (record[2], record[3], record[4]),
                                           const.TMP_USERS_FILENAME)
        else:
            msg_warning = f"No records were found in the database."
            logger.log_warning(msg_warning)
    except Exception as e:
        msg_error = f"Error selecting all records from database: {e}"
        logger.log_error(msg_error)
    finally:
        cursor.close()
        db_connection.close()
        return records
