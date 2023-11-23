class SecurityException(Exception):

    """Main class for security errors"""


class TaskError(SecurityException):

    """Main class for task - based exceptions"""


class TaskPermissionError(TaskError):

    """Task cannot be accessed due the permission error"""


class TaskTimeError(TaskError):

    """Task cannot be accessed due the timing error"""


class AuthError(SecurityException):

    """Main class for exceptions associated with auth problems"""


class AuthRoleError(AuthError):

    """Auth cannot be proceeded: invalid user role"""


class PasswordError(AuthError):

    """Auth cannot be proceeded: invalid password"""


class NoSuchUserError(AuthError):

    """Auth cannot be proceeded: no such user"""


class DeletedUserAuthError(AuthError):

    """Auth cannot be proceeded: user accounе is marked for deletion"""
