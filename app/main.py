# main.py (Phase 1: Registration & Core Setup)
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import our project modules
import models, auth, database
from database import engine, get_db

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt # Used to decode the token

import crypto
from fastapi.middleware.cors import CORSMiddleware

# This line creates the actual .db file and tables when the app starts
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="fz-creds-manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, you'd put your domain here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "online", "project": "fz-creds-manager"}

# User sends JSON -> 2. FastAPI validates -> 3. App checks for duplicates $\rightarrow$
# 4. Auth hashes password -> 5. DB saves user -> 6. User receives "Success".
@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: models.UserCreate, db: Session = Depends(get_db)):
    # 1. Check if user already exists
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    # 2. Hash the password using our auth module
    hashed_pw = auth.get_password_hash(user_data.password)

    # 3. Save to database
    new_user = models.User(username=user_data.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()

    return {"message": f"User '{user_data.username}' registered successfully."}

# ------------ next part login -----------

# --- SECURITY CONFIGURATION ---
# This tells FastAPI where the login logic lives for the "Authorize" button
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# --- DEPENDENCY: THE GATEKEEPER ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Decodes the JWT token. If valid, returns the User object.
    If invalid or expired, it automatically kicks the user out (401).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token using the secret from your .env
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


# --- LOGIN & TOKEN ---
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Check if user exists
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    # 2. Verify hashed password
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # 3. Create the JWT Token
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# --- PROTECTED CREDENTIAL STORAGE ---
@app.post("/creds")
def store_credential(
        payload: models.SecretCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)  # The Lock
):
    # Envelope Encryption: Encrypt the value
    encrypted_data = crypto.vault.encrypt_secret(payload.value)

    new_secret = models.Secret(
        key_name=payload.key_name,
        encrypted_value=encrypted_data["ciphertext"],
        encrypted_data_key=encrypted_data["encrypted_key"],
        owner_id=current_user.id  # Link to this specific user
    )
    db.add(new_secret)
    db.commit()
    return {"message": f"Credential '{payload.key_name}' encrypted and saved."}


@app.get("/creds/{key_name}")
def get_credential(
        key_name: str,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    # Only find secrets belonging to THIS logged-in user
    secret = db.query(models.Secret).filter(
        models.Secret.key_name == key_name,
        models.Secret.owner_id == current_user.id
    ).first()

    if not secret:
        raise HTTPException(status_code=404, detail="Credential not found")

    # Decrypt using the unlocked Data Key
    decrypted_value = crypto.vault.decrypt_secret(
        secret.encrypted_value,
        secret.encrypted_data_key
    )
    return {"key": key_name, "value": decrypted_value}


@app.post("/token")
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    # 1. Authenticate the user
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Create the JWT token
    access_token = auth.create_access_token(data={"sub": user.username})

    # 3. Return the token in the specific format OAuth2 expects
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/secrets", status_code=status.HTTP_201_CREATED)
def create_secret(
    secret_data: models.SecretCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # This is the lock!
):
    # 1. Encrypt the secret using Envelope Encryption (AES-256-GCM)
    encryption_result = crypto.encrypt_secret(secret_data.value)

    # 2. Create the Database Record
    new_secret = models.Secret(
        key_name=secret_data.key_name,
        encrypted_value=encryption_result["ciphertext"],
        encrypted_data_key=encryption_result["encrypted_data_key"],
        owner_id=current_user.id  # Links this secret strictly to YOU
    )

    # 3. Save to the database
    db.add(new_secret)
    db.commit()

    return {"message": f"Secret '{secret_data.key_name}' saved and encrypted successfully."}

@app.get("/creds")
def list_credentials(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Fetch all secrets belonging to the logged-in user
    secrets = db.query(models.Secret).filter(models.Secret.owner_id == current_user.id).all()
    # We only return the key_names, NOT the values (for better security/performance)
    return [{"key_name": s.key_name} for s in secrets]