import boto3
import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv

load_dotenv()


class Vault:
    def __init__(self):
        # We now use the AWS KMS Key ARN instead of a hex string
        self.kms_key_id = os.getenv("AWS_KMS_KEY_ID")
        self.region = os.getenv("AWS_REGION", "us-east-1")

        # Initialize the AWS KMS Client
        self.kms_client = boto3.client('kms', region_name=self.region)

    def _get_aes_gcm(self, key: bytes):
        return AESGCM(key)

    def encrypt_secret(self, plaintext: str) -> dict:
        """
        1. Asks AWS KMS to generate a new Data Key.
        2. Encrypts the secret with the Plaintext Data Key.
        3. Returns the Ciphertext and the ENCRYPTED Data Key (The Envelope).
        """
        # Request a Data Key from AWS
        response = self.kms_client.generate_data_key(
            KeyId=self.kms_key_id,
            KeySpec='AES_256'
        )

        plaintext_data_key = response['Plaintext']
        encrypted_data_key = response['CiphertextBlob']  # This is the envelope

        # Encrypt the actual value
        nonce = os.urandom(12)
        aesgcm = self._get_aes_gcm(plaintext_data_key)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)

        # Security Best Practice: Explicitly wipe the plaintext key from memory
        del plaintext_data_key

        return {
            "ciphertext": base64.b64encode(nonce + ciphertext).decode(),
            "encrypted_key": base64.b64encode(encrypted_data_key).decode()
        }

    def decrypt_secret(self, b64_ciphertext: str, b64_encrypted_key: str) -> str:
        """
        1. Sends the 'Envelope' back to AWS KMS to be decrypted.
        2. Uses the returned Plaintext Data Key to unlock the secret.
        """
        encrypted_key_bytes = base64.b64decode(b64_encrypted_key)

        # Ask AWS to decrypt the data key
        response = self.kms_client.decrypt(
            CiphertextBlob=encrypted_key_bytes,
            KeyId=self.kms_key_id  # Optional but recommended for security
        )

        plaintext_data_key = response['Plaintext']

        # Decrypt the ciphertext
        raw_payload = base64.b64decode(b64_ciphertext)
        nonce, cipher_v = raw_payload[:12], raw_payload[12:]

        aesgcm = self._get_aes_gcm(plaintext_data_key)
        plaintext = aesgcm.decrypt(nonce, cipher_v, None)

        return plaintext.decode()


vault = Vault()