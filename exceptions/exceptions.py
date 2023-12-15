class InvalidRoleError(Exception):
    def __init__(self, role):
        self.role = role
        super().__init__(f"Invalid role {role}")


class MissingEnvironmentVariableException(Exception):
    pass


class _BaseException(Exception):
    def __init__(self, message: str):
        self.message = message
