

import os
from base64 import urlsafe_b64encode, urlsafe_b64decode

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from environs import Env

env = Env()
env.read_env()

encryption_key = env.str('ENCRYPTION_KEY')

# function to generate a key using a password
def generate_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

# function to encrypt text
def encrypt(plain_text: str, password: str=encryption_key) -> str:
    # generate a salt and key
    salt = os.urandom(16)
    key = generate_key(password, salt)
    
    # generate a random IV
    iv = os.urandom(16)
    
    # set up AES cipher with key and IV in CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # add padding to the plaintext
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(plain_text.encode()) + padder.finalize()
    
    # encrypt the data
    cipher_text = encryptor.update(padded_data) + encryptor.finalize()
    
    # combine salt, iv, and ciphertext for output
    return urlsafe_b64encode(salt + iv + cipher_text).decode('utf-8')

# function to decrypt text
def decrypt(encrypted_text: str, password: str=encryption_key) -> str:
    # decode the base64 input
    encrypted_data = urlsafe_b64decode(encrypted_text)
    
    # extract salt, iv, and ciphertext from the input
    salt = encrypted_data[:16]
    iv = encrypted_data[16:32]
    cipher_text = encrypted_data[32:]
    
    # generate the key from the password and salt
    key = generate_key(password, salt)
    
    # set up AES cipher with key and IV in CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    # decrypt the data
    padded_data = decryptor.update(cipher_text) + decryptor.finalize()
    
    # remove padding
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plain_text = unpadder.update(padded_data) + unpadder.finalize()
    
    return plain_text.decode('utf-8')
