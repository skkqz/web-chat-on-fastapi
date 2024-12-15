import uuid
from typing import List

from fastapi import APIRouter, Response, Depends
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.chat.router import active_connections
from app.users.dependencies import get_current_user
from app.users.models import User
from exceptions import UserAlreadyExistsException, IncorrectEmailOrPasswordException, PasswordMismatchException
from app.users.auth import get_password_hash, authenticate_user, create_access_token
from app.users.dao import UserDAO
from app.users.schemas import SUserRegister, SUserAuth, SUserRead


router = APIRouter(prefix='/auth', tags=['Auth'])
templates = Jinja2Templates(directory='templates')


@router.get("/", response_class=HTMLResponse, summary="Страница авторизации")
async def get_auth_page(request: Request):
    """
    Возвращает страницу авторизации.
    """

    return templates.TemplateResponse("auth.html", {"request": request})


@router.post('/register')
async def register_user(user_data: SUserRegister) -> dict:
    """
    Регистрация нового пользователя.

    Эта функция позволяет пользователю зарегистрироваться, проверяя наличие пользователя
    с данным email в базе данных и соответствие введенных паролей.

    :param user_data: Данные пользователя для регистрации (имя, email, пароль, проверка пароля).
    :return: Словарь с сообщением об успешной регистрации.
    :raises UserAlreadyExistsException: Если пользователь с указанным email уже существует.
    :raises PasswordMismatchException: Если пароли не совпадают.
    """

    user = await UserDAO.find_one_or_none(email=user_data.email)

    if user:
        raise UserAlreadyExistsException

    if user_data.password != user_data.password_check:
        raise PasswordMismatchException

    hashed_password = get_password_hash(user_data.password)
    await UserDAO.add(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password
    )

    return {'message': 'Вы успешно зарегистрированы'}


@router.post('/login/')
async def auth_user(response: Response, user_data: SUserAuth) -> dict:
    """
    Авторизация пользователя.

    Эта функция проверяет учетные данные пользователя и генерирует JWT-токен для доступа к системе.
    Токен сохраняется в cookie.

    :param response: Объект ответа, в который записывается JWT-токен в cookie.
    :param user_data: Данные пользователя для авторизации (email, пароль).
    :return: Словарь с подтверждением авторизации и токенами.
    :raises IncorrectEmailOrPasswordException: Если email или пароль неверны.
    """

    check_ = await authenticate_user(email=user_data.email, password=user_data.password)

    if check_ is None:
        raise IncorrectEmailOrPasswordException

    access_token = create_access_token({'sub': str(check_.id)})
    response.set_cookie(key='user_access_token', value=access_token, httponly=True)

    return {'ok': True, 'access_token': access_token, 'refresh_token': None, 'message': 'Авторизация успешна!'}


@router.post("/logout/")
async def logout_user(response: Response) -> dict:
    """
    Выход пользователя из системы.

    Удаляет JWT-токен пользователя из cookie, тем самым завершает текущую сессию.

    :param response: Объект ответа, из которого удаляется cookie с токеном.
    :return: Словарь с сообщением об успешном выходе.
    """

    response.delete_cookie(key='users_access_token')
    return {'message': 'Пользователь успешно вышел из системы'}


@router.get('/users', response_model=List[SUserRead])
async def get_users(current_user: User = Depends(get_current_user)):
    """
    Получение списка пользователей.

    :return: Список словарей с ID и именем пользователей.
    """

    # users_all = await UserDAO.find_all()
    users_all = await UserDAO.list_users(user_id=current_user.id)
    return [
        {'id': user.id, 'name': user.name, 'email': user.email, 'online_status': user.online_status }
        for user in users_all
    ]


@router.get('/me', response_model=SUserRead, summary='Получить информацию о текущем пользователе')
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Получить информацию о текущем авторизованном пользователе.

    Этот эндпоинт извлекает данные о пользователе, используя токен доступа,
    и возвращает информацию о текущем пользователе.

    :param current_user: Текущий пользователь, извлеченный из токена.
    :return: Информация о текущем пользователе.
    """

    return current_user


@router.get("/users/status", response_model=List[SUserRead])
async def get_users_status():
    """
    Возвращает всех пользователей с их статусом онлайн/оффлайн.
    """
    users = await UserDAO.find_all()
    return [{"id": user.id, "name": user.name, "online_status": user.online_status} for user in users]
