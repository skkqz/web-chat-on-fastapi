from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from database import Bace


class User(Bace):
    """
    Класс модели пользователя.
    """

    name: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
