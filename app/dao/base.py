import logging
import uuid
from shutil import which

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete, func

from database import async_session_maker


class BaseDAO:
    model = None

    @classmethod
    async def find_one_or_none_by_id(cls, data_id: int):
        """
        Найти один экземпляр модели по ID.

        :param data_id: Идентификатор записи.
        :return: Экземпляр модели или None.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=data_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        """
        Найти один экземпляр модели по фильтрам.

        :param filter_by: Фильтры для поиска.
        :return: Экземпляр модели или None.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, **filter_by):
        """
        Найти все экземпляры модели по фильтрам.

        :param filter_by: Фильтры для поиска.
        :return: Список экземпляров модели.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def add(cls, **values):
        """
        Создать новый экземпляр модели.

        :param values: Данные для создания.
        :return: Созданный экземпляр модели.
        """

        values['id'] = values.get('id', uuid.uuid4())
        async with async_session_maker() as session:
            async with session.begin():
                new_instance = cls.model(**values)
                session.add(new_instance)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return new_instance

    @classmethod
    async def add_many(cls, instances: list[dict]):
        """
        Создать несколько экземпляров модели.

        :param instances: Список данных для создания.
        :return: Список созданных экземпляров модели.
        """
        async with async_session_maker() as session:
            async with session.begin():
                new_instances = [cls.model(**values) for values in instances]
                session.add_all(new_instances)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return new_instances

    @classmethod
    async def update(cls, filter_by, **values):
        """
        Обновить экземпляры модели по фильтрам.

        :param filter_by: Фильтры для поиска.
        :param values: Данные для обновления.
        :return: Количество обновленных записей.
        """
        async with async_session_maker() as session:
            async with session.begin():
                query = (
                    sqlalchemy_update(cls.model)
                    .where(*[getattr(cls.model, k) == v for k, v in filter_by.items()])
                    .values(**values)
                    .execution_options(synchronize_session="fetch")
                )
                result = await session.execute(query)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return result.rowcount

    @classmethod
    async def delete(cls, delete_all: bool = False, **filter_by):
        """
        Удалить экземпляры модели по фильтрам.

        :param delete_all: Если True, удаляются все записи.
        :param filter_by: Фильтры для удаления.
        :return: Количество удаленных записей.
        """
        if delete_all is False and not filter_by:
            raise ValueError("Необходимо указать фильтры для удаления.")

        async with async_session_maker() as session:
            async with session.begin():
                query = sqlalchemy_delete(cls.model).filter_by(**filter_by)
                result = await session.execute(query)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return result.rowcount
