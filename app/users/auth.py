from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext  # Настройка и хеширование паролей
from pydantic import EmailStr
from jose import jwt

from config import get_auth_data
from app.users.dao import UserDAO


def create_access_token(data: dict) -> str:
    """
    Создает JWT‑токен с заданными данными и сроком действия.

    Токен включает данные, переданные в параметре `data`,
    а также добавляет время истечения действия токена (`exp`).
    Данные кодируются с использованием секретного ключа и алгоритма шифрования.

    :param data: Словарь с данными для включения в токен.
    :return: Строка, представляющая закодированный JWT‑токен.
    """

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({'exp': expire})
    auth_data = get_auth_data()
    encode_jwt = jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])

    return encode_jwt


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_password_hash(password: str) -> str:
    """
    Хэширует переданный пароль с использованием алгоритма bcrypt.

    :param password: Строка пароля, которую нужно захэшировать.
    :return: Строка хэша пароля.
    """

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие введенного пароля и хэша.

    :param plain_password: Обычный пароль (введенный пользователем).
    :param hashed_password: Захэшированный пароль, сохраненный в базе данных.
    :return: True, если пароли совпадают, иначе False.
    """

    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(email: EmailStr, password: str):
    """
    Проверяет подлинность пользователя по email и паролю.

    :param email: Email пользователя.
    :param password: Пароль пользователя.
    :return: Объект пользователя, если email и пароль верны, иначе None.
    """

    user = await UserDAO.find_one_or_none(email=email)

    if not user or verify_password(plain_password=password, hashed_password=user.hashed_password) is False:
        return None
    return user
