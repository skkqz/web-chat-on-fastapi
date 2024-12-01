import uuid
from shutil import which

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete, func

from database import async_session_maker


class BaseDAO:
    """
    Базовый класс для запросов к бд.
    """

    model = None

    @classmethod
    async def find_one_or_none_by_id(cls, data_id: uuid):
        """
        Асинхронно находит и возвращает один экземпляр модели по указанным критериям или None.

        @:param data_id: Критерии фильтрации в виде идентификатора записи.
        @:return: Экземпляр модели или None, если ничего не найдено.
        """

        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=data_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        """
        Асинхронно находит и возвращает один экземпляр модели по указанным критериям или None.

        @param filter_by: Критерии фильтрации в виде именованных параметров.
        @return: Экземпляр модели или None, если ничего не найдено.
        """

        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, **filter_by):
        """
        Асинхронно находит и возвращает все экземпляры модели, удовлетворяющие указанным критериям.

        @:param filter_by: Критерии фильтрации в виде именованных параметров.
        @:return: Список экземпляров модели.
        """

        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def add(cls, **values):
        """
        Асинхронно создает новый экземпляр модели с указанными значениями.

        @:param: values: Именованные параметры для создания нового экземпляра модели.
        @:return: Созданный экземпляр модели.
        """

        async with async_session_maker() as session:
            async with session.begin():
                new_instance = cls.model(**values)
                session.add(new_instance)

                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    return e
                return new_instance
