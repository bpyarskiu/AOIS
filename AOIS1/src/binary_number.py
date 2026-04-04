class BinaryNumber:
    """
    Класс для представления 32-битных двоичных чисел
    Поддерживает различные форматы: прямой, обратный, дополнительный код
    """

    def __init__(self, value=0, code_type="additional"):
        """
        Инициализация двоичного числа
        :param value: целое число или двоичная строка
        :param code_type: тип кода ('straight', 'reverse', 'additional')
        """
        self.bits = 32
        self.code_type = code_type

        if isinstance(value, int):
            # Если передано целое число
            self.value = value
            self.binary = self.int_to_binary(value, code_type)
        elif isinstance(value, str):
            # Если передана двоичная строка
            self.binary = value.zfill(32)
            self.value = self.binary_to_int(self.binary, code_type)
        else:
            raise TypeError("Поддерживаются только int и str")
        if code_type not in ["straight", "reverse", "additional"]:
            raise ValueError(f"Неизвестный тип кода: {code_type}")

    # ============== Базовые преобразования ==============

    def int_to_binary(self, num, code_type):
        """Преобразование целого числа в двоичную строку заданного типа"""
        if num >= 0:
            # Для положительных все коды одинаковы
            return self._positive_to_binary(num)
        else:
            # Для отрицательных в зависимости от типа кода
            if code_type == "straight":
                return self._negative_to_straight(num)
            elif code_type == "reverse":
                return self._negative_to_reverse(num)
            elif code_type == "additional":
                return self._negative_to_additional(num)
            else:
                raise ValueError(f"Неизвестный тип кода: {code_type}")

    def _positive_to_binary(self, num):
        """Прямой код для положительного числа"""
        if num == 0:
            return "0" * 32

        binary_parts = []
        temp = num
        while temp > 0:
            binary_parts.append(str(temp % 2))
            temp = temp // 2

        binary = "".join(reversed(binary_parts))
        return "0" + binary.zfill(31)

    def _negative_to_straight(self, num):
        """Прямой код для отрицательного числа"""
        abs_num = abs(num)
        if abs_num == 0:
            return "1" + "0" * 31

        binary_parts = []
        temp = abs_num
        while temp > 0:
            binary_parts.append(str(temp % 2))
            temp = temp // 2

        binary = "".join(reversed(binary_parts))
        return "1" + binary.zfill(31)

    def _negative_to_reverse(self, num):
        """Обратный код для отрицательного числа"""
        # Сначала получаем прямой код модуля
        abs_num = abs(num)
        if abs_num == 0:
            abs_binary = "0" * 31
        else:
            binary_parts = []
            temp = abs_num
            while temp > 0:
                binary_parts.append(str(temp % 2))
                temp = temp // 2
            abs_binary = "".join(reversed(binary_parts))
            abs_binary = abs_binary.zfill(31)

        # Инвертируем все биты
        inverted = ""
        for bit in abs_binary:
            inverted += "1" if bit == "0" else "0"

        return "1" + inverted

    def _negative_to_additional(self, num):
        """Дополнительный код для отрицательного числа"""
        # Получаем обратный код
        reverse = self._negative_to_reverse(num)
        # Прибавляем 1
        one = BinaryNumber(1, "straight")
        result = self._binary_add(reverse, one.binary)
        return result[-32:]

    def binary_to_int(self, binary, code_type):
        """Преобразование двоичной строки в целое число"""
        if binary[0] == "0":
            # Положительное число
            result = 0
            for i, bit in enumerate(binary[1:]):
                if bit == "1":
                    result += 2 ** (30 - i)
            return result
        else:
            # Отрицательное число
            if code_type == "straight":
                # Прямой код: просто модуль со знаком минус
                result = 0
                for i, bit in enumerate(binary[1:]):
                    if bit == "1":
                        result += 2 ** (30 - i)
                return -result
            elif code_type == "reverse":
                # Обратный код: инвертируем и получаем модуль
                inverted = ""
                for bit in binary[1:]:
                    inverted += "1" if bit == "0" else "0"
                result = 0
                for i, bit in enumerate(inverted):
                    if bit == "1":
                        result += 2 ** (30 - i)
                return -result
            elif code_type == "additional":
                # Дополнительный код: инвертируем, прибавляем 1
                inverted = ""
                for bit in binary[1:]:
                    inverted += "1" if bit == "0" else "0"
                # Прибавляем 1
                one = BinaryNumber(1, "straight")
                abs_binary = self._binary_add("0" + inverted, one.binary)
                abs_binary = abs_binary[-32:]
                result = 0
                for i, bit in enumerate(abs_binary[1:]):
                    if bit == "1":
                        result += 2 ** (30 - i)
                return -result

    # ============== Арифметические операции ==============

    @staticmethod
    def _binary_add(bin1, bin2):
        """Сложение двух двоичных строк"""
        # Дополняем до одинаковой длины
        max_len = max(len(bin1), len(bin2))
        bin1 = bin1.zfill(max_len)
        bin2 = bin2.zfill(max_len)

        result = []
        carry = 0

        for i in range(max_len - 1, -1, -1):
            bit1 = int(bin1[i])
            bit2 = int(bin2[i])

            sum_bits = bit1 + bit2 + carry
            result_bit = sum_bits % 2
            carry = sum_bits // 2

            result.insert(0, str(result_bit))

        if carry:
            result.insert(0, "1")

        return "".join(result)

    @staticmethod
    def _binary_subtract(bin1, bin2):
        """Вычитание двоичных строк (bin1 - bin2) через дополнительный код"""
        # Получаем дополнительный код bin2
        inverted = ""
        for bit in bin2:
            inverted += "1" if bit == "0" else "0"

        # Прибавляем 1 к инвертированному
        one = "0" * (len(bin2) - 1) + "1"
        neg_bin2 = BinaryNumber._binary_add(inverted, one)
        if len(neg_bin2) > len(bin2):
            neg_bin2 = neg_bin2[-len(bin2) :]

        # Складываем bin1 с отрицательным bin2
        result = BinaryNumber._binary_add(bin1, neg_bin2)
        return result[-len(bin1) :]

    @staticmethod
    def _binary_multiply(bin1, bin2):
        """Умножение двоичных строк"""
        len1, len2 = len(bin1), len(bin2)

        # Сдвигаем и складываем
        results = []
        for i in range(len2 - 1, -1, -1):
            if bin2[i] == "1":
                shifted = bin1 + "0" * (len2 - 1 - i)
                results.append(shifted)

        if not results:
            return "0" * (len1 + len2)

        result = results[0]
        for i in range(1, len(results)):
            result = BinaryNumber._binary_add(result, results[i])

        return result

    # ============== Магические методы ==============

    def __add__(self, other):
        """Сложение двух двоичных чисел"""
        if not isinstance(other, BinaryNumber):
            other = BinaryNumber(other)

        # Для сложения используем дополнительный код
        if self.code_type != "additional":
            self_in_add = self.to_code("additional")
        else:
            self_in_add = self

        if other.code_type != "additional":
            other_in_add = other.to_code("additional")
        else:
            other_in_add = other

        # Складываем
        result_binary = self._binary_add(self_in_add.binary, other_in_add.binary)
        result_binary = result_binary[-32:]  # Обрезаем до 32 бит

        # Создаем результат в дополнительном коде
        result = BinaryNumber(result_binary, "additional")

        # Если исходные числа были в другом коде, преобразуем результат
        if self.code_type != "additional":
            return result.to_code(self.code_type)
        return result

    def __sub__(self, other):
        """Вычитание через сложение с отрицательным числом"""
        return self + (-other)

    def __mul__(self, other):
        """Умножение в прямом коде"""
        if not isinstance(other, BinaryNumber):
            other = BinaryNumber(other)

        # Для умножения используем прямой код
        self_straight = self.to_code("straight")
        other_straight = other.to_code("straight")

        # Определяем знак результата
        sign = "0" if self_straight.binary[0] == other_straight.binary[0] else "1"

        # Берем модули (убираем знаковый бит)
        mag1 = self_straight.binary[1:]
        mag2 = other_straight.binary[1:]

        # Умножаем модули
        result_mag = self._binary_multiply(mag1, mag2)

        # Обрезаем до 31 бита
        if len(result_mag) > 31:
            result_mag = result_mag[-31:]
        else:
            result_mag = result_mag.zfill(31)

        # Добавляем знак
        result_binary = sign + result_mag

        return BinaryNumber(result_binary, "straight").to_code(self.code_type)

    def __truediv__(self, other):
        """
        Деление методом последовательного вычитания
        Возвращает целую часть от деления
        """
        if not isinstance(other, BinaryNumber):
            other = BinaryNumber(other)

        
        if other.value == 0:
            raise ZeroDivisionError("Деление на ноль!")

        
        self_straight = self.to_code("straight")
        other_straight = other.to_code("straight")

        # Определяем знак результата
        sign = "0" if self_straight.binary[0] == other_straight.binary[0] else "1"

        
        dividend_abs = self_straight.value
        divisor_abs = other_straight.value

        # Если делимое меньше делителя, результат 0
        if abs(dividend_abs) < abs(divisor_abs):
            return BinaryNumber(0, self.code_type)

        # Последовательное вычитание
        quotient = 0
        remainder_abs = abs(dividend_abs)
        divisor_abs_val = abs(divisor_abs)

        print(f"\nДеление {dividend_abs} на {divisor_abs_val}:")
        step = 1

        while remainder_abs >= divisor_abs_val:
            remainder_abs -= divisor_abs_val
            quotient += 1
            print(
                f"  Шаг {step}: {remainder_abs + divisor_abs_val} - {divisor_abs_val} = {remainder_abs}, частное = {quotient}"
            )
            step += 1

        # Применяем знак
        if sign == "1":
            quotient = -quotient

        print(f"Результат: {quotient}")

        return BinaryNumber(quotient, self.code_type)

    def __floordiv__(self, other):
        """Целочисленное деление"""
        return (self / other).to_code("straight")

    def __mod__(self, other):
        """Остаток от деления"""
        if not isinstance(other, BinaryNumber):
            other = BinaryNumber(other)

        quotient = self // other
        return self - (quotient * other)

    def __neg__(self):
        """Унарный минус - получение числа с противоположным знаком"""
        if self.binary[0] == "0":
            # Положительное -> отрицательное
            if self.code_type == "straight":
                return BinaryNumber("1" + self.binary[1:], "straight")
            elif self.code_type == "reverse":
                inverted = ""
                for bit in self.binary[1:]:
                    inverted += "1" if bit == "0" else "0"
                return BinaryNumber("1" + inverted, "reverse")
            elif self.code_type == "additional":
                # Для доп. кода: инвертируем и прибавляем 1
                inverted = ""
                for bit in self.binary:
                    inverted += "1" if bit == "0" else "0"
                one = BinaryNumber(1, "straight")
                result = self._binary_add(inverted, one.binary)
                return BinaryNumber(result[-32:], "additional")
        else:
            # Отрицательное -> положительное
            if self.code_type == "straight":
                return BinaryNumber("0" + self.binary[1:], "straight")
            elif self.code_type == "reverse":
                inverted = ""
                for bit in self.binary[1:]:
                    inverted += "1" if bit == "0" else "0"
                return BinaryNumber("0" + inverted, "reverse")
            elif self.code_type == "additional":
                # Для доп. кода: инвертируем и прибавляем 1
                inverted = ""
                for bit in self.binary:
                    inverted += "1" if bit == "0" else "0"
                one = BinaryNumber(1, "straight")
                result = self._binary_add(inverted, one.binary)
                return BinaryNumber(result[-32:], "additional")

    def __abs__(self):
        """Модуль числа"""
        return BinaryNumber(abs(self.value), self.code_type)

    def __int__(self):
        """Преобразование в int"""
        return self.value

    def __float__(self):
        """Преобразование в float"""
        return float(self.value)

    # ============== Методы сравнения ==============

    def __eq__(self, other):
        if not isinstance(other, BinaryNumber):
            other = BinaryNumber(other)
        return self.value == other.value

    def __lt__(self, other):
        if not isinstance(other, BinaryNumber):
            other = BinaryNumber(other)
        return self.value < other.value

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not (self <= other)

    def __ge__(self, other):
        return not (self < other)

    # ============== Методы представления ==============

    def __str__(self):
        """Строковое представление"""
        binary_display = self.binary
        # Группируем по 4 бита для читаемости
        grouped = " ".join([binary_display[i : i + 4] for i in range(0, 32, 4)])
        return f"{grouped} ({self.value}) [{self.code_type}]"

    def __repr__(self):
        return f"BinaryNumber({self.value}, '{self.code_type}')"

    def to_code(self, code_type):
        """Преобразование в другой тип кода"""
        if code_type == self.code_type:
            return self

        if code_type == "straight":
            return BinaryNumber(self.value, "straight")
        elif code_type == "reverse":
            return BinaryNumber(self.value, "reverse")
        elif code_type == "additional":
            return BinaryNumber(self.value, "additional")
        else:
            raise ValueError(f"Неизвестный тип кода: {code_type}")

    def to_binary_string(self, grouped=True):
        """Получение двоичной строки"""
        if grouped:
            return " ".join([self.binary[i : i + 4] for i in range(0, 32, 4)])
        return self.binary
