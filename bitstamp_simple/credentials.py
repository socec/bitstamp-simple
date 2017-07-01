import base64
import getpass
import hashlib
import os

from Crypto.Cipher import AES


class Cryptography:
    """
    Handle cryptographic details
    """

    @staticmethod
    def password_hash(password: str):
        hash_object = hashlib.sha256()
        hash_object.update(password.encode('utf-8'))
        return hash_object.digest()

    @staticmethod
    def data_encrypt(password: str, plaintext: bytes) -> bytes:
        key = Cryptography.password_hash(password)
        iv = os.urandom(AES.block_size)
        ciphertext = AES.new(key, AES.MODE_CFB, iv).encrypt(plaintext)
        return base64.b64encode(iv + ciphertext)

    @staticmethod
    def data_decrypt(password: str, ciphertext: bytes) -> bytes:
        data = base64.b64decode(ciphertext)
        iv = data[0:AES.block_size]
        key = Cryptography.password_hash(password)
        return AES.new(key, AES.MODE_CFB, iv).decrypt(data[AES.block_size:]).decode('utf-8')


class Credentials:
    """
    Safely store and load credentials for Bitstamp API
    """
    _credentials_dir = os.path.expanduser('~/.bitstamp_simple')
    _credentials_file = os.path.join(_credentials_dir, 'cred')

    @classmethod
    def save(cls, api_key: str, api_secret: str, client_id: str):
        data = (api_key + api_secret + client_id).encode('utf-8')
        data = Cryptography.data_encrypt(getpass.getpass('Choose your password: '), data)
        os.makedirs(cls._credentials_dir, exist_ok=True)
        with open(cls._credentials_file, 'wb') as f:
            f.write(data)

    @classmethod
    def load(cls) -> (str, str, str):
        try:
            with open(cls._credentials_file, 'rb') as f:
                data = Cryptography.data_decrypt(getpass.getpass('Enter your password: '),
                                                 f.read())
        except OSError:
            print('Could not open credentials file.')
            return ()

        if len(data) != 70:
            print('Credentials file is corrupted ({}). '.format(len(data)))
            return ()

        api_key = data[0:32]
        api_secret = data[32:64]
        client_id = data[64:70]
        return api_key, api_secret, client_id
