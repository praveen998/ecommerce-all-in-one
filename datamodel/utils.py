import os
import bcrypt
from dotenv import load_dotenv
import asyncio
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


load_dotenv()


class Hashing:

    @staticmethod
    async def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = await asyncio.to_thread(bcrypt.gensalt)  # Generate salt
        hashed = await asyncio.to_thread( bcrypt.hashpw,password.encode(), salt)  # Hash password
        return hashed.decode()  # Convert bytes to string
    
    @staticmethod
    async def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against a stored hash."""
        return await asyncio.to_thread(bcrypt.checkpw,password.encode(),hashed_password.encode())

    
#print(Hashing.hash_password("nibhas1234"))
#-------------------------------------------------------------------------------------------------------


class JWTHandler:
    def __init__(self, secret_key: str, algorithm: str, expire_minutes: int):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=self.expire_minutes))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)


    def verify_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def jwt_header_extraction(jwt_handler:JWTHandler):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token not provided or invalid format")
        token = token.split(" ")[1]
        payload = jwt_handler.verify_token(token)
        return {"message": "Access granted", "user": payload}


