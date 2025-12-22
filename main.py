# main.py (Phase 1: Registration & Core Setup)
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import our project modules
import models, auth, database
from database import engine, get_db

# This line creates the actual .db file and tables when the app starts
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="fz-creds-manager")


@app.get("/")
def health_check():
    return {"status": "online", "project": "fz-creds-manager"}


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