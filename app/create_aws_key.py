import os
from cryptography.fernet import Fernet
from aws_test import encrypt_api_key
from dotenv import load_dotenv
import dotenv

"""
print the environment variable TF_VAR_OPENAI_API_KEY (encryption key); if it doesn't exist, create it
"""

load_dotenv()

# ensure there is an encryption key, create one if needed
OPENAI_ENC_KEY = os.getenv('TF_VAR_OPENAI_ENC_KEY')
if not OPENAI_ENC_KEY:
    dotenv_file = dotenv.find_dotenv()
    secret_key = Fernet.generate_key().decode("utf-8")
    dotenv.set_key(dotenv_file,
                   key_to_set="TF_VAR_OPENAI_ENC_KEY",
                   value_to_set=secret_key)

enc = encrypt_api_key(os.getenv('TF_VAR_OPENAI_API_KEY'),
                      OPENAI_ENC_KEY)
print(enc)
