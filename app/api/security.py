from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from app.core.security import SECRET_KEY, ALGORITHM
from app.api.deps import get_db
from sqlalchemy.orm import Session
from app.models.all_models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except:
        raise HTTPException(401, "Invalid token")

    user = db.query(User).get(user_id)

    if not user:
        raise HTTPException(401, "User not found")

    return user
