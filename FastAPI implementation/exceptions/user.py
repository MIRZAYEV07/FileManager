from fastapi.exceptions import HTTPException


class UserNotFoundException(HTTPException):
    detail = "User not found"

    def __init__(self):
        super().__init__(status_code=404, detail=self.detail)


class UserWithUsernameAlreadyExistsException(HTTPException):
    detail = "User with username already exists"

    def __init__(self, username):
        super().__init__(status_code=409, detail=self.detail.format(username))


class UserWithEmailAlreadyExistsException(HTTPException):
    detail = "User with email already exists"

    def __init__(self, email):
        super().__init__(status_code=403, detail=self.detail.format(email))


class UserPermissionException(HTTPException):
    detail = "You do not have permission to update this object."

    def __init__(self):
        super().__init__(status_code=403, detail=self.detail)
