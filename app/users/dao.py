# FIRSTPARTY
from app.dao.base import BaseDao
from app.users.models import Users


class UserDAO(BaseDao):
    model = Users
