import uuid

from pydantic import BaseModel, Field



class MessageReadS(BaseModel):
    """
    Схема для чтения сообщения.
    """

    id: uuid.UUID = Field(..., description='Уникальный идентификатор  сообщения')
    sender_id: uuid.UUID = Field(..., description='ID отправителя сообщения')
    recipient_id: uuid.UUID = Field(..., description='ID получателя сообщения')
    content: str = Field(..., description='Содержимое сообщения')


class MessageCreateS(BaseModel):
    """
    Схема для записи сообщения.
    """

    recipient_id: uuid.UUID = Field(..., description="ID получателя сообщения")
    content: str = Field(..., description="Содержимое сообщения")