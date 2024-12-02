from app.dao.base import BaseDAO
from app.users.models import User


class UserDAO(BaseDAO):
    """
    Класс для запросов к бд пользователя.
    """

    model = User
    