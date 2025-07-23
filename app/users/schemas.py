# THIRDPARTY
from pydantic import BaseModel


class SUsers(BaseModel):
    id: int
    user_chat_id: int
    is_admin: int
