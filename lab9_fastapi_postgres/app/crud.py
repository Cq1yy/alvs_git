from sqlalchemy.orm import Session

from .models import User
from .schemas import UserCreate


def create_user(db: Session, user: UserCreate) -> User:
    obj = User(username=user.username, email=user.email)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.id).all()
