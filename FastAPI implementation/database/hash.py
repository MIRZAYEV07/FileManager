from passlib.context import CryptContext
from cryptography.fernet import Fernet
from dotenv import load_dotenv, find_dotenv
import os
import sys

pwd_cxt = CryptContext(schemes='bcrypt', deprecated='auto')


class Hash():
    def bcrypt(password: str):
        return pwd_cxt.hash(password)

    def verify(hashed_password, plain_password):
        return pwd_cxt.verify(plain_password, hashed_password)

# class Encryption:
#     def encrpyt(self, key, msg):
#         f = Fernet(key)
#         return f.encrypt(msg)
#     def decrypt(self, key, msg):
#         f = Fernet(key)
#         return f.decrypt(msg)
