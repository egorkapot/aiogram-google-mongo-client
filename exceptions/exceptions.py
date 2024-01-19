class InvalidRoleError(Exception):
    def __init__(self, role):
        self.role = role
        super().__init__(f"Invalid role {role}")


class MissingEnvironmentVariableException(Exception):
    pass


class _BaseException(Exception):
    CODE = "BASE_ERROR"

    def __init__(self, message: str):
        self.message = message

    def get_response(self):
        return {'message': self.message, "code": self.CODE}
