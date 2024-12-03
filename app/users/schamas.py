from pydantic import BaseModel, EmailStr, Field


class SUserRegister(BaseModel):
    """
    Схема для регистрации пользователя.
    """

    email: EmailStr = Field(..., description='Электронная почта')
    password: str = Field(..., min_length=3, max_length=10, description='Пароль от 3 до 10 символов')
    password_check: str = Field(..., min_length=3, max_length=10, description='Пароль от 3 до 10 символов')
    name: str = Field(..., min_length=3, max_length=50, description='Имя')


class SUserAuth(BaseModel):
    """
    Схема для авторизации пользователя.
    """

    email: EmailStr = Field(..., description='Электронная почта')
    password: str = Field(..., min_length=3, max_length=10, description='Пароль от 3 до 10 символов')