from hashlib import pbkdf2_hmac, sha256
import os


def hash_password(password, hash_type='sha256'):
    if hash_type == 'sha256':
        return sha256(password.encode('utf-8')).hexdigest()
    elif hash_type == 'pbkdf2':
        return pbkdf2_hmac(
            'sha256', password.encode('utf-8'), os.environ['SALT'].encode('utf-8'), 100000
        ).hexdigest()
