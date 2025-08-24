class DynamicFloat:
    """A class that acts like an float but generates its value dynamically via a function."""

    def __init__(self, value_func):
        """
        Initialize with a function that returns an integer.

        Args:
            value_func: A callable that takes no arguments and returns an integer
        """
        if not callable(value_func):
            raise TypeError("value_func must be callable")
        self._value_func = value_func

    @property
    def value(self):
        """Get the current value by calling the function."""
        return self._value_func()

    # Conversion methods
    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __complex__(self):
        return complex(self.value)

    def __bool__(self):
        return bool(self.value)

    # String representation
    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"DynamicFloat({self.value})"

    def __format__(self, format_spec):
        return format(self.value, format_spec)

    # Arithmetic operations
    def __add__(self, other):
        return self.value + other

    def __radd__(self, other):
        return other + self.value

    def __sub__(self, other):
        return self.value - other

    def __rsub__(self, other):
        return other - self.value

    def __mul__(self, other):
        return self.value * other

    def __rmul__(self, other):
        return other * self.value

    def __truediv__(self, other):
        return self.value / other

    def __rtruediv__(self, other):
        return other / self.value

    def __floordiv__(self, other):
        return self.value // other

    def __rfloordiv__(self, other):
        return other // self.value

    def __mod__(self, other):
        return self.value % other

    def __rmod__(self, other):
        return other % self.value

    def __divmod__(self, other):
        return divmod(self.value, other)

    def __rdivmod__(self, other):
        return divmod(other, self.value)

    def __pow__(self, other, modulo=None):
        return pow(self.value, other, modulo)

    def __rpow__(self, other):
        return pow(other, self.value)

    # Bitwise operations
    def __lshift__(self, other):
        return self.value << other

    def __rlshift__(self, other):
        return other << self.value

    def __rshift__(self, other):
        return self.value >> other

    def __rrshift__(self, other):
        return other >> self.value

    def __and__(self, other):
        return self.value & other

    def __rand__(self, other):
        return other & self.value

    def __xor__(self, other):
        return self.value ^ other

    def __rxor__(self, other):
        return other ^ self.value

    def __or__(self, other):
        return self.value | other

    def __ror__(self, other):
        return other | self.value

    # Unary operations
    def __neg__(self):
        return -self.value

    def __pos__(self):
        return +self.value

    def __abs__(self):
        return abs(self.value)

    def __invert__(self):
        return ~self.value

    # Comparison operations
    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __lt__(self, other):
        return self.value < other

    def __le__(self, other):
        return self.value <= other

    def __gt__(self, other):
        return self.value > other

    def __ge__(self, other):
        return self.value >= other

    # Additional integer methods
    def __index__(self):
        """Support for bin(), hex(), oct() and use as list index."""
        return self.value

    def __hash__(self):
        """Make the object hashable."""
        return hash(self.value)

    def __round__(self, ndigits=None):
        return round(self.value, ndigits)

    def __trunc__(self):
        return self.value

    def __floor__(self):
        return self.value

    def __ceil__(self):
        return self.value


