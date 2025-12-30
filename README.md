## fz-creds-manager
A secure, local key-value store using Envelope Encryption (AES-256-GCM) and OAuth2 Authentication.
Built with Python (FastAPI), SQLAlchemy, and Cryptography.

---
### Security Notice

This is a demonstration of security architecture patterns. 
While it uses industry-standard libraries (cryptography, passlib), 
please review the code thoroughly before using it for production secrets.

---
### Setup
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and generate your own keys.
3. Run `uvicorn main:app --reload`

#### Note: `The MASTER_KEY should be handled with care and that this is a "Proof of Concept" before moving to AWS.`


#### To use AWS KMS:
1. Create IAM user (add necessary permissions to access KMS)
2. Go to the KMS Console -> Customer managed keys (add necessary permissions under Key Policy for user to access)


#### Note: `AWS KMS keys have a "double-lock." The user needs permission to use the key, and the Key itself must allow that user.` 


---
### Architecture:
![img.png](img.png)

---
#### Stacks with reason for selecting:
- Backend API - FastAPI (Speed and documentation)
- Hashing - Argon2 (GPU resistance - secure from brute force attack)
- Encryption - AES-GCM	(modern, faster, and safer standard)
- Authentication - JWT (Scalability)
- Database - SQLAlchemy (Security & Readability)

---
License:
MIT License