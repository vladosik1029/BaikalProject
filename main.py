from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
import crud, schemas, models, auth
from database import SessionLocal, engine, get_db
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_admin,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Эндпоинт для аутентификации и получения токена
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Административные эндпоинты
@app.get("/admin/users/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: schemas.User = Depends(get_current_admin)
):
    """
    Получить список пользователей (только для администраторов)
    """
    return crud.get_users(db, skip=skip, limit=limit)

@app.post("/admin/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_admin: schemas.User = Depends(get_current_admin)
):
    """
    Создать нового пользователя (только для администраторов)
    """
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    return crud.create_user(db, user=user)

@app.put("/admin/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_admin: schemas.User = Depends(get_current_admin)
):
    """
    Обновить данные пользователя (только для администраторов)
    """
    db_user = crud.update_user(db, user_id=user_id, user_data=user)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user

@app.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: schemas.User = Depends(get_current_admin)
):
    """
    Удалить пользователя (только для администраторов)
    """
    db_user = crud.delete_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return None

# Публичные эндпоинты
@app.get("/public/", tags=["Public"])
def public_route():
    """
    Публичный эндпоинт, доступен без аутентификации
    """
    return {"message": "This is public data"}

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Получить данные текущего пользователя
    """
    return current_user