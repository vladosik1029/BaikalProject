from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import Session 
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")
    
def create_admin_user(db: Session):
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password="hashed_admin_password",  # Замените на реальный хеш
        role="admin"
    )
    db.add(admin)
    db.commit()
    return admin