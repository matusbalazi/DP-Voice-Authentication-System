import mysql.connector as mysql
import requests
from general import log_file_builder as log
from authentication import credentials
from cryptography.fernet import Fernet


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


def quick_check_internet_connection():
    try:
        response = requests.get("https://www.google.com")
        return response.status_code == 200
    except requests.ConnectionError:
        return False


def connect_to_database():
    key = credentials.database_password_key
    cipher_suite = Fernet(key)
    encrypted_password = credentials.database_password_encrypted
    decrypted_password = cipher_suite.decrypt(encrypted_password)
    database_password = decrypted_password.decode()

    try:
        db_connection = mysql.connect(host=credentials.server_host_ip, database=credentials.database_name,
                                      user=credentials.database_user, password=database_password)
        msg_info = "Connected to database succesfully."
        log.log_info(msg_info)
        return db_connection
    except mysql.Error as e:
        msg_error = f"Error connecting to database: {e}"
        log.log_error(msg_error)
        return None
