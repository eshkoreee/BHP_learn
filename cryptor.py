from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from io import BytesIO

import base64
import zlib


def generate():
    new_key = RSA.generate(2048)
    private_key = new_key.exportKey()
    public_key = new_key.publickey().exportKey()

    with open('key.pri', 'wb') as f:
        f.write(private_key)

    with open('key.pub', 'wb') as f:
        f.write(public_key)


def get_rsa_cipher(keytype):
    with open(f'key.{keytype}') as f:
        key = f.read() # читаем ранее сгенерированый ключ. любой из двух
    rsakey = RSA.importKey(key)
    return (PKCS1_OAEP.new(rsakey), rsakey.size_in_bytes())


def encrypt(plaintext): # тут мы подгатавливаем входящие данные зашифровывая их и сохдаем полезную нагрузку что бы расшифровка была возможной
    compressed_text = zlib.compress(plaintext) # сжимаем данные

    session_key = get_random_bytes(16) # получаем сессионный ключ шифрования публичного ключа
    cipher_aes = AES.new(session_key, AES.MODE_EAX) # создаем объект шифрования где указываем сессионный ключ и атентификационный режим где добавляют байты tag. если хоть байт был изменен то данные будут недействительны
    ciphertext, tag = cipher_aes.encrypt_and_digest(compressed_text) # шифруем наши сжатые данные и получаем аутентификационный тег

    cipher_rsa, _ = get_rsa_cipher('pub') # читаем публичный ключ
    encrypted_session_key = cipher_rsa.encrypt(session_key) # затем зашифровываем публичный ключ

    msg_payload = encrypted_session_key + cipher_aes.nonce + tag + ciphertext # тут мы конкатенируем: зашифрованый AES ключ RSA способом, случайный байт от AES ключа это необходимо для корректной работы, контрольную сумму для проверки что байты не изменяли и само зашифрованное сообщение
    encrypted = base64.encodebytes(msg_payload) # кодируем в base64 и возвращаем
    return(encrypted)


def decrypt(encrypted):
    encrypted_bytes = BytesIO(base64.decodebytes(encrypted))
    cipher_rsa, keysize_in_bytes = get_rsa_cipher('pri') # получаем приватный ключ

    encrypted_session_key = encrypted_bytes.read(keysize_in_bytes) # читаем полезную нагрузку указывая какие именно байты нужно получить
    nonce = encrypted_bytes.read(16) 
    tag = encrypted_bytes.read(16) # читаем все сообщение и разбиваем его на составляющее читая по 16 байт и отделяя само сообщение от полезной нагрузки
    ciphertext = encrypted_bytes.read()

    session_key = cipher_rsa.decrypt(encrypted_session_key) # затем расшифровываем AES ключ
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce) # создаем копию объекта шифрования для расшифровки
    decrypted = cipher_aes.decrypt_and_verify(ciphertext, tag) # затем расшифровываем наши данные по AES ключу также указывая аутентификационный тег

    plaintext = zlib.decompress(decrypted) # разжимаем наши данные
    return plaintext # и возвращаем


if __name__ == '__main__':
    plaintext = b'hey there you.'
    print(decrypt(encrypt(plaintext)))
