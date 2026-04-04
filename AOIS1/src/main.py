# main.py
#!/usr/bin/env python
"""
Консольное приложение для работы с двоичной арифметикой
Поддерживает:
- BinaryNumber (прямой, обратный, дополнительный коды)
- BinaryFloat (IEEE-754)
- BCDExcess3
"""

import sys
import os
from binary_number import BinaryNumber
from binary_float import BinaryFloat
from binary_excess3 import BCDExcess3


class BinaryCalculatorConsole:
    """Консольный калькулятор для работы с двоичными числами"""

    def __init__(self):
        self.running = True
        self.history = []

    def clear_screen(self):
        """Очистка экрана"""
        os.system("cls" if os.name == "nt" else "clear")

    def print_header(self, title):
        """Печать заголовка"""
        print("\n" + "=" * 80)
        print(f" {title} ".center(80, "="))
        print("=" * 80)

    def print_menu(self):
        """Главное меню"""
        self.clear_screen()
        print("\n" + "" * 80)
        print(" " * 25 + "ДВОИЧНЫЙ КАЛЬКУЛЯТОР")
        print("" * 80)
        print("\n    ВЫБЕРИТЕ РЕЖИМ РАБОТЫ:")
        print("─" * 80)
        print("  1 BinaryNumber - работа с целыми числами")
        print("  2 BinaryFloat - числа с плавающей точкой (IEEE-754)")
        print("  3 BCD Excess-3 - двоично-десятичный код")
        print("  0   Выход")
        print("─" * 80)

    def print_submenu(self, title):
        """Печать подменю"""
        print("\n" + "─" * 80)
        print(f"  {title}")
        print("─" * 80)
        print(" 1. Сложение (+)")
        print(" 2. Вычитание (-)")
        print(" 3. Умножение (*)")
        print(" 4. Деление (/)")
        print(" 0. Вернуться в главное меню")
        print("─" * 80)

    def get_number_input(self, prompt):
        """Получение числа с обработкой ошибок"""
        while True:
            try:
                value = input(prompt)
                return float(value) if "." in value else int(value)
            except ValueError:
                print("  Ошибка: введите корректное число!")

    def get_code_type(self):
        """Выбор типа кода для BinaryNumber"""
        print("\n    Типы кодов:")
        print("  1. Прямой код (straight)")
        print("  2. Обратный код (reverse)")
        print("  3. Дополнительный код (additional)")

        while True:
            choice = input("Выберите тип кода (1-3): ").strip()
            if choice == "1":
                return "straight"
            elif choice == "2":
                return "reverse"
            elif choice == "3":
                return "additional"
            else:
                print("  Неверный выбор. Попробуйте снова.")

    def add_to_history(self, operation, result):
        """Добавление операции в историю"""
        self.history.append({"operation": operation, "result": str(result)})
        # Ограничиваем историю 20 записями
        if len(self.history) > 20:
            self.history.pop(0)

    def show_history(self):
        """Показать историю операций"""
        self.print_header("ИСТОРИЯ ОПЕРАЦИЙ")
        if not self.history:
            print("\n История пуста. Выполните несколько операций.")
        else:
            print("\n    Последние операции:")
            print("─" * 80)
            for i, entry in enumerate(self.history[-10:], 1):
                print(f"  {i}. {entry['operation']}")
                print(f"     → {entry['result']}")
            print("─" * 80)

        input("\nНажмите Enter для продолжения...")

    # ============== BinaryNumber режим ==============

    def run_binary_number_mode(self):
        """Режим работы с BinaryNumber"""
        while True:
            self.print_header("BINARYNUMBER - ЦЕЛЫЕ ЧИСЛА")

            print("\n    Сначала создайте число:")
            try:
                value = int(input("Введите целое число: "))
                code_type = self.get_code_type()
                num = BinaryNumber(value, code_type)

                print(f"\n    Создано число: {num}")
                print(f"   Десятичное: {num.value}")
                print(f"   Двоичное: {num.to_binary_string()}")
                print(f"   Тип кода: {code_type}")
            except Exception as e:
                print(f"\n  Ошибка: {e}")
                input("\nНажмите Enter для продолжения...")
                continue

            self.print_submenu(f"Работа с числом: {num.value}")
            choice = input("\nВыберите операцию (0-9): ").strip()

            if choice == "0":
                break

            try:
                if choice == "1":  # Сложение
                    val2 = int(input("Введите второе число: "))
                    code2 = self.get_code_type()
                    num2 = BinaryNumber(val2, code2)
                    result = num + num2
                    op_str = f"{num.value} + {num2.value} = {result.value}"
                    print(f"\n   Результат: {result}")
                    self.add_to_history(op_str, result)

                elif choice == "2":  # Вычитание
                    val2 = int(input("Введите второе число: "))
                    code2 = self.get_code_type()
                    num2 = BinaryNumber(val2, code2)
                    result = num - num2
                    op_str = f"{num.value} - {num2.value} = {result.value}"
                    print(f"\n   Результат: {result}")
                    self.add_to_history(op_str, result)

                elif choice == "3":  # Умножение
                    val2 = int(input("Введите второе число: "))
                    code2 = self.get_code_type()
                    num2 = BinaryNumber(val2, code2)
                    result = num * num2
                    op_str = f"{num.value} * {num2.value} = {result.value}"
                    print(f"\n   Результат: {result}")
                    self.add_to_history(op_str, result)

                elif choice == "4":  # Деление
                    val2 = int(input("Введите второе число: "))
                    code2 = self.get_code_type()
                    num2 = BinaryNumber(val2, code2)
                    try:
                        result = num / num2
                        op_str = f"{num.value} / {num2.value} = {result.value}"
                        print(f"\n   Результат (целая часть): {result}")
                        self.add_to_history(op_str, result)
                    except ZeroDivisionError:
                        print("\n  Ошибка: деление на ноль!")

                elif choice == "5":  # Унарный минус
                    result = -num
                    op_str = f"-({num.value}) = {result.value}"
                    print(f"\n   Результат: {result}")
                    self.add_to_history(op_str, result)

                elif choice == "6":  # Модуль
                    result = abs(num)
                    op_str = f"|{num.value}| = {result.value}"
                    print(f"\n   Результат: {result}")
                    self.add_to_history(op_str, result)

                elif choice == "7":  # Сравнение
                    val2 = int(input("Введите второе число: "))
                    code2 = self.get_code_type()
                    num2 = BinaryNumber(val2, code2)
                    print(f"\n   Сравнение {num.value} и {num2.value}:")
                    print(f"   {num.value} == {num2.value}: {num == num2}")
                    print(f"   {num.value} != {num2.value}: {num != num2}")
                    print(f"   {num.value} <  {num2.value}: {num < num2}")
                    print(f"   {num.value} >  {num2.value}: {num > num2}")
                    op_str = f"Сравнение {num.value} и {num2.value}"
                    self.add_to_history(op_str, f"{num == num2}, {num < num2}")

                elif choice == "8":  # Показать представление
                    print(f"\n   ПРЕДСТАВЛЕНИЕ ЧИСЛА {num.value}:")
                    print(f"   Текущий код ({num.code_type}): {num.to_binary_string()}")

                    # Показываем в других кодах
                    if num.code_type != "straight":
                        print(
                            f"   Прямой код: {num.to_code('straight').to_binary_string()}"
                        )
                    if num.code_type != "reverse":
                        print(
                            f"   Обратный код: {num.to_code('reverse').to_binary_string()}"
                        )
                    if num.code_type != "additional":
                        print(
                            f"   Дополнительный код: {num.to_code('additional').to_binary_string()}"
                        )

                    op_str = f"Представление числа {num.value}"
                    self.add_to_history(op_str, num.to_binary_string())

                elif choice == "9":  # Преобразовать в другой код
                    new_code = self.get_code_type()
                    result = num.to_code(new_code)
                    print(f"\n🔄 Преобразовано в {new_code} код:")
                    print(f"   {result}")
                    op_str = (
                        f"Преобразование {num.value} из {num.code_type} в {new_code}"
                    )
                    self.add_to_history(op_str, result)

                else:
                    print("\n  Неверный выбор!")

            except Exception as e:
                print(f"\n  Ошибка: {e}")

            input("\nНажмите Enter для продолжения...")

    # ============== BinaryFloat режим ==============

    def run_binary_float_mode(self):
        """Режим работы с BinaryFloat"""
        while True:
            self.print_header("BINARYFLOAT - ЧИСЛА С ПЛАВАЮЩЕЙ ТОЧКОЙ (IEEE-754)")

            print("\n    Сначала создайте число:")
            try:
                value = float(input("Введите число с плавающей точкой: "))
                num = BinaryFloat(value)

                print(f"\n    Создано число: {num}")
                print(f"   Десятичное: {num.value}")
            except Exception as e:
                print(f"\n  Ошибка: {e}")
                input("\nНажмите Enter для продолжения...")
                continue

            self.print_submenu(f"Работа с числом: {num.value}")
            choice = input("\nВыберите операцию (0-9): ").strip()

            if choice == "0":
                break

            try:
                if choice == "1":  # Сложение
                    val2 = float(input("Введите второе число: "))
                    num2 = BinaryFloat(val2)
                    result = num + num2
                    op_str = f"{num.value} + {num2.value} = {result.value}"
                    print(f"\n   Результат: {result}")
                    self.add_to_history(op_str, result)

                elif choice == "2":  # Вычитание
                    val2 = float(input("Введите второе число: "))
                    num2 = BinaryFloat(val2)
                    result = num - num2
                    op_str = f"{num.value} - {num2.value} = {result.value}"
                    print(f"\n   Результат: {result}")
                    self.add_to_history(op_str, result)

                elif choice == "3":  # Умножение
                    val2 = float(input("Введите второе число: "))
                    num2 = BinaryFloat(val2)
                    result = num * num2
                    op_str = f"{num.value} * {num2.value} = {result.value}"
                    print(f"\n   Результат: {result}")
                    self.add_to_history(op_str, result)

                elif choice == "4":  # Деление
                    val2 = float(input("Введите второе число: "))
                    num2 = BinaryFloat(val2)
                    try:
                        result = num / num2
                        op_str = f"{num.value} / {num2.value} = {result.value}"
                        print(f"\n   Результат: {result}")
                        self.add_to_history(op_str, result)
                    except ZeroDivisionError:
                        print("\n  Ошибка: деление на ноль!")

                elif choice == "5":  # Унарный минус
                    result = -num
                    op_str = f"-({num.value}) = {result.value}"
                    print(f"\n   Результат: {result}")
                    self.add_to_history(op_str, result)

                elif choice == "6":  # Модуль
                    result = abs(num)
                    op_str = f"|{num.value}| = {result.value}"
                    print(f"\n   Результат: {result}")
                    self.add_to_history(op_str, result)

                elif choice == "8":  # Показать представление
                    print(f"\n   IEEE-754 ПРЕДСТАВЛЕНИЕ:")
                    print(f"   {num}")
                    print(f"   Двоичная строка: {num.binary}")
                    print(f"   Группировка: {num.to_binary_string()}")
                    op_str = f"Представление числа {num.value} в IEEE-754"
                    self.add_to_history(op_str, num.to_binary_string())

                else:
                    print("\n  Неверный выбор!")

            except Exception as e:
                print(f"\n  Ошибка: {e}")

            input("\nНажмите Enter для продолжения...")

    # ============== BCD Excess-3 режим ==============

    def run_bcd_mode(self):
        """Режим работы с BCD Excess-3"""
        while True:
            self.print_header("BCD EXCESS-3 - ДВОИЧНО-ДЕСЯТИЧНЫЙ КОД")

            print("\n    Сначала создайте число:")
            try:
                value = int(input("Введите неотрицательное целое число: "))
                if value < 0:
                    print("  BCD Excess-3 поддерживает только неотрицательные числа!")
                    input("\nНажмите Enter для продолжения...")
                    continue
                num = BCDExcess3(value)

                print(f"\n    Создано число: {num}")
                print(f"   Десятичное: {num.value}")
                print(f"   BCD Excess-3: {num.to_str()}")
            except OverflowError:
                print(f"\n  Ошибка: число слишком большое! Максимум: {10**8 - 1}")
                input("\nНажмите Enter для продолжения...")
                continue
            except Exception as e:
                print(f"\n  Ошибка: {e}")
                input("\nНажмите Enter для продолжения...")
                continue

            self.print_submenu(f"Работа с числом: {num.value}")
            choice = input("\nВыберите операцию (0-9): ").strip()

            if choice == "0":
                break

            try:
                if choice == "1":  # Сложение
                    val2 = int(input("Введите второе число: "))
                    num2 = BCDExcess3(val2)
                    result = num + num2
                    op_str = f"{num.value} + {num2.value} = {result.value}"
                    print(f"\n   Результат: {result}")
                    self.add_to_history(op_str, result)

                elif choice == "2":  # Вычитание
                    val2 = int(input("Введите второе число: "))
                    num2 = BCDExcess3(val2)
                    try:
                        result = num - num2
                        op_str = f"{num.value} - {num2.value} = {result.value}"
                        print(f"\n   Результат: {result}")
                        self.add_to_history(op_str, result)
                    except ValueError as e:
                        print(f"\n  {e}")

                elif choice == "3":  # Умножение
                    val2 = int(input("Введите второе число: "))
                    num2 = BCDExcess3(val2)
                    result = num * num2
                    op_str = f"{num.value} * {num2.value} = {result.value}"
                    print(f"\n   Результат: {result}")
                    self.add_to_history(op_str, result)

                elif choice == "8":  # Показать представление
                    print(f"\n   BCD EXCESS-3 ПРЕДСТАВЛЕНИЕ:")
                    print(f"   {num}")
                    print(f"   Детальный вывод:")
                    num.print_nibbles()
                    op_str = f"Представление числа {num.value} в BCD Excess-3"
                    self.add_to_history(op_str, num.to_str())

                else:
                    print("\n  Неверный выбор!")

            except Exception as e:
                print(f"\n  Ошибка: {e}")

            input("\nНажмите Enter для продолжения...")

    # ============== Демонстрация ==============

    def run_demo(self):
        """Демонстрация всех возможностей"""
        self.print_header("ДЕМОНСТРАЦИЯ ВСЕХ РЕЖИМОВ")

        print("\n 1. BINARYNUMBER - работа с целыми числами")
        print("─" * 80)

        # BinaryNumber демо
        a = BinaryNumber(5, "straight")
        b = BinaryNumber(3, "additional")
        print(f"   a = {a}")
        print(f"   b = {b}")
        print(f"   a + b = {a + b}  (5 + 3 = 8)")
        print(f"   a - b = {a - b}  (5 - 3 = 2)")
        print(f"   a * b = {a * b}  (5 * 3 = 15)")
        print(f"   a / b = {a / b}  (5 / 3 = 1)")

        print("\n 2. BINARYFLOAT - числа с плавающей точкой")
        print("─" * 80)

        # BinaryFloat демо
        f1 = BinaryFloat(5.75)
        f2 = BinaryFloat(2.25)
        print(f"   f1 = {f1}")
        print(f"   f2 = {f2}")
        print(f"   f1 + f2 = {f1 + f2}  (5.75 + 2.25 = 8.0)")
        print(f"   f1 - f2 = {f1 - f2}  (5.75 - 2.25 = 3.5)")
        print(f"   f1 * f2 = {f1 * f2}  (5.75 * 2.25 = 12.9375)")
        print(f"   f1 / f2 = {f1 / f2}  (5.75 / 2.25 = 2.555...)")

        print("\n 3. BCD EXCESS-3 - двоично-десятичный код")
        print("─" * 80)

        # BCD демо
        bcd1 = BCDExcess3(78)
        bcd2 = BCDExcess3(45)
        print(f"   bcd1 = {bcd1}")
        print(f"   bcd2 = {bcd2}")
        print(f"   bcd1 + bcd2 = {bcd1 + bcd2}  (78 + 45 = 123)")
        print(f"   bcd1 - bcd2 = {bcd1 - bcd2}  (78 - 45 = 33)")

        print("\n 4. ДОПОЛНИТЕЛЬНЫЕ ВОЗМОЖНОСТИ")
        print("─" * 80)

        # Демо преобразования кодов
        num = BinaryNumber(-5, "straight")
        print(f"   Число: {num}")
        print(f"   Прямой код: {num.to_binary_string()}")
        print(f"   Обратный код: {num.to_code('reverse').to_binary_string()}")
        print(f"   Дополнительный код: {num.to_code('additional').to_binary_string()}")

        # Демо сравнения
        print(f"\n   Сравнение: 5 > 3? {BinaryNumber(5) > BinaryNumber(3)}")

        # Демо специальных значений IEEE-754
        print(f"\n   IEEE-754: ноль = {BinaryFloat(0.0)}")
        print(f"   IEEE-754: единица = {BinaryFloat(1.0)}")

        input("\n\nНажмите Enter для продолжения...")

    # ============== Главный цикл ==============

    def run(self):
        """Главный цикл приложения"""
        while self.running:
            self.print_menu()
            choice = input("\nВведите номер режима (0-5): ").strip()

            if choice == "1":
                self.run_binary_number_mode()
            elif choice == "2":
                self.run_binary_float_mode()
            elif choice == "3":
                self.run_bcd_mode()
            elif choice == "4":
                self.show_history()
            elif choice == "5":
                self.run_demo()
            elif choice == "0":
                self.print_header("ДО СВИДАНИЯ!")
                print("\n   Спасибо за использование Binary Calculator!")
                print("   Разработано в рамках курса АОИС\n")
                self.running = False
            else:
                print("\n Неверный выбор! Пожалуйста, выберите 0-5.")
                input("\nНажмите Enter для продолжения...")


# Точка входа
if __name__ == "__main__":
    try:
        app = BinaryCalculatorConsole()
        app.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\n Непредвиденная ошибка: {e}")
        print("Перезапустите программу.")
