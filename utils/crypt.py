import base64
from cryptography.fernet import Fernet
from cryptography.hazmat import backends
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class FernetPlus(Fernet):
    def __init__(self, key) -> None:
        super().__init__(key)

    def encrypt_plus(self, message: str) -> str:
        message = message.encode('utf-8')
        token = self.encrypt(message)
        return token.decode('utf-8')

    def decrypt_plus(self, token: str) -> str:
        token = token.encode('utf-8')
        message = self.decrypt(token)
        return message.decode('utf-8')


def get_fernet(password: str) -> FernetPlus:
    password = password.encode('utf-8')
    salt = b'\xb0w\x16gy\xbd\xb2U\xb4\x19\x14\x83,\\\xbd-'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=backends.default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return FernetPlus(key)


def decrypt_express(password: str, token: str) -> str:
    f = get_fernet(password)
    return f.decrypt_plus(token)


if __name__ == "__main__":
    f = get_fernet('')
    token = f.encrypt_plus('')
    print(token)