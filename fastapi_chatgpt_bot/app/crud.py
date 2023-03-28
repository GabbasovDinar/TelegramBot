from sqlalchemy.orm import Session

from models import Message, User


def create_user(db: Session, telegram_id: str, password: str) -> User:
    new_user = User(telegram_id=telegram_id)
    new_user.set_password(password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user_by_telegram_id(db: Session, telegram_id: str) -> User:
    return db.query(User).filter(User.telegram_id == telegram_id).first()


def check_user_password(user: User, password: str) -> bool:
    if user.check_password(password):
        user.active = True
    else:
        user.active = False
    return user.active


def user_exists(db: Session, telegram_id: str):
    return db.query(User).filter(User.telegram_id == telegram_id).first() is not None


def get_users(db: Session):
    return db.query(User).all()


def add_message(db: Session, user_id: str, text: str, is_bot: bool) -> Message:
    message = Message(user_id=user_id, text=text, is_bot=is_bot)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

# TODO: add update password method
# TODO: send message to all users from bot
