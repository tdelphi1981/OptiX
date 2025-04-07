import inspect
from pathlib import Path


class OXception(Exception):
    """Custom exception class for the OptiX library.

    This exception automatically captures detailed information about where
    the exception occurred, including the file name, line number, method name,
    and local variables at the time of the exception.

    Attributes:
        message (str): The error message.
        line_nr (int): The line number where the exception occurred.
        file_name (str): The relative path of the file where the exception occurred.
        method_name (str): The name of the method where the exception occurred.
        params (dict): The local variables at the time of the exception.

    Examples:
        >>> try:
        ...     raise OXception("Something went wrong")
        ... except OXception as e:
        ...     print(e.message)
        ...     print(e.file_name)
        ...     print(e.line_nr)
        Something went wrong
        src/example.py
        42
    """
    def __init__(self, message):
        """Initialize the exception with the given message and capture context information.

        Args:
            message (str): The error message.
        """
        self.message = message
        frm = inspect.currentframe()
        self.line_nr = frm.f_back.f_lineno
        current_path = Path(__file__).parent.parent.parent.absolute()
        error_file_path = Path(frm.f_back.f_code.co_filename)
        relative_path = error_file_path.relative_to(current_path)
        self.file_name = str(relative_path)
        self.method_name = frm.f_back.f_code.co_name
        self.params = frm.f_back.f_locals
        super().__init__(self.message)

    def to_json(self):
        """Convert the exception to a JSON-serializable dictionary.

        This is useful for logging and error reporting.

        Returns:
            dict: A dictionary containing the exception details.
        """
        return {
            "message": self.message,
            "file_name": self.file_name,
            "line_nr": self.line_nr,
            "method_name": self.method_name,
            "params": self.params
        }

    def __str__(self):
        """Return a string representation of the exception.

        Returns:
            str: A detailed string representation including the message, file name,
                line number, method name, and local variables.
        """
        return f"OXception: {self.message} in {self.file_name}:{self.line_nr} ({self.method_name} with locals: {self.params})"

    def __repr__(self):
        """Return a string representation of the exception for debugging.

        Returns:
            str: The same string as __str__.
        """
        return self.__str__()
