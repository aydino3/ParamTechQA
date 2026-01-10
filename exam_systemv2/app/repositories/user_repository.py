from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User, UserRole


class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()
    
    def create(self, username: str, password_hash: str, role: UserRole, email: Optional[str] = None) -> User:
        user = User(
            username=username,
            password_hash=password_hash,
            role=role,
            email=email
        )
        self.db.add(user)
        self.db.flush()
        return user
    
    def update(self, user: User) -> User:
        self.db.flush()
        return user
    
    def list_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def list_by_role(self, role: UserRole):
        return self.db.query(User).filter(User.role == role).all()

