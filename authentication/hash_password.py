import hashlib
import os

def encode_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    else:
        salt = bytes.fromhex(salt)

    sha256 = hashlib.sha256()
    sha256.update(salt)
    sha256.update(password.encode('utf-8'))
    encoded_password = sha256.hexdigest()
    print(encoded_password, salt.hex())
    return encoded_password, salt.hex()

def check_password(input_password, encoded_password, salt):
    sha256 = hashlib.sha256()
    sha256.update(bytes.fromhex(salt))
    sha256.update(input_password.encode('utf-8'))
    return sha256.hexdigest() == encoded_password