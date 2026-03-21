# tests/conftest.py
import pytest
from src.binary_number import BinaryNumber
from src.binary_float import BinaryFloat
from src.binary_excess3 import BCDExcess3


@pytest.fixture
def sample_binary_numbers():
    """Фикстура с набором двоичных чисел для тестов"""
    return {
        "pos": BinaryNumber(5, "straight"),
        "neg": BinaryNumber(-5, "additional"),
        "zero": BinaryNumber(0, "straight"),
        "max_pos": BinaryNumber(2147483647, "straight"),
        "min_neg": BinaryNumber(-2147483648, "additional"),
    }


@pytest.fixture
def sample_float_numbers():
    """Фикстура с набором чисел с плавающей точкой"""
    return {
        "pos": BinaryFloat(5.75),
        "neg": BinaryFloat(-5.75),
        "zero": BinaryFloat(0.0),
        "small": BinaryFloat(1e-10),
        "large": BinaryFloat(1e10),
    }


@pytest.fixture
def sample_bcd_numbers():
    """Фикстура с набором BCD чисел"""
    return {
        "simple": BCDExcess3(123),
        "zero": BCDExcess3(0),
        "max": BCDExcess3(99999999),
        "with_zeros": BCDExcess3(1001),
    }
