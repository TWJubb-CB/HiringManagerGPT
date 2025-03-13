import boto3
import os
from cryptography.fernet import Fernet

def encrypt_api_key(api_key, enc_key = os.getenv('TF_VAR_OPENAI_ENC_KEY')):
    """Encrypts the API key using Fernet symmetric encryption."""
    cipher = Fernet(enc_key.encode("utf-8"))
    encrypted_key = cipher.encrypt(api_key.encode())
    return encrypted_key.decode()

def decrypt_api_key(encrypted_api_key: str, enc_key = os.getenv('TF_VAR_OPENAI_ENC_KEY')):
    """Decrypts the API key using Fernet symmetric encryption."""
    cipher = Fernet(enc_key.encode("utf-8"))
    decrypted_key = cipher.decrypt(encrypted_api_key.encode("utf-8"))
    return decrypted_key.decode()


def store_api_key_in_ssm(parameter_name, api_key, region="eu-west-2"):
    """Stores the API key securely in AWS SSM Parameter Store."""
    ssm_client = boto3.client("ssm", region_name=region)

    api_key_encrypted = encrypt_api_key(api_key)

    response = ssm_client.put_parameter(
        Name=parameter_name,
        Value=api_key_encrypted,
        Type="SecureString",
        Overwrite=True  # Set to True to update an existing parameter
    )

    print(f"Stored parameter '{parameter_name}' successfully.")
    return response



