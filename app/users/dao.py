import uuid

from sqlalchemy import select

from app.dao.base import BaseDAO
from app.users.models import User
from database import async_session_maker


class UserDAO(BaseDAO):
    """
    Класс для запросов к бд пользователя.
    """

    model = User

    @classmethod
    async def update_user_status(cls, user_id: uuid.UUID, status: bool) -> User:

        async with async_session_maker() as session:
            async with session.begin():
                user = await session.get(User, user_id)
                if user:
                    user.online_status = status
                    await session.commit()
                    return user
                # query = select(cls.model).filter(cls.model.id == user_id)
                # result = await session.execute(query)
                # db_user = result.scalars().first()
                # db_user.status = status
                # await session.commit()
                # await session.refresh(db_user)
                # return db_user

    @classmethod
    async def find_all_online_users(cls):
        async with async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.online_status == True)
            )
            return result.scalars().all()

    @classmethod
    async def list_users(cls, user_id: uuid.UUID, **filter_by):

        async with async_session_maker() as session:
            query = select(cls.model).filter(cls.model.id != user_id)
            result = await session.execute(query)
            return result.scalars().all()
