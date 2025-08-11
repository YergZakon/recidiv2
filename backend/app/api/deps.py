"""
Зависимости для FastAPI endpoints
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import verify_token
from app.models.user import User


# Database dependency
def get_db() -> Generator:
    """Получение сессии базы данных"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# Security dependencies
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Получение текущего аутентифицированного пользователя
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # В будущем здесь будет поиск пользователя в БД
    # user = get_user_by_username(db, username=username)
    # if user is None:
    #     raise credentials_exception
    # return user
    
    # Пока возвращаем заглушку
    return User(username=username, is_active=True)


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Проверка что пользователь активен
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Optional authentication (для публичных endpoints)
def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Опциональная аутентификация для публичных endpoints
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None