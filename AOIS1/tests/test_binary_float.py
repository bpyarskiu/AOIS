# tests/test_binary_float.py
import pytest
import math
from src.binary_float import BinaryFloat


class TestBinaryFloatCreation:
    """Тесты создания объектов BinaryFloat"""

    @pytest.mark.parametrize(
        "value,expected_sign",
        [
            (5.75, "0"),
            (-5.75, "1"),
            (0.0, "0"),
        ],
    )
    def test_creation_from_float(self, value, expected_sign):
        """Создание из float"""
        num = BinaryFloat(value)
        assert num.value == value
        assert num.binary[0] == expected_sign
        assert len(num.binary) == 32

    def test_creation_from_binary_string(self):
        """Создание из двоичной строки"""
        # 5.75 в IEEE-754: 0 10000001 01110000000000000000000
        binary = "01000000101110000000000000000000"
        num = BinaryFloat(binary)
        assert abs(num.value - 5.75) < 1e-6

    def test_special_values(self):
        """Специальные значения"""
        # Ноль
        zero = BinaryFloat(0.0)
        assert zero.binary == "0" * 32

        # Бесконечность (упрощенно)
        # В полной реализации должны быть тесты для inf, nan

    def test_invalid_type(self):
        """Неверный тип входных данных"""
        with pytest.raises(TypeError):
            BinaryFloat([1, 2, 3])  # список не поддерживается


class TestBinaryFloatConversion:
    """Тесты преобразований IEEE-754"""

    @pytest.mark.parametrize(
        "value",
        [
            0.0,
            1.0,
            -1.0,
            2.0,
            0.5,
            5.75,
            -5.75,
            123.456,
            0.1,  # 0.1 не представляется точно
        ],
    )
    def test_roundtrip_conversion(self, value):
        """Проверка обратного преобразования: float -> bits -> float"""
        num = BinaryFloat(value)
        restored = num.ieee754_to_float(num.binary)

        # Сравниваем с учетом погрешности
        if value == 0.0:
            assert restored == 0.0
        else:
            rel_error = abs((restored - value) / value)
            assert rel_error < 1e-7

    def test_binary_add_static(self):
        """Тест статического метода сложения двоичных строк"""
        result = BinaryFloat._binary_add("1010", "0101")
        assert result == "1111"

        result = BinaryFloat._binary_add("1111", "0001")
        assert result == "10000"  # с переносом

    def test_binary_subtract_static(self):
        """Тест статического метода вычитания"""
        result = BinaryFloat._binary_subtract("1010", "0101")
        # 10 - 5 = 5
        assert int(result, 2) == 5


class TestBinaryFloatArithmetic:
    """Тесты арифметических операций"""

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (5.75, 2.25, 8.0),
            (5.75, -2.25, 3.5),
            (-5.75, 2.25, -3.5),
            (-5.75, -2.25, -8.0),
            (0.0, 5.75, 5.75),
            (5.75, 0.0, 5.75),
        ],
    )
    def test_addition(self, a, b, expected):
        """Тест сложения"""
        x = BinaryFloat(a)
        y = BinaryFloat(b)
        result = x + y
        assert abs(result.value - expected) < 1e-6

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (5.75, 2.25, 3.5),
            (5.75, -2.25, 8.0),
            (-5.75, 2.25, -8.0),
            (-5.75, -2.25, -3.5),
            (5.75, 5.75, 0.0),
        ],
    )
    def test_subtraction(self, a, b, expected):
        """Тест вычитания"""
        x = BinaryFloat(a)
        y = BinaryFloat(b)
        result = x - y
        print(result.value, "gfhuofhwoimfweji")
        assert abs(result.value - expected) < 1e-6

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (5.75, 2.25, 12.9375),
            (5.75, -2.25, -12.9375),
            (-5.75, 2.25, -12.9375),
            (-5.75, -2.25, 12.9375),
            (0.0, 5.75, 0.0),
            (2.0, 0.5, 1.0),
        ],
    )
    def test_multiplication(self, a, b, expected):
        """Тест умножения"""
        x = BinaryFloat(a)
        y = BinaryFloat(b)
        result = x * y
        assert abs(result.value - expected) < 1e-6

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (5.75, 2.25, 5.75 / 2.25),
            (5.75, -2.25, 5.75 / -2.25),
            (-5.75, 2.25, -5.75 / 2.25),
            (-5.75, -2.25, -5.75 / -2.25),
            (1.0, 2.0, 0.5),
        ],
    )
    def test_division(self, a, b, expected):
        """Тест деления"""
        x = BinaryFloat(a)
        y = BinaryFloat(b)
        result = x / y
        assert abs(result.value - expected) < 1e-6

    def test_division_by_zero(self):
        """Деление на ноль"""
        x = BinaryFloat(5.75)
        y = BinaryFloat(0.0)
        with pytest.raises(ZeroDivisionError):
            x / y


class TestBinaryFloatUnaryOperations:
    """Тесты унарных операций"""

    @pytest.mark.parametrize(
        "value,expected",
        [
            (5.75, -5.75),
            (-5.75, 5.75),
            (0.0, 0.0),
        ],
    )
    def test_negation(self, value, expected):
        """Унарный минус"""
        num = BinaryFloat(value)
        neg = -num
        assert abs(neg.value - expected) < 1e-6


class TestBinaryFloatEdgeCases:
    """Тесты граничных случаев"""

    def test_zero_addition(self):
        """Сложение с нулем"""
        zero = BinaryFloat(0.0)
        num = BinaryFloat(5.75)

        assert (zero + num).value == 5.75
        assert (num + zero).value == 5.75

    def test_positive_negative_cancellation(self):
        """Взаимное уничтожение положительного и отрицательного"""
        pos = BinaryFloat(5.75)
        neg = BinaryFloat(-5.75)
        result = pos + neg
        assert abs(result.value) < 1e-6

    def test_small_numbers(self):
        """Очень маленькие числа (денормализованные)"""
        small = BinaryFloat(1e-40)
        # Проверяем, что создается без ошибок
        assert small is not None

    def test_large_numbers(self):
        """Очень большие числа"""
        large = BinaryFloat(1e38)
        assert large is not None


class TestBinaryFloatStringRepresentation:
    """Тесты строкового представления"""

    def test_str_method(self):
        """Метод __str__"""
        num = BinaryFloat(5.75)
        str_repr = str(num)
        assert "0100 0000 1011 1000 0000 0000 0000 0000" in str_repr
        assert "(5.75)" in str_repr

    def test_repr_method(self):
        """Метод __repr__"""
        num = BinaryFloat(5.75)
        repr_str = repr(num)
        assert repr_str == "BinaryFloat(5.75)"
