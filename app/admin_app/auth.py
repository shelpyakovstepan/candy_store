# THIRDPARTY
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

# FIRSTPARTY
from app.config import get_password_hash, pwd_context
from app.users.auth import create_access_token
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(user_id: int, password: str):
    auth_user = await UsersDAO.find_by_id(user_id)
    if not auth_user:
        return None
    if not verify_password(password, get_password_hash()):
        return None
    return auth_user


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        user_id, password = form["username"], form["password"]

        user = await authenticate_user(int(user_id), password)  # pyright: ignore [reportArgumentType]
        if user:
            access_token = create_access_token({"sub": str(user.id)})
            request.session.update({"token": access_token})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False
        user = await get_current_user(token)

        if not user:
            return False

        return True


authentication_backend = AdminAuth(secret_key="...")
