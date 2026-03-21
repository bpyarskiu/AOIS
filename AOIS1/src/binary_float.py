# from binary_number import BinaryNumber


class BinaryFloat:
    """Класс для чисел с плавающей точкой по стандарту IEEE-754 (32 бита)"""

    def __init__(self, value=0.0):
        self.bits = 32
        self.sign_bits = 1
        self.exp_bits = 8
        self.mantissa_bits = 23

        if isinstance(value, float) or isinstance(value, int):
            self.value = float(value)
            self.binary = self.float_to_ieee754(value)
        elif isinstance(value, str):
            self.binary = value.zfill(32)
            self.value = self.ieee754_to_float(value)
        else:
            raise TypeError("Поддерживаются только float/int и str")

    def float_to_ieee754(self, num):
        """Преобразование float в IEEE-754 (32 бита)"""
        num = float(num)
        if num == 0.0:
            return "0" * 32

        # Определяем знак
        sign = "0" if num >= 0 else "1"
        num = abs(num)

        # Нормализация для чисел >= 1 или < 1
        exponent = 0
        if num >= 2.0:
            while num >= 2.0:
                num /= 2.0
                exponent += 1
        elif num < 1.0:
            while num < 1.0:
                num *= 2.0
                exponent -= 1

        # Получаем мантиссу (23 бита)
        num -= 1.0  # Убираем целую часть (она всегда 1)
        mantissa = []
        for _ in range(23):
            num *= 2.0
            if num >= 1.0:
                mantissa.append("1")
                num -= 1.0
            else:
                mantissa.append("0")

        # Смещенный порядок (exponent + 127)
        biased = exponent + 127

        # Порядок в двоичный вид (8 бит)
        if biased == 0:
            exp_binary = "0" * 8
        else:
            exp_parts = []
            temp = biased
            while temp > 0:
                exp_parts.append(str(temp % 2))
                temp = temp // 2
            exp_binary = "".join(reversed(exp_parts))
            exp_binary = exp_binary.zfill(8)

        return sign + exp_binary + "".join(mantissa)

    def ieee754_to_float(self, binary):
        """Преобразование IEEE-754 в float"""
        if binary == "0" * 32:
            return 0.0

        sign = -1.0 if binary[0] == "1" else 1.0
        exp_binary = binary[1:9]
        mantissa_binary = binary[9:]

        # Порядок
        exponent = 0
        for i, bit in enumerate(exp_binary):
            if bit == "1":
                exponent += 2 ** (7 - i)
        exponent -= 127

        # Мантисса
        mantissa = 1.0
        for i, bit in enumerate(mantissa_binary):
            if bit == "1":
                mantissa += 2.0 ** (-(i + 1))

        return sign * mantissa * (2.0**exponent)

    @staticmethod
    def _binary_add(bin1, bin2):
        """Сложение двух двоичных строк произвольной длины"""
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
        # Выравниваем длины
        max_len = max(len(bin1), len(bin2))
        bin1 = bin1.zfill(max_len)
        bin2 = bin2.zfill(max_len)

        # Инвертируем bin2
        inverted = "".join("1" if b == "0" else "0" for b in bin2)

        # Прибавляем 1 для получения дополнительного кода
        one = "0" * (max_len - 1) + "1"
        neg_bin2 = BinaryFloat._binary_add(inverted, one)

        # Обрезаем до нужной длины
        if len(neg_bin2) > max_len:
            neg_bin2 = neg_bin2[-max_len:]

        # Складываем
        result = BinaryFloat._binary_add(bin1, neg_bin2)

        # Обрезаем до нужной длины
        if len(result) > max_len:
            result = result[-max_len:]

        return result

    def _align_exponents(self, exp1, mantissa1, exp2, mantissa2):
        """Выравнивание порядков для сложения"""
        e1 = int(exp1, 2)
        e2 = int(exp2, 2)

        if e1 > e2:
            # Сдвигаем мантиссу второго числа вправо на (e1 - e2) разрядов
            shift = e1 - e2
            mantissa2 = ("0" * shift) + mantissa2[:-shift] if shift <= 23 else "0" * 23
            exp = exp1
            e = e1
        elif e2 > e1:
            # Сдвигаем мантиссу первого числа вправо
            shift = e2 - e1
            mantissa1 = ("0" * shift) + mantissa1[:-shift] if shift <= 23 else "0" * 23
            exp = exp2
            e = e2
        else:
            # Порядки равны
            exp = exp1
            e = e1

        return exp, e, mantissa1, mantissa2

    def _normalize_result(self, mantissa, exp_value):
        """Нормализация результата"""
        # Находим первую единицу
        first_one = mantissa.find("1")

        if first_one == -1:  # Все нули
            return "0" * 23, exp_value

        if first_one > 0:
            # Сдвигаем влево до появления единицы в старшем разряде
            mantissa = mantissa[first_one:] + "0" * first_one
            exp_value -= first_one
        elif first_one == -1:  # Переполнение (есть единица перед мантиссой)
            mantissa = mantissa[1:] + "0"
            exp_value += 1

        return mantissa[:23], exp_value

    def __add__(self, other):
        """Сложение двух чисел IEEE-754"""
        if not isinstance(other, BinaryFloat):
            other = BinaryFloat(other)
        
        print(f"\nСЛОЖЕНИЕ IEEE-754:")
        print(f"  {self.binary}  ({self.value})")
        print(f"+ {other.binary}  ({other.value})")
        print("-" * 50)
        
        # Извлекаем компоненты
        sign1 = self.binary[0]
        sign2 = other.binary[0]
        exp1 = self.binary[1:9]
        exp2 = other.binary[1:9]
        mant1 = self.binary[9:]
        mant2 = other.binary[9:]
        
        # Проверка на нули
        if exp1 == '0' * 8 and mant1 == '0' * 23:
            return other
        if exp2 == '0' * 8 and mant2 == '0' * 23:
            return self
        
        # Добавляем скрытую единицу к мантиссе
        mant1_full = '1' + mant1
        mant2_full = '1' + mant2
        
        print(f"  Мантисса 1: {mant1_full}")
        print(f"  Мантисса 2: {mant2_full}")
        print(f"  Порядок 1: {exp1} = {int(exp1, 2)}")
        print(f"  Порядок 2: {exp2} = {int(exp2, 2)}")
        
        # Выравнивание порядков
        exp, e, mant1_aligned, mant2_aligned = self._align_exponents(
            exp1, mant1_full, exp2, mant2_full
        )
        
        print(f"  После выравнивания:")
        print(f"    Мантисса 1: {mant1_aligned}")
        print(f"    Мантисса 2: {mant2_aligned}")
        print(f"    Порядок: {exp} = {e}")
        
        # Определяем операцию на основе знаков
        if sign1 == sign2:
            # Одинаковые знаки - складываем мантиссы
            mant_sum = self._binary_add(mant1_aligned, mant2_aligned)
            result_sign = sign1
            print(f"  Сложение мантисс: {mant1_aligned} + {mant2_aligned} = {mant_sum}")
        else:
            # Разные знаки - вычитаем
            # Сравниваем мантиссы для определения знака результата
            if int(mant1_aligned, 2) > int(mant2_aligned, 2):
                mant_sum = self._binary_subtract(mant1_aligned, mant2_aligned)
                result_sign = sign1
                print(f"  Вычитание: {mant1_aligned} - {mant2_aligned} = {mant_sum}")
            elif int(mant1_aligned, 2) < int(mant2_aligned, 2):
                mant_sum = self._binary_subtract(mant2_aligned, mant1_aligned)
                result_sign = sign2
                print(f"  Вычитание: {mant2_aligned} - {mant1_aligned} = {mant_sum}")
            else:
                # Мантиссы равны - результат 0
                print(f"  Мантиссы равны - результат 0")
                return BinaryFloat(0.0)
        
        # Нормализация результата
        if mant_sum[0] == '1' and len(mant_sum) > 24:
            # Есть перенос в целую часть
            mant_sum = mant_sum[1:]  # Убираем старший бит
            e += 1
            print(f"  Перенос: порядок увеличен до {e}")
        else:
            # Убираем ведущие нули
            first_one = mant_sum.find('1')
            if first_one > 0:
                mant_sum = mant_sum[first_one:]
                e -= first_one
                print(f"  Сдвиг влево на {first_one}: порядок уменьшен до {e}")
            elif first_one == -1:
                # Все нули
                return BinaryFloat(0.0)
        
        # Получаем 23-битную мантиссу (убираем скрытую единицу)
        if len(mant_sum) > 23:
            mant_result = mant_sum[1:24]  # Убираем скрытую единицу
        elif len(mant_sum) == 24:
            mant_result = mant_sum[1:]  # Убираем скрытую единицу
        else:
            mant_result = mant_sum[1:].ljust(23, '0')
        
        # Преобразуем порядок в двоичный вид
        if e <= 0:
            exp_result = '0' * 8  # Денормализованное число
        elif e >= 255:
            exp_result = '1' * 8  # Бесконечность
        else:
            # Порядок в двоичный
            exp_parts = []
            temp = e
            while temp > 0:
                exp_parts.append(str(temp % 2))
                temp = temp // 2
            exp_result = ''.join(reversed(exp_parts))
            exp_result = exp_result.zfill(8)
        
        result_binary = result_sign + exp_result + mant_result
        result_value = self.ieee754_to_float(result_binary)
        
        print(f"\n  Результат:")
        print(f"  {result_binary}")
        print(f"  = {result_value}")
        
        return BinaryFloat(result_binary)

    def __sub__(self, other):
        """Вычитание через сложение с отрицательным числом"""
        return self + (-other)

    def __neg__(self):
        """Унарный минус - инвертируем бит знака"""
        if self.binary[0] == "0":
            return BinaryFloat("1" + self.binary[1:])
        else:
            return BinaryFloat("0" + self.binary[1:])

    def __mul__(self, other):
        """Умножение чисел IEEE-754"""
        if not isinstance(other, BinaryFloat):
            other = BinaryFloat(other)

        print(f"\nУМНОЖЕНИЕ IEEE-754:")
        print(f"  {self.binary}  ({self.value})")
        print(f"* {other.binary}  ({other.value})")
        print("-" * 50)

        # Извлекаем компоненты
        sign1 = self.binary[0]
        sign2 = other.binary[0]
        exp1 = self.binary[1:9]
        exp2 = other.binary[1:9]
        mant1 = self.binary[9:]
        mant2 = other.binary[9:]

        # Знак результата (XOR)
        result_sign = "0" if sign1 == sign2 else "1"

        # Порядки складываются (с учетом смещения 127)
        e1 = int(exp1, 2)
        e2 = int(exp2, 2)
        e_result = e1 + e2 - 127

        # Мантиссы умножаются (со скрытой единицей)
        mant1_full = "1" + mant1
        mant2_full = "1" + mant2

        # Преобразуем в целые числа для умножения (для простоты)
        # В реальной реализации нужно двоичное умножение
        m1 = int(mant1_full, 2)
        m2 = int(mant2_full, 2)
        m_result = m1 * m2

        print(f"  Мантисса 1: {mant1_full} = {m1}")
        print(f"  Мантисса 2: {mant2_full} = {m2}")
        print(f"  Произведение мантисс: {m_result}")

        # Нормализация
        if m_result >= (1 << 47):  # Если результат >= 2^47
            m_result >>= 1
            e_result += 1

        # Преобразуем обратно в двоичную мантиссу (23 бита)
        mant_result = bin(m_result)[2:].zfill(47)[1:24]  # Убираем скрытую единицу

        # Порядок в двоичный
        if e_result <= 0:
            exp_result = "0" * 8
        elif e_result >= 255:
            exp_result = "1" * 8
        else:
            exp_parts = []
            temp = e_result
            while temp > 0:
                exp_parts.append(str(temp % 2))
                temp = temp // 2
            exp_result = "".join(reversed(exp_parts))
            exp_result = exp_result.zfill(8)

        result_binary = result_sign + exp_result + mant_result
        result_value = self.ieee754_to_float(result_binary)

        print(f"\n  Результат:")
        print(f"  {result_binary}")
        print(f"  = {result_value}")

        return BinaryFloat(result_binary)

    def __truediv__(self, other):
        """Деление чисел IEEE-754"""
        if not isinstance(other, BinaryFloat):
            other = BinaryFloat(other)

        if other.value == 0:
            raise ZeroDivisionError("Деление на ноль!")

        print(f"\nДЕЛЕНИЕ IEEE-754:")
        print(f"  {self.binary}  ({self.value})")
        print(f"/ {other.binary}  ({other.value})")
        print("-" * 50)

        # Извлекаем компоненты
        sign1 = self.binary[0]
        sign2 = other.binary[0]
        exp1 = self.binary[1:9]
        exp2 = other.binary[1:9]
        mant1 = self.binary[9:]
        mant2 = other.binary[9:]

        # Знак результата (XOR)
        result_sign = "0" if sign1 == sign2 else "1"

        # Порядки вычитаются
        e1 = int(exp1, 2)
        e2 = int(exp2, 2)
        e_result = e1 - e2 + 127

        # Мантиссы делятся (со скрытой единицей)
        mant1_full = "1" + mant1
        mant2_full = "1" + mant2

        # Для деления умножаем числитель на 2^23 и делим на знаменатель
        m1 = int(mant1_full, 2) << 23
        m2 = int(mant2_full, 2)
        m_result = m1 // m2

        # Нормализация
        if m_result < (1 << 23):
            m_result <<= 1
            e_result -= 1

        # Преобразуем в двоичную мантиссу (23 бита)
        mant_result = bin(m_result)[2:].zfill(24)[1:24]

        # Порядок в двоичный
        if e_result <= 0:
            exp_result = "0" * 8
        elif e_result >= 255:
            exp_result = "1" * 8
        else:
            exp_parts = []
            temp = e_result
            while temp > 0:
                exp_parts.append(str(temp % 2))
                temp = temp // 2
            exp_result = "".join(reversed(exp_parts))
            exp_result = exp_result.zfill(8)

        result_binary = result_sign + exp_result + mant_result
        result_value = self.ieee754_to_float(result_binary)

        print(f"\n  Результат:")
        print(f"  {result_binary}")
        print(f"  = {result_value}")

        return BinaryFloat(result_binary)

    def __str__(self):
        binary_display = " ".join([self.binary[i : i + 4] for i in range(0, 32, 4)])
        return f"{binary_display} ({self.value})"

    def __repr__(self):
        return f"BinaryFloat({self.value})"
