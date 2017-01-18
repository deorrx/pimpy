import unittest
from aes import AESCipher


class TestAES(unittest.TestCase):
    def test_encrypt_decrypt(self):
        secret = 'kLF9AW8IA0H5WiLcoByZF9H3Yl7FXtBU'
        aes_cipher = AESCipher(secret)

        text = 'dummy text'
        encrypted_text = aes_cipher.encrypt(text)
        print(type(encrypted_text), encrypted_text)

        self.assertEqual(text, aes_cipher.decrypt(encrypted_text))

        text = 'this is dummy text'
        encrypted_text = aes_cipher.encrypt(text)
        print(type(encrypted_text), encrypted_text)

        self.assertEqual(text, aes_cipher.decrypt(encrypted_text))

        text = 'this is dummy text this is dummy text this is dummy text this is dummy text '
        encrypted_text = aes_cipher.encrypt(text)
        print(type(encrypted_text), encrypted_text)

        self.assertEqual(text, aes_cipher.decrypt(encrypted_text))

    def test_encrypt_decrypt_bytes(self):
        secret = 'kLF9AW8IA0H5WiLcoByZF9H3Yl7FXtBU'
        aes_cipher = AESCipher(secret)

        text = b'dummy text'
        encrypted_text = aes_cipher.encrypt_bytes(text)
        print(type(encrypted_text), encrypted_text)

        self.assertEqual(text, aes_cipher.decrypt_bytes(encrypted_text))

        text = b'this is dummy text'
        encrypted_text = aes_cipher.encrypt_bytes(text)
        print(type(encrypted_text), encrypted_text)

        self.assertEqual(text, aes_cipher.decrypt_bytes(encrypted_text))

        text = b'this is dummy text this is dummy text this is dummy text this is dummy text '
        encrypted_text = aes_cipher.encrypt_bytes(text)
        print(type(encrypted_text), encrypted_text)

        self.assertEqual(text, aes_cipher.decrypt_bytes(encrypted_text))


if __name__ == '__main__':
    unittest.main()
