from typing import Union
from base64 import b64decode
import json

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from utils.env_variables import ENCRYPTION_KEY

from utils.logger_script import logger

backend = default_backend()

def decrypt(stored_encrypted_data: str) -> Union[dict, str]:
    """
    Decrypt the encrypted data using AES-CBC.

    Args:
        stored_encrypted_data (str): The encrypted data, serialized as a string.

    Returns:
        bytes: The decrypted binary data.
    """
    iv, binary_data_length, encrypted_data = stored_encrypted_data.split("$")

    iv = b64decode(iv.encode())
    encrypted_data = b64decode(encrypted_data.encode())
    binary_data_length = int(binary_data_length)
    cipher = Cipher(
        algorithms.AES(b64decode(ENCRYPTION_KEY)), 
        modes.CBC(iv), 
        backend=backend
    )
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

    decrypted_data2: bytes = decrypted_data[:binary_data_length]
    decrypted_data_decoded = decrypted_data2.decode("utf-8")
    if decrypted_data_decoded.startswith("{"):
        decrypted_data_decoded = json.loads(decrypted_data_decoded)
    return decrypted_data_decoded