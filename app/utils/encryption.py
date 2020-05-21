import binascii

from Crypto.Cipher import AES

from ..config import AES_KEY


def encrypt_with_key(key, plain_text):
    mod = len(plain_text) % 16
    if mod > 0:
        # 补齐16的倍数
        zero = '\0' * (16 - mod)
        plain_text += zero
    aes = AES.new(key.encode(), AES.MODE_ECB)
    cipher_text = binascii.hexlify(aes.encrypt(plain_text.encode())).decode()
    return cipher_text


def decrypt_with_key(key, cipher_text):
    aes = AES.new(key.encode(), AES.MODE_ECB)
    plain_text = aes.decrypt(binascii.unhexlify(cipher_text)).decode().rstrip('\0')
    return plain_text


def encrypt(plain_text: str) -> str:
    """
    encrypt text
    :param plain_text: raw text
    :return: encrypted text
    """
    return encrypt_with_key(AES_KEY, plain_text)


def decrypt(cipher_text: str) -> str:
    """
    decrypt text
    :param cipher_text: encrypted text
    :return: decrypted text
    """
    return decrypt_with_key(AES_KEY, cipher_text)


def hash_password(password: str) -> str:
    return encrypt(password)


def check_password(password: str, hashed_password: str) -> bool:
    return encrypt(password) == hashed_password
