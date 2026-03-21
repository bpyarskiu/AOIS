# from binary_number import BinaryNumber
class BCDExcess3:
    """
    Класс для представления чисел в коде BCD Excess-3 (8 десятичных цифр в 32 битах)
    Формат: 32 бита = 8 тетрад (nibble) по 4 бита, каждая тетрада хранит цифру + 3
    """

    # Константы класса
    BITS_PER_DIGIT = 4
    MAX_DIGITS = 8
    BIT_WIDTH = 32
    # Коррекция для Excess-3 (число 3 в двоичном виде для 4 бит)
    CORRECTION = [0, 0, 1, 1]  # 3 в двоичном

    def __init__(self, value=0):
        """
        Инициализация BCD Excess-3 числа

        Args:
            value: может быть int (десятичное число) или list (32-битный массив)
        """
        if isinstance(value, int):
            if value < 0:
                raise ValueError(
                    "BCD Excess-3 поддерживает только неотрицательные числа"
                )
            if value >= 10**self.MAX_DIGITS:
                raise OverflowError(
                    f"Число превышает максимальное значение для {self.MAX_DIGITS} цифр"
                )

            self.value = value
            self.bits = self._decimal_to_bits(value)

        elif isinstance(value, list) and len(value) == self.BIT_WIDTH:
            # Принимаем готовый битовый массив
            self.bits = value.copy()
            self.value = self._bits_to_decimal(value)

        elif isinstance(value, str):
            # Поддержка строки для удобства (например, из другого формата)
            bits = [int(b) for b in value.replace(" ", "")]
            if len(bits) != self.BIT_WIDTH:
                raise ValueError(f"Строка должна содержать {self.BIT_WIDTH} бит")
            self.bits = bits
            self.value = self._bits_to_decimal(bits)

        else:
            raise TypeError("Поддерживаются типы: int, list (32 бита), str")

    # ============== Базовые преобразования ==============

    def _decimal_to_bits(self, num: int) -> list:
        """Преобразование десятичного числа в 32-битный массив Excess-3"""
        # Получаем цифры числа
        digits = self._int_to_digits(num)

        # Создаем массив из 32 нулей
        bits = [0] * self.BIT_WIDTH

        # Код для нуля в Excess-3 (0 + 3 = 3 -> 0011)
        zero_code = self._int_to_nibble_bits(3)

        # Заполняем все тетрады кодом нуля
        for nibble_idx in range(self.MAX_DIGITS):
            start = nibble_idx * self.BITS_PER_DIGIT
            bits[start : start + self.BITS_PER_DIGIT] = zero_code

        # Размещаем цифры числа справа (младшие разряды)
        offset = self.MAX_DIGITS - len(digits)
        for i, digit in enumerate(digits):
            code = digit + 3
            code_bits = self._int_to_nibble_bits(code)
            start = (offset + i) * self.BITS_PER_DIGIT
            bits[start : start + self.BITS_PER_DIGIT] = code_bits

        return bits

    def _bits_to_decimal(self, bits: list) -> int:
        """Преобразование 32-битного массива Excess-3 в десятичное число"""
        digits = []

        for nibble_idx in range(self.MAX_DIGITS):
            start = nibble_idx * self.BITS_PER_DIGIT
            nibble = bits[start : start + self.BITS_PER_DIGIT]
            code = self._nibble_bits_to_int(nibble)

            # Проверка корректности Excess-3 кода (допустимые значения 3-12)
            if code < 3 or code > 12:
                raise ValueError(
                    f"Некорректный Excess-3 код в тетраде {nibble_idx}: {code}"
                )

            digits.append(code - 3)

        # Убираем ведущие нули
        first_non_zero = 0
        while first_non_zero < len(digits) - 1 and digits[first_non_zero] == 0:
            first_non_zero += 1

        return self._digits_to_int(digits[first_non_zero:])

    @staticmethod
    def _int_to_digits(num: int) -> list:
        """Преобразование целого числа в список цифр"""
        if num == 0:
            return [0]

        reversed_digits = []
        current = num
        while current > 0:
            reversed_digits.append(current % 10)
            current //= 10

        # Разворачиваем
        digits = []
        for i in range(len(reversed_digits) - 1, -1, -1):
            digits.append(reversed_digits[i])

        return digits

    @staticmethod
    def _digits_to_int(digits: list) -> int:
        """Преобразование списка цифр в целое число"""
        result = 0
        for digit in digits:
            result = result * 10 + digit
        return result

    @staticmethod
    def _int_to_nibble_bits(num: int) -> list:
        """Преобразование числа (0-15) в 4-битный массив"""
        if num < 0 or num > 15:
            raise ValueError(f"Число {num} не помещается в 4 бита")

        bits = [0] * 4
        for i in range(3, -1, -1):
            bits[i] = num & 1
            num >>= 1
        return bits

    @staticmethod
    def _nibble_bits_to_int(bits: list) -> int:
        """Преобразование 4-битного массива в число"""
        if len(bits) != 4:
            raise ValueError(f"Ожидался 4-битный массив, получен {len(bits)}")

        result = 0
        for bit in bits:
            result = (result << 1) | bit
        return result

    # ============== Вспомогательные операции с битами ==============

    @staticmethod
    def _add_nibbles(nibble1: list, nibble2: list, carry_in: int = 0) -> tuple:
        """
        Сложение двух 4-битных чисел с переносом

        Returns:
            tuple: (результат (4 бита), перенос наружу)
        """
        # Преобразуем в целые числа для простоты
        a = BCDExcess3._nibble_bits_to_int(nibble1)
        b = BCDExcess3._nibble_bits_to_int(nibble2)

        total = a + b + carry_in

        # Результат (младшие 4 бита)
        result_bits = BCDExcess3._int_to_nibble_bits(total & 0b1111)
        # Перенос (старшие биты)
        carry_out = 1 if total > 15 else 0

        return result_bits, carry_out

    @staticmethod
    def _subtract_nibbles(nibble1: list, nibble2: list, borrow_in: int = 0) -> tuple:
        """
        Вычитание двух 4-битных чисел с заемом (nibble1 - nibble2 - borrow_in)

        Returns:
            tuple: (результат (4 бита), заем наружу)
        """
        a = BCDExcess3._nibble_bits_to_int(nibble1)
        b = BCDExcess3._nibble_bits_to_int(nibble2)

        total = a - b - borrow_in

        if total >= 0:
            result_bits = BCDExcess3._int_to_nibble_bits(total)
            borrow_out = 0
        else:
            # Занимаем 16
            result_bits = BCDExcess3._int_to_nibble_bits(total + 16)
            borrow_out = 1

        return result_bits, borrow_out

    @staticmethod
    def _compare_nibbles(nibble1: list, nibble2: list) -> int:
        """Сравнение двух 4-битных чисел: -1 если <, 0 если =, 1 если >"""
        a = BCDExcess3._nibble_bits_to_int(nibble1)
        b = BCDExcess3._nibble_bits_to_int(nibble2)

        if a < b:
            return -1
        elif a > b:
            return 1
        else:
            return 0

    # ============== Арифметические операции ==============

    def __add__(self, other):
        """Сложение двух чисел в коде Excess-3"""
        if not isinstance(other, BCDExcess3):
            other = BCDExcess3(other)

        print(f"\n{'='*60}")
        print(f"СЛОЖЕНИЕ BCD EXCESS-3:")
        print(f"  {self.to_str()}  ({self.value})")
        print(f"+ {other.to_str()}  ({other.value})")
        print(f"{'-'*60}")

        # Результирующий массив битов
        result_bits = [0] * self.BIT_WIDTH
        carry = 0  # перенос между тетрадами

        # Проходим по тетрадам справа налево (от младших к старшим)
        for nibble_idx in range(self.MAX_DIGITS - 1, -1, -1):
            start = nibble_idx * self.BITS_PER_DIGIT
            a_nibble = self.bits[start : start + self.BITS_PER_DIGIT]
            b_nibble = other.bits[start : start + self.BITS_PER_DIGIT]

            a_val = self._nibble_bits_to_int(a_nibble)
            b_val = self._nibble_bits_to_int(b_nibble)
            a_digit = a_val - 3
            b_digit = b_val - 3

            print(
                f"\n  Тетрада {nibble_idx} (позиция {self.MAX_DIGITS-1-nibble_idx} справа):"
            )
            print(
                f"    {self._nibble_to_str(a_nibble)} (Excess-3: {a_val:2d} -> цифра {a_digit})"
            )
            print(
                f"  + {self._nibble_to_str(b_nibble)} (Excess-3: {b_val:2d} -> цифра {b_digit})"
            )
            print(f"  + перенос: {carry}")

            # 1. Двоичное сложение тетрад с учетом переноса
            raw_sum, nibble_carry = self._add_nibbles(a_nibble, b_nibble, carry)
            raw_sum_val = self._nibble_bits_to_int(raw_sum)

            print(
                f"    Сумма (двоичная): {self._nibble_to_str(raw_sum)} = {raw_sum_val:2d}"
            )

            # 2. Excess-3 коррекция
            if nibble_carry == 1:
                # Был перенос - значит сумма цифр >= 10
                # Коррекция: прибавляем 3
                corrected, _ = self._add_nibbles(raw_sum, self.CORRECTION, 0)
                carry = 1
                print(
                    f"    Есть перенос -> +3 коррекция: {self._nibble_to_str(corrected)}"
                )
            else:
                # Не было переноса - значит сумма цифр < 10
                # Коррекция: вычитаем 3
                # Проверяем, что сумма достаточно велика для вычитания
                if self._compare_nibbles(raw_sum, self.CORRECTION) < 0:
                    raise ValueError(f"Ошибка коррекции: {raw_sum_val} < 3")
                corrected, _ = self._subtract_nibbles(raw_sum, self.CORRECTION, 0)
                carry = 0
                print(
                    f"    Нет переноса -> -3 коррекция: {self._nibble_to_str(corrected)}"
                )

            # 3. Сохраняем результат
            result_bits[start : start + self.BITS_PER_DIGIT] = corrected
            corrected_val = self._nibble_bits_to_int(corrected)
            corrected_digit = corrected_val - 3
            print(
                f"    Результат: {self._nibble_to_str(corrected)} (Excess-3: {corrected_val:2d} -> цифра {corrected_digit})"
            )
            print(f"    Новый перенос: {carry}")

        # Проверка на переполнение
        overflow = carry == 1
        if overflow:
            print(
                f"\n  ВНИМАНИЕ: Переполнение! Результат требует более {self.MAX_DIGITS} цифр"
            )

        # Создаем результат
        result = BCDExcess3(result_bits)
        exact = self.value + other.value

        print(f"\n  Результат в BCD Excess-3: {result.to_str()}")
        print(f"  = {result.value}")
        print(f"  Проверка: {self.value} + {other.value} = {exact}")
        if overflow:
            print(f"  (Переполнение: сохранено только {result.value})")
        print(f"{'='*60}")

        return result

    def __sub__(self, other):
        """Вычитание двух чисел в коде Excess-3"""
        if not isinstance(other, BCDExcess3):
            other = BCDExcess3(other)

        print(f"\n{'='*60}")
        print(f"ВЫЧИТАНИЕ BCD EXCESS-3:")
        print(f"  {self.to_str()}  ({self.value})")
        print(f"- {other.to_str()}  ({other.value})")
        print(f"{'-'*60}")

        # Проверка на отрицательный результат
        if other.value > self.value:
            raise ValueError(
                f"Отрицательный результат: {self.value} - {other.value} < 0"
            )

        # Результирующий массив битов
        result_bits = [0] * self.BIT_WIDTH
        borrow = 0  # заем из старшего разряда

        # Проходим по тетрадам справа налево
        for nibble_idx in range(self.MAX_DIGITS - 1, -1, -1):
            start = nibble_idx * self.BITS_PER_DIGIT
            a_nibble = self.bits[start : start + self.BITS_PER_DIGIT]
            b_nibble = other.bits[start : start + self.BITS_PER_DIGIT]

            a_val = self._nibble_bits_to_int(a_nibble)
            b_val = self._nibble_bits_to_int(b_nibble)
            a_digit = a_val - 3
            b_digit = b_val - 3

            print(
                f"\n  Тетрада {nibble_idx} (позиция {self.MAX_DIGITS-1-nibble_idx} справа):"
            )
            print(
                f"    {self._nibble_to_str(a_nibble)} (Excess-3: {a_val:2d} -> цифра {a_digit})"
            )
            print(
                f"  - {self._nibble_to_str(b_nibble)} (Excess-3: {b_val:2d} -> цифра {b_digit})"
            )
            print(f"  - заем: {borrow}")

            # Преобразуем в цифры, вычитаем с заемом
            diff_digit = a_digit - b_digit - borrow

            if diff_digit >= 0:
                # Не нужно занимать
                new_borrow = 0
                print(
                    f"    Разность цифр: {a_digit} - {b_digit} - {borrow} = {diff_digit}"
                )
            else:
                # Нужно занять из старшего разряда
                diff_digit += 10
                new_borrow = 1
                print(f"    Заем: добавляем 10 -> {diff_digit}")

            # Преобразуем обратно в Excess-3
            excess_val = diff_digit + 3
            print(f"    Преобразуем в Excess-3: {diff_digit} + 3 = {excess_val}")

            # Переводим в 4-битный массив
            corrected = self._int_to_nibble_bits(excess_val)
            result_bits[start : start + self.BITS_PER_DIGIT] = corrected
            borrow = new_borrow

            print(
                f"    Результат: {self._nibble_to_str(corrected)} (Excess-3: {excess_val:2d} -> цифра {diff_digit})"
            )
            print(f"    Новый заем: {borrow}")

        if borrow == 1:
            print(
                f"\n  ВНИМАНИЕ: Заем после старшей тетрады! Возможно, результат отрицательный?"
            )

        # Создаем результат
        result = BCDExcess3(result_bits)

        print(f"\n  Результат в BCD Excess-3: {result.to_str()}")
        print(f"  = {result.value}")
        print(f"  Проверка: {self.value} - {other.value} = {self.value - other.value}")
        print(f"{'='*60}")

        return result

    # ============== Магические методы ==============

    def __int__(self):
        """Преобразование в int"""
        return self.value

    def __str__(self):
        """Строковое представление для пользователя"""
        return f"{self.to_str()} ({self.value})"

    def __repr__(self):
        return f"BCDExcess3({self.value})"

    def __eq__(self, other):
        if not isinstance(other, BCDExcess3):
            other = BCDExcess3(other)
        return self.value == other.value

    def __lt__(self, other):
        if not isinstance(other, BCDExcess3):
            other = BCDExcess3(other)
        return self.value < other.value

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not (self <= other)

    def __ge__(self, other):
        return not (self < other)

    # ============== Вспомогательные методы для вывода ==============

    def to_str(self, grouped=True) -> str:
        """Получение строки с двоичным представлением"""
        if grouped:
            # Группируем по тетрадам
            groups = []
            for nibble_idx in range(self.MAX_DIGITS):
                start = nibble_idx * self.BITS_PER_DIGIT
                nibble = self.bits[start : start + self.BITS_PER_DIGIT]
                groups.append("".join(str(b) for b in nibble))
            return " ".join(groups)
        else:
            return "".join(str(b) for b in self.bits)

    def _nibble_to_str(self, nibble: list) -> str:
        """Преобразование 4-битного массива в строку"""
        return "".join(str(b) for b in nibble)

    def print_nibbles(self):
        """Детальный вывод всех тетрад с расшифровкой"""
        print(f"\nДетальное представление числа {self.value}:")
        for nibble_idx in range(self.MAX_DIGITS):
            start = nibble_idx * self.BITS_PER_DIGIT
            nibble = self.bits[start : start + self.BITS_PER_DIGIT]
            code = self._nibble_bits_to_int(nibble)
            digit = code - 3
            print(
                f"  Тетрада {nibble_idx}: {self._nibble_to_str(nibble)} = {code:2d} -> цифра {digit}"
            )
