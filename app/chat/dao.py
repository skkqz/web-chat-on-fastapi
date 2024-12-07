import uuid

from sqlalchemy import select, and_, or_

from database import async_session_maker
from  app.dao.base import BaseDAO
from app.chat.models import Message


class MessageDAO(BaseDAO):
    """
    Класс для запросов к бд сообщения.
    """

    model = Message

    @classmethod
    async def get_messages_between_users(cls, user_id_first: uuid, user_id_second: uuid):
        """
        Асинхронно находит и возвращает все сообщения между двумя пользователями.

        @:param user_id_first: ID первого пользователя.
        @:param user_id_second: ID второго пользователя.
        @:return: Список сообщений между двумя пользователями.
        """

        async with async_session_maker() as session:
            query = select(cls.model).filter(
                or_(
                    and_(cls.model.sender_id == user_id_first, cls.model.recipient_id == user_id_second),
                    and_(cls.model.sender_id == user_id_second, cls.model.recipient_id == user_id_first)
                )
            ).order_by(cls.model.id)
            result = await session.execute(query)
            return result.scalars().all()
