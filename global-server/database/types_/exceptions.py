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


class VerificationError(Exception):

    """Base class for errors associated with personal data"""


class PersonalDataValidationError(VerificationError):

    """Personal data has not passed primary validation"""


class EmailValidationError(PersonalDataValidationError):

    """Email has not passed primary validation"""


class PhoneValidationError(PersonalDataValidationError):

    """Phone has not passed primary validation"""


class TelegramValidationError(PersonalDataValidationError):

    """Telegram has not passed primary validation"""


class ActorError(SecurityException):

    """Main class for security errors connected with Actor model"""


class ActorExistsError(ActorError):
    pass


class ActorNotExistsError(ActorError):
    pass


class ActorCreationError(ActorError):
    pass
