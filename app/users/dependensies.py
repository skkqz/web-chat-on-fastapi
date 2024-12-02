from datetime import datetime, timezone

from fastapi import Request, HTTPException, status, Depends
from jose import jwt, JWTError

from config import get_auth_data
from exceptions import TokenExpiredException, TokenNoFoundException, NoUserIdException, NoJwtException
from app.users.dao import UserDAO


def get_token(request: Request):
    """
    Извлекает JWT-токен из cookies запроса.

    :param request: Объект FastAPI-запроса.
    :return: Строка JWT-токена.
    :raises TokenNoFoundException: Если токен отсутствует в cookies.
    """

    token = request.cookies.get('user_access_token')

    if not token:
        raise TokenNoFoundException
    return token

async def get_current_user(token: str = Depends(get_token)):
    """
    Проверяет JWT-токен, извлекает идентификатор пользователя и возвращает объект пользователя.

    :param token: JWT-токен, извлеченный из cookies (зависимость от get_token).
    :return: Объект пользователя из базы данных.
    :raises NoJwtException: Если токен недействителен или некорректен.
    :raises TokenExpiredException: Если срок действия токена истек.
    :raises NoUserIdException: Если токен не содержит идентификатора пользователя.
    :raises HTTPException: Если пользователь с переданным ID не найден.
    """

    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=auth_data['algorithm'])
    except JWTError:
        raise NoJwtException

    expire: str = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)

    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise TokenExpiredException

    user_id: str = payload.get('sub')

    if not user_id:
        raise NoUserIdException

    user = await UserDAO.find_one_or_none_by_id(str(user_id))

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Пользователь не найден')
    return user
