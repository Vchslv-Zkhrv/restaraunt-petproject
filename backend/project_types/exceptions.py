
class DatabaseError(Exception):

    """Main class for database - based exceptions"""


class TaskError(DatabaseError):

    """Main class for task - based exceptions"""


class TaskPermissionError(TaskError):

    """Task cannot be accessed due the permission error"""

