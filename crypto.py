# crypto.py
import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv

load_dotenv()


class Vault:
    def __init__(self):
        # This is your 'Master Key' from .env
        master_key_hex = os.getenv("MASTER_KEY")
        if not master_key_hex:
            raise ValueError("MASTER_KEY missing in .env! Run 'openssl rand -hex 32' to get one.")
        self.master_key = bytes.fromhex(master_key_hex)

    def _get_aes_gcm(self, key: bytes):
        return AESGCM(key)

    def encrypt_secret(self, plaintext: str) -> dict:
        """
        1. Generates a unique Data Key.
        2. Encrypts the plaintext with the Data Key.
        3. Encrypts the Data Key with the Master Key.
        """
        # Generate random 256-bit Data Key
        data_key = AESGCM.generate_key(bit_length=256)

        # Encrypt the Secret Value
        nonce_val = os.urandom(12)
        cipher_val = self._get_aes_gcm(data_key).encrypt(nonce_val, plaintext.encode(), None)

        # Encrypt the Data Key (Envelope)
        nonce_key = os.urandom(12)
        cipher_key = self._get_aes_gcm(self.master_key).encrypt(nonce_key, data_key, None)

        # Clean up sensitive key from memory
        del data_key

        return {
            "ciphertext": base64.b64encode(nonce_val + cipher_val).decode(),
            "encrypted_key": base64.b64encode(nonce_key + cipher_key).decode()
        }

    def decrypt_secret(self, b64_ciphertext: str, b64_encrypted_key: str) -> str:
        """Unlocks the Data Key using Master Key, then decrypts the secret."""
        # 1. Unlock the Data Key
        key_blob = base64.b64decode(b64_encrypted_key)
        nonce_k, cipher_k = key_blob[:12], key_blob[12:]
        data_key = self._get_aes_gcm(self.master_key).decrypt(nonce_k, cipher_k, None)

        # 2. Decrypt the value
        val_blob = base64.b64decode(b64_ciphertext)
        nonce_v, cipher_v = val_blob[:12], val_blob[12:]
        plaintext = self._get_aes_gcm(data_key).decrypt(nonce_v, cipher_v, None)

        return plaintext.decode()


# Global instance
vault = Vault()