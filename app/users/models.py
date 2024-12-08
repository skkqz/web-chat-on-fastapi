from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class User(Base):
    """
    Класс модели пользователя.
    """

    name: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    online_status: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
