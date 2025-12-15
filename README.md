# fz-creds-manager

A secure, local key-value store using Envelope Encryption (AES-256-GCM) and OAuth2 Authentication.
Built with Python (FastAPI), SQLAlchemy, and Cryptography.

## Security Notice
This is a demonstration of security architecture patterns. 
While it uses industry-standard libraries (cryptography, passlib), 
please review the code thoroughly before using it for production secrets.

## Setup
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and generate your own keys.
3. Run `uvicorn main:app --reload`
