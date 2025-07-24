# THIRDPARTY
from fastapi import HTTPException, status


class BaseAppException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "User already exists"


class IncorrectUserEmailOrPasswordException(BaseAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Incorrect email or password"


class TokenExpiredException(BaseAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token expired"


class TokenAbsentException(BaseAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token absent"


class IncorrectTokenFormatException(BaseAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Incorrect token format"


class NotUserException(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Not user"


class UserIsNotPresentException(BaseAppException):
    status_code = status.HTTP_401_UNAUTHORIZED


class NotEnoughRightsException(BaseAppException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Not enough rights"


class NotProductsException(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Not products"


class NotAddressException(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Not address"


class AddressAlreadyExistsException(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Address already exists"


class NotCartException(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Not cart"


class NotTrueProductsQuantityException(BaseAppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Not true products quantity"


class NotCartsItemException(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Not cart's item"


class CartsItemsAlreadyExistsException(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Cart's items already exists"


class NotTrueTimeException(BaseAppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Not true time"


class YouCanNotChooseThisPaymentException(BaseAppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "You can't choose this payment"


class YouCanNotAddNewOrderException(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "You can't add new order"


class YouCanNotOrderByThisId(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "You can't order by this id"


class YouDoNotHaveOrdersException(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "You don't have any orders"


class ProductAlreadyExistsException(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Product already exists"


class NotOrdersException(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Not orders"


class YouCanNotPayOrderException(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "You can't pay this order"


class YouDoNotHaveCartItemsException(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "You don't have cart items"
