"""
Based on Stackoverflow Answer: http://stackoverflow.com/a/12525165/353550
Taken from https://gist.github.com/psjinx/2070045424d558839604
"""
import base64


from Crypto.Cipher import AES

# Trick for PyCrypto under Windows
try:
    from Crypto import Random

    def make_iv():
        return Random.new().read(AES.block_size)
except ImportError:
    from os import urandom

    def make_iv():
        return urandom(AES.block_size)

BS = AES.block_size


def pad(s):
    return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)


def unpad(s):
    return s[:-ord(s[len(s)-1:])]


def pad_bytes(s: bytes) -> bytes:
    return s + bytearray(chr(BS - len(s) % BS), 'utf-8') * (BS - len(s) % BS)


def unpad_bytes(s: bytes) -> bytes:
    return s[:-ord(s[len(s)-1:])]


class AESCipher(object):
    def __init__(self, key):
        self.key = key

    def encrypt(self, raw):
        raw = pad(raw)
        iv = make_iv()
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[AES.block_size:])).decode("utf-8")

    def encrypt_bytes(self, raw: bytes) -> bytes:
        raw = pad_bytes(raw)
        iv = make_iv()
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(raw)

    def decrypt_bytes(self, enc: bytes) -> bytes:
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad_bytes(cipher.decrypt(enc[AES.block_size:]))


if __name__ == '__main__':
    raise RuntimeError('This module must not be used independently')
