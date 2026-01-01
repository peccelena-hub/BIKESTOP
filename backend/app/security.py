from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
import os
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.getenv("JWT_SECRET", "change_me")
JWT_ALG = os.getenv("JWT_ALG", "HS256")
JWT_EXPIRES_MINUTES = int(os.getenv("JWT_EXPIRES_MINUTES", "10080"))
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)
def create_access_token(sub: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=JWT_EXPIRES_MINUTES)
    payload = {"sub": sub, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return payload.get("sub")
    except JWTError as e:
        raise ValueError("Invalid token") from e
