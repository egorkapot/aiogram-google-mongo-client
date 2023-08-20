class InvalidRoleError(Exception):
    def __init__(self, role):
        self.role = role
        super().__init__(f"Invalid role {role}")