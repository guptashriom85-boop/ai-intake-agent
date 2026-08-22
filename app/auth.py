from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException, Request
from .config import settings

ALG = "HS256"

def create_token(subject: str) -> str:
    payload = {"sub": subject, "exp": datetime.now(timezone.utc) + timedelta(hours=12)}
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALG)

def require_admin(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = jwt.decode(auth.removeprefix("Bearer ").strip(), settings.jwt_secret, algorithms=[ALG])
        if payload.get("sub") != settings.admin_email:
            raise HTTPException(status_code=403, detail="Admin access required")
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc
