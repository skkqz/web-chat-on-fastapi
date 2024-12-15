import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Dict
from app.chat.dao import MessageDAO
from app.chat.schemas import MessageReadS, MessageCreateS
from app.users.dao import UserDAO
from app.users.dependencies import get_current_user
from app.users.models import User
import asyncio


# Создаем экземпляр маршрутизатора с префиксом /chat и тегом "Chat"
router = APIRouter(prefix='/chat', tags=['Chat'])
# Настройка шаблонов Jinja2
templates = Jinja2Templates(directory='templates')


# Страница чата
@router.get("/", response_class=HTMLResponse, summary="Chat Page")
async def get_chat_page(request: Request, user_data: User = Depends(get_current_user)):
    # Получаем всех пользователей из базы данных
    users_all = await UserDAO.find_all()
    # Возвращаем HTML-страницу с использованием шаблона Jinja2
    return templates.TemplateResponse("chat.html",
                                      {"request": request, "user": user_data, 'users_all': users_all})


# Активные WebSocket-подключения: {user_id: websocket}
active_connections: Dict[uuid.UUID, WebSocket] = {}


# Функция для отправки сообщения пользователю, если он подключен
async def notify_user(user_id: uuid.UUID, message: dict):
    """Отправить сообщение пользователю, если он подключен."""
    if user_id in active_connections:
        websocket = active_connections[user_id]
        # Отправляем сообщение в формате JSON
        await websocket.send_json(message)


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: uuid.UUID):
    # Принимаем соединение
    await websocket.accept()

    # Устанавливаем статус "онлайн"
    await UserDAO.update_user_status(user_id=user_id, status=True)
    active_connections[user_id] = websocket

    try:
        while True:
            # Поддерживаем соединение
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Устанавливаем статус "оффлайн" при разрыве соединения
        await UserDAO.update_user_status(user_id=user_id, status=False)
        active_connections.pop(user_id, None)


# # WebSocket эндпоинт для соединений
# @router.websocket("/ws/{user_id}")
# async def websocket_endpoint(websocket: WebSocket, user_id: uuid.UUID):
#     # Принимаем WebSocket-соединение
#     await websocket.accept()
#     # Сохраняем активное соединение для пользователя
#     active_connections[user_id] = websocket
#     # await UserDAO.update_user_status(user_id=user_id, status=True)
#     try:
#         while True:
#             # Просто поддерживаем соединение активным (1 секунда паузы)
#             await asyncio.sleep(1)
#     except WebSocketDisconnect:
#         # Удаляем пользователя из активных соединений при отключении
#         # await UserDAO.update_user_status(user_id=user_id, status=False)
#         active_connections.pop(user_id, None)


# Получение сообщений между двумя пользователями
@router.get("/messages/{user_id}", response_model=List[MessageReadS])
async def get_messages(user_id: uuid.UUID, current_user: User = Depends(get_current_user)):
    # Возвращаем список сообщений между текущим пользователем и другим пользователем
    messages = await MessageDAO.get_messages_between_users(user_id_first=user_id, user_id_second=current_user.id) or []
    messages_sorted = sorted(messages, key=lambda msg: msg.created_at)
    return messages_sorted


@router.post('/messages', response_model=MessageCreateS)
async def send_message(message: MessageCreateS, current_user: User = Depends(get_current_user)):
    """
    Отправить сообщение пользователю.

    :param message: Данные сообщения.
    :param current_user: Текущий пользователь.
    :return: Результат отправки сообщения.
    """

    await MessageDAO.add(
        sender_id=current_user.id,
        content=message.content,
        recipient_id=message.recipient_id
    )

    message_data = {
        'sender_id': str(current_user.id),
        'recipient_id': str(message.recipient_id),
        'content': message.content
    }

    await notify_user(message.recipient_id, message_data)
    await notify_user(current_user.id, message_data)

    return {
        'recipient_id': message.recipient_id,
        'content': message.content,
        'status': 'ok',
        'message': 'Сообщение сохранено'
    }
