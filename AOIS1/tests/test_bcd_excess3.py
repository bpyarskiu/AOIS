import pytest
from src.binary_excess3 import BCDExcess3


class TestBCDExcess3Creation:
    """Тесты создания объектов BCDExcess3"""

    def test_create_from_int(self):
        """Создание числа из целого значения"""
        num = BCDExcess3(123)
        assert num.value == 123
        assert len(num.bits) == 32
        # Проверяем, что все тетрады корректны
        for nibble_idx in range(8):
            start = nibble_idx * 4
            nibble = num.bits[start : start + 4]
            code = num._nibble_bits_to_int(nibble)
            assert 3 <= code <= 12

    def test_create_from_zero(self):
        """Создание нуля"""
        num = BCDExcess3(0)
        assert num.value == 0
        # Все тетрады должны быть 0011 (3)
        for nibble_idx in range(8):
            start = nibble_idx * 4
            nibble = num.bits[start : start + 4]
            assert nibble == [0, 0, 1, 1]

    def test_create_from_bits(self):
        """Создание из битового массива"""
        bits = [0] * 32
        # Устанавливаем число 123 в младшие тетрады
        # 1 -> 4 (0100), 2 -> 5 (0101), 3 -> 6 (0110)
        bits[0:20] = [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1,0,0,1,1]
        bits[20:24] = [0, 1, 0, 0]  # 1 в Excess-3
        bits[24:28] = [0, 1, 0, 1]  # 2 в Excess-3
        bits[28:32] = [0, 1, 1, 0]  # 3 в Excess-3

        num = BCDExcess3(bits)
        assert num.value == 123

    def test_create_from_string(self):
        """Создание из строки с битами"""
        bits_str = "0011 0011 0011 0011 0011 0100 0101 0110"
        num = BCDExcess3(bits_str)
        assert num.value == 123

    def test_invalid_negative_int(self):
        """Проверка на отрицательное число"""
        with pytest.raises(ValueError, match="только неотрицательные"):
            BCDExcess3(-5)

    def test_invalid_too_large_int(self):
        """Проверка на слишком большое число"""
        with pytest.raises(OverflowError):
            BCDExcess3(10**8)  # 9 цифр, а максимум 8


class TestBCDExcess3Conversion:
    """Тесты внутренних методов преобразования"""

    def test_int_to_digits(self):
        """Преобразование числа в список цифр"""
        assert BCDExcess3._int_to_digits(123) == [1, 2, 3]
        assert BCDExcess3._int_to_digits(0) == [0]
        assert BCDExcess3._int_to_digits(1000) == [1, 0, 0, 0]

    def test_digits_to_int(self):
        """Преобразование списка цифр в число"""
        assert BCDExcess3._digits_to_int([1, 2, 3]) == 123
        assert BCDExcess3._digits_to_int([0]) == 0
        assert BCDExcess3._digits_to_int([1, 0, 0, 0]) == 1000

    def test_int_to_nibble_bits(self):
        """Преобразование числа в 4-битный массив"""
        assert BCDExcess3._int_to_nibble_bits(3) == [0, 0, 1, 1]
        assert BCDExcess3._int_to_nibble_bits(12) == [1, 1, 0, 0]

        with pytest.raises(ValueError):
            BCDExcess3._int_to_nibble_bits(16)

    def test_nibble_bits_to_int(self):
        """Преобразование 4-битного массива в число"""
        assert BCDExcess3._nibble_bits_to_int([0, 0, 1, 1]) == 3
        assert BCDExcess3._nibble_bits_to_int([1, 1, 0, 0]) == 12

        with pytest.raises(ValueError):
            BCDExcess3._nibble_bits_to_int([0, 0, 1])  # меньше 4 бит

    def test_nibble_operations(self):
        """Тест операций с тетрадами"""
        # Сложение
        res, carry = BCDExcess3._add_nibbles([0, 1, 1, 0], [0, 1, 0, 1], 0)
        assert res == [1, 0, 1, 1]  # 6 + 5 = 11
        assert carry == 0

        res, carry = BCDExcess3._add_nibbles([1, 0, 0, 0], [1, 0, 0, 0], 0)
        assert carry == 1  # 8 + 8 = 16 -> перенос

        # Вычитание
        res, borrow = BCDExcess3._subtract_nibbles([0, 1, 1, 0], [0, 0, 1, 1], 0)
        assert res == [0, 0, 1, 1]  # 6 - 3 = 3

        res, borrow = BCDExcess3._subtract_nibbles([0, 0, 1, 1], [0, 1, 1, 0], 0)
        assert borrow == 1  # 3 - 6 -> заем

        # Сравнение
        assert BCDExcess3._compare_nibbles([0, 1, 1, 0], [0, 1, 0, 1]) == 1  # 6 > 5
        assert BCDExcess3._compare_nibbles([0, 1, 0, 1], [0, 1, 1, 0]) == -1  # 5 < 6
        assert BCDExcess3._compare_nibbles([0, 1, 1, 0], [0, 1, 1, 0]) == 0  # 6 == 6


class TestBCDExcess3Arithmetic:
    """Тесты арифметических операций"""

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (12, 34, 46),  # без переноса
            (8, 5, 13),  # с переносом в тетраде
            (78, 45, 123),  # с межразрядным переносом
            (999, 1, 1000),  # с переносом через несколько разрядов
            (0, 123, 123),  # с нулем
            (99999999, 0, 99999999),  # максимальное значение
        ],
    )
    def test_addition(self, a, b, expected):
        """Тест сложения"""
        x = BCDExcess3(a)
        y = BCDExcess3(b)
        result = x + y
        assert result.value == expected
        assert isinstance(result, BCDExcess3)

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (78, 34, 44),  # без заема
            (52, 38, 14),  # с заемом в тетраде
            (1000, 999, 1),  # с заемом через несколько разрядов
            (123, 0, 123),  # вычитание нуля
            (99999999, 99999998, 1),  # граничный случай
        ],
    )
    def test_subtraction(self, a, b, expected):
        """Тест вычитания"""
        x = BCDExcess3(a)
        y = BCDExcess3(b)
        result = x - y
        assert result.value == expected
        assert isinstance(result, BCDExcess3)

    def test_subtraction_negative_result(self):
        """Тест попытки получить отрицательный результат"""
        x = BCDExcess3(5)
        y = BCDExcess3(10)

        with pytest.raises(ValueError, match="Отрицательный результат"):
            x - y

    def test_subtraction_equal_numbers(self):
        """Вычитание равных чисел"""
        x = BCDExcess3(123)
        y = BCDExcess3(123)
        result = x - y
        assert result.value == 0

    def test_chain_operations(self):
        """Цепочка операций"""
        a = BCDExcess3(125)
        b = BCDExcess3(236)
        c = BCDExcess3(48)

        result = a + b - c
        assert result.value == 125 + 236 - 48


class TestBCDExcess3Comparison:
    """Тесты операций сравнения"""

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (123, 123, True),
            (123, 456, False),
            (0, 0, True),
        ],
    )
    def test_equality(self, a, b, expected):
        """Тест равенства"""
        x = BCDExcess3(a)
        y = BCDExcess3(b)
        assert (x == y) == expected

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (123, 456, True),
            (456, 123, False),
            (123, 123, False),
        ],
    )
    def test_less_than(self, a, b, expected):
        """Тест меньше"""
        x = BCDExcess3(a)
        y = BCDExcess3(b)
        assert (x < y) == expected

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (456, 123, True),
            (123, 456, False),
            (123, 123, True),
        ],
    )
    def test_greater_than_or_equal(self, a, b, expected):
        """Тест больше или равно"""
        x = BCDExcess3(a)
        y = BCDExcess3(b)
        assert (x >= y) == expected


class TestBCDExcess3EdgeCases:
    """Тесты граничных случаев"""

    def test_max_value(self):
        """Максимальное значение (8 девяток)"""
        num = BCDExcess3(99999999)
        assert num.value == 99999999

        # Проверяем, что все тетрады содержат 9+3=12 -> 1100
        for nibble_idx in range(8):
            start = nibble_idx * 4
            nibble = num.bits[start : start + 4]
            assert nibble == [1, 1, 0, 0]

    def test_min_value(self):
        """Минимальное значение (0)"""
        num = BCDExcess3(0)
        assert num.value == 0

        # Все тетрады должны быть 0011 (3)
        for nibble_idx in range(8):
            start = nibble_idx * 4
            nibble = num.bits[start : start + 4]
            assert nibble == [0, 0, 1, 1]

    def test_invalid_nibble_in_bits(self):
        """Некорректный код в тетраде"""
        bits = [0] * 32
        bits[28:32] = [0, 0, 0, 0]  # код 0 (должен быть 3-12)

        with pytest.raises(ValueError, match="Некорректный Excess-3 код"):
            BCDExcess3(bits)


class TestBCDExcess3StringRepresentation:
    """Тесты строкового представления"""

    def test_str_method(self):
        """Тест метода __str__"""
        num = BCDExcess3(123)
        str_repr = str(num)
        assert "0011 0011 0011 0011 0011 0100 0101 0110" in str_repr
        assert "(123)" in str_repr

    def test_repr_method(self):
        """Тест метода __repr__"""
        num = BCDExcess3(123)
        repr_str = repr(num)
        assert repr_str == "BCDExcess3(123)"

    def test_to_str_grouped(self):
        """Тест grouped представления"""
        num = BCDExcess3(123)
        grouped = num.to_str(grouped=True)
        assert grouped == "0011 0011 0011 0011 0011 0100 0101 0110"

        ungrouped = num.to_str(grouped=False)
        assert ungrouped == "00110011001100110011010001010110"

    def test_print_nibbles(self, capsys):
        """Тест детального вывода (проверяем, что не падает)"""
        num = BCDExcess3(123)
        num.print_nibbles()
        captured = capsys.readouterr()
        assert "Тетрада" in captured.out
        assert "цифра" in captured.out
