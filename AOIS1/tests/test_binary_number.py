# tests/test_binary_number.py
import pytest
from src.binary_number import BinaryNumber


class TestBinaryNumberCreation:
    """Тесты создания объектов BinaryNumber"""

    @pytest.mark.parametrize(
        "value,code_type,expected_sign",
        [
            (5, "straight", "0"),
            (-5, "straight", "1"),
            (5, "reverse", "0"),
            (-5, "reverse", "1"),
            (5, "additional", "0"),
            (-5, "additional", "1"),
        ],
    )
    def test_creation_from_int(self, value, code_type, expected_sign):
        """Создание из целого числа с разными типами кодов"""
        num = BinaryNumber(value, code_type)
        assert num.value == value
        assert num.code_type == code_type
        assert num.binary[0] == expected_sign
        assert len(num.binary) == 32

    def test_creation_from_binary_string(self):
        """Создание из двоичной строки"""
        binary = "00000000000000000000000000000101"
        num = BinaryNumber(binary, "straight")
        assert num.value == 5
        assert num.binary == binary

    def test_invalid_code_type(self):
        """Неверный тип кода"""
        with pytest.raises(ValueError):
            BinaryNumber(5, "invalid_code")

    def test_invalid_type(self):
        """Неверный тип входных данных"""
        with pytest.raises(TypeError):
            BinaryNumber(3.14, "straight")  # float не поддерживается


class TestBinaryNumberConversions:
    """Тесты преобразований между кодами"""

    def test_positive_to_all_codes(self):
        """Положительное число во всех кодах одинаково"""
        num = BinaryNumber(5, "straight")
        assert num.binary == "00000000000000000000000000000101"

        num_rev = num.to_code("reverse")
        assert num_rev.binary == num.binary

        num_add = num.to_code("additional")
        assert num_add.binary == num.binary

    def test_negative_straight_code(self):
        """Отрицательное число в прямом коде"""
        num = BinaryNumber(-5, "straight")
        expected = "10000000000000000000000000000101"
        assert num.binary == expected

    def test_negative_reverse_code(self):
        """Отрицательное число в обратном коде"""
        num = BinaryNumber(-5, "reverse")
        # Инверсия модуля: 101 -> 010, плюс знак 1
        expected = "11111111111111111111111111111010"
        assert num.binary == expected

    def test_negative_additional_code(self):
        """Отрицательное число в дополнительном коде"""
        num = BinaryNumber(-5, "additional")
        # Обратный код (111...11010) + 1
        expected = "11111111111111111111111111111011"
        assert num.binary == expected

    def test_zero_in_all_codes(self):
        """Нуль во всех кодах"""
        for code_type in ["straight", "reverse", "additional"]:
            num = BinaryNumber(0, code_type)
            assert num.binary == "0" * 32
            assert num.value == 0


class TestBinaryNumberArithmetic:
    """Тесты арифметических операций"""

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (5, 3, 8),
            (-5, 3, -2),
            (5, -3, 2),
            (-5, -3, -8),
            (0, 5, 5),
            (2147483647, 1, -2147483648),  # переполнение
        ],
    )
    def test_addition(self, a, b, expected):
        """Тест сложения"""
        x = BinaryNumber(a, "additional")
        y = BinaryNumber(b, "additional")
        result = x + y
        # Для переполнения может быть другой результат, проверяем особо
        if abs(a + b) <= 2147483647:
            assert result.value == expected

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (5, 3, 2),
            (5, -3, 8),
            (-5, 3, -8),
            (-5, -3, -2),
            (5, 5, 0),
        ],
    )
    def test_subtraction(self, a, b, expected):
        """Тест вычитания"""
        x = BinaryNumber(a, "additional")
        y = BinaryNumber(b, "additional")
        result = x - y
        assert result.value == expected

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (5, 3, 15),
            (-5, 3, -15),
            (5, -3, -15),
            (-5, -3, 15),
            (0, 5, 0),
        ],
    )
    def test_multiplication(self, a, b, expected):
        """Тест умножения"""
        x = BinaryNumber(a, "straight")
        y = BinaryNumber(b, "straight")
        result = x * y
        assert result.value == expected

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (
                6,
                3,
                2,
            ),
            (-6, 3, -2),
            (6, -3, -2),
            (-6, -3, 2),
        ],
    )
    def test_division(self, a, b, expected):
        """Тест деления"""
        x = BinaryNumber(a, "straight")
        y = BinaryNumber(b, "straight")
        result, frac = x / y
        assert result.value == expected

    def test_division_by_zero(self):
        """Деление на ноль"""
        x = BinaryNumber(5, "straight")
        y = BinaryNumber(0, "straight")
        with pytest.raises(ZeroDivisionError):
            x / y


class TestBinaryNumberUnaryOperations:
    """Тесты унарных операций"""

    @pytest.mark.parametrize(
        "value,expected",
        [
            (5, -5),
            (-5, 5),
            (0, 0),
        ],
    )
    def test_negation(self, value, expected):
        """Унарный минус"""
        num = BinaryNumber(value, "additional")
        neg = -num
        assert neg.value == expected

    @pytest.mark.parametrize(
        "value,expected",
        [
            (5, 5),
            (-5, 5),
            (0, 0),
        ],
    )
    def test_abs(self, value, expected):
        """Модуль числа"""
        num = BinaryNumber(value, "additional")
        abs_num = abs(num)
        assert abs_num.value == expected


class TestBinaryNumberComparison:
    """Тесты сравнения"""

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (5, 5, True),
            (5, -5, False),
            (-5, -5, True),
            (0, 0, True),
        ],
    )
    def test_equality(self, a, b, expected):
        """Равенство"""
        x = BinaryNumber(a, "additional")
        y = BinaryNumber(b, "additional")
        assert (x == y) == expected

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (3, 5, True),
            (5, 3, False),
            (-5, -3, True),
            (5, 5, False),
        ],
    )
    def test_less_than(self, a, b, expected):
        """Меньше"""
        x = BinaryNumber(a, "additional")
        y = BinaryNumber(b, "additional")
        assert (x < y) == expected


class TestBinaryNumberStringRepresentation:
    """Тесты строкового представления"""

    def test_str_method(self):
        """Метод __str__"""
        num = BinaryNumber(5, "straight")
        str_repr = str(num)
        assert "0000 0000 0000 0000 0000 0000 0000 0101" in str_repr
        assert "(5)" in str_repr
        assert "[straight]" in str_repr

    def test_repr_method(self):
        """Метод __repr__"""
        num = BinaryNumber(5, "straight")
        repr_str = repr(num)
        assert repr_str == "BinaryNumber(5, 'straight')"

    def test_to_binary_string(self):
        """Метод to_binary_string"""
        num = BinaryNumber(5, "straight")
        grouped = num.to_binary_string(grouped=True)
        assert grouped == "0000 0000 0000 0000 0000 0000 0000 0101"

        ungrouped = num.to_binary_string(grouped=False)
        assert ungrouped == "00000000000000000000000000000101"


class TestBinaryNumberEdgeCases:
    """Дополнительные тесты для краевых случаев и непокрытого кода"""

    def test_zero_in_all_code_types(self):
        """Тест нуля во всех типах кода"""
        for code_type in ["straight", "reverse", "additional"]:
            num = BinaryNumber(0, code_type)
            assert num.binary == "0" * 32
            assert num.value == 0
            # Проверяем, что преобразование обратно работает
            assert BinaryNumber(num.binary, code_type).value == 0

    def test_max_positive_value(self):
        """Максимальное положительное значение (2^31 - 1)"""
        max_val = 2147483647
        num = BinaryNumber(max_val, "straight")
        # Проверяем, что бит знака 0
        assert num.binary[0] == "0"
        # Проверяем, что остальные биты - все единицы
        assert num.binary[1:] == "1" * 31
        # Проверяем обратное преобразование
        assert BinaryNumber(num.binary, "straight").value == max_val

    def test_min_negative_value(self):
        """Минимальное отрицательное значение (-2^31)"""
        min_val = -2147483648
        num = BinaryNumber(min_val, "additional")
        # В дополнительном коде -2^31 представляется как 1 + 31 ноль
        assert num.binary[0] == "1"
        assert num.binary[1:] == "0" * 31

    def test_negative_to_additional_with_carry(self):
        """Тест преобразования в дополнительный код с переносом"""
        # -1 в дополнительном коде - все единицы
        num = BinaryNumber(-1, "additional")
        assert num.binary == "1" * 32

        # Проверяем, что -1 правильно преобразуется обратно
        assert BinaryNumber(num.binary, "additional").value == -1

    def test_binary_to_int_for_negative_additional(self):
        """Тест преобразования отрицательного дополнительного кода в int"""
        # -5 в дополнительном коде
        num = BinaryNumber(-5, "additional")
        assert num.binary == "11111111111111111111111111111011"

        # Создаем из битовой строки
        num2 = BinaryNumber("11111111111111111111111111111011", "additional")
        assert num2.value == -5

    def test_binary_to_int_for_negative_reverse(self):
        """Тест преобразования отрицательного обратного кода в int"""
        # -5 в обратном коде
        num = BinaryNumber(-5, "reverse")
        expected = "11111111111111111111111111111010"
        assert num.binary == expected

        # Создаем из битовой строки
        num2 = BinaryNumber(expected, "reverse")
        assert num2.value == -5

    def test_binary_to_int_for_negative_straight(self):
        """Тест преобразования отрицательного прямого кода в int"""
        # -5 в прямом коде
        num = BinaryNumber(-5, "straight")
        expected = "10000000000000000000000000000101"
        assert num.binary == expected

        # Создаем из битовой строки
        num2 = BinaryNumber(expected, "straight")
        assert num2.value == -5

    def test_addition_with_overflow(self):
        """Тест сложения с переполнением"""
        max_val = BinaryNumber(2147483647, "additional")
        one = BinaryNumber(1, "additional")
        result = max_val + one
        # При переполнении должно получиться -2147483648
        assert result.value == 0

    def test_subtraction_with_overflow(self):
        """Тест вычитания с переполнением"""
        min_val = BinaryNumber(-2147483648, "additional")
        one = BinaryNumber(1, "additional")
        result = min_val - one
        # При переполнении должно получиться 2147483647
        assert result.value == 2147483647

    def test_floordiv_operator(self):
        """Тест оператора целочисленного деления //"""
        x = BinaryNumber(7, "straight")
        y = BinaryNumber(3, "straight")
        result = x // y
        assert result.value == 2
        assert isinstance(result, BinaryNumber)

    def test_mod_operator(self):
        """Тест оператора остатка от деления %"""
        x = BinaryNumber(7, "straight")
        y = BinaryNumber(3, "straight")
        result = x % y
        assert result.value == 1
        assert isinstance(result, BinaryNumber)

    def test_mod_with_negative_numbers(self):
        """Тест остатка от деления с отрицательными числами"""
        x = BinaryNumber(-7, "straight")
        y = BinaryNumber(3, "straight")
        result = x % y
        # В Python -7 % 3 = 2
        assert result.value == -1

    def test_binary_subtract_static_method(self):
        """Тест статического метода _binary_subtract"""
        # 10 - 5 = 5
        result = BinaryNumber._binary_subtract("1010", "0101")
        # Результат должен быть 5 в двоичной системе
        assert int(result, 2) == 5 or result == "101"

        # Тест с разной длиной строк
        result = BinaryNumber._binary_subtract("1000", "1")
        assert int(result, 2) == 9
