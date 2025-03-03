import inspect
from pathlib import Path


class OXception(Exception):
    def __init__(self, message):
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
        return {
            "message": self.message,
            "file_name": self.file_name,
            "line_nr": self.line_nr,
            "method_name": self.method_name,
            "params": self.params
        }

    def __str__(self):
        return f"OXception: {self.message} in {self.file_name}:{self.line_nr} ({self.method_name} with locals: {self.params})"

    def __repr__(self):
        return self.__str__()
