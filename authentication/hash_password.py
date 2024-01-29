import hashlib
import os

def encode_password(password, sol=None):
    if sol is None:
        sol = os.urandom(16)
    else:
        sol = bytes.fromhex(sol)

    sha256 = hashlib.sha256()
    sha256.update(sol)
    sha256.update(password.encode('utf-8'))
    encoded_password = sha256.hexdigest()
    return encoded_password, sol.hex()

def check_password(input_password, encoded_password, sol):
    sha256 = hashlib.sha256()
    sha256.update(bytes.fromhex(sol))
    sha256.update(input_password.encode('utf-8'))
    return sha256.hexdigest() == encoded_password