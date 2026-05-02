"""
Модуль для проверки принадлежности функции к классам Поста:
T0, T1, S, M, L
"""

from typing import List, Dict, Tuple
from truth_table import TruthTable


class PostClasses:
    """Проверка принадлежности к классам Поста"""

    def __init__(self, truth_table: TruthTable):
        self.tt = truth_table
        self.variables = truth_table.variables
        self.n_vars = len(self.variables)
        self.vector = truth_table.get_truth_vector_int()

        self.classes = {
            "T0": self.check_T0(),
            "T1": self.check_T1(),
            "S": self.check_S(),
            "M": self.check_M(),
            "L": self.check_L(),
        }

    def check_T0(self) -> bool:
        """
        Класс T0 - функции, сохраняющие 0
        f(0,0,...,0) = 0
        """
        return self.vector[0] == 0

    def check_T1(self) -> bool:
        """
        Класс T1 - функции, сохраняющие 1
        f(1,1,...,1) = 1
        """
        return self.vector[-1] == 1

    def check_S(self) -> bool:
        """
        Класс S - самодвойственные функции
        f(x1,...,xn) = !f(!x1,...,!xn)
        """
        n = len(self.vector)
        for i in range(n):
            # Противоположный набор: инвертируем все биты индекса
            opposite_idx = n - 1 - i
            if self.vector[i] == self.vector[opposite_idx]:
                return False
        return True

    def check_M(self) -> bool:
        """
        Класс M - монотонные функции
        Для любых наборов α ≤ β должно быть f(α) ≤ f(β)
        """
        n = len(self.vector)

        # Функция проверки: α ≤ β (побитовое сравнение)
        def less_or_equal(idx1: int, idx2: int) -> bool:
            """Проверяет, что набор idx1 ≤ набор idx2"""
            for bit in range(self.n_vars):
                # Извлекаем биты из индексов
                bit1 = (idx1 >> (self.n_vars - 1 - bit)) & 1
                bit2 = (idx2 >> (self.n_vars - 1 - bit)) & 1
                if bit1 > bit2:
                    return False
            return True

        # Проверяем монотонность
        for i in range(n):
            for j in range(n):
                if less_or_equal(i, j):
                    if self.vector[i] > self.vector[j]:
                        return False
        return True

    def check_L(self) -> bool:
        """
        Класс L - линейные функции
        Функция линейна, если представляется в виде: a0 ⊕ a1x1 ⊕ ... ⊕ anxn
        Проверяем через полином Жегалкина (без нелинейных конъюнкций)
        """
        from zhg_polynomial import ZhgPolynomial

        zhg = ZhgPolynomial(self.tt)
        return zhg.is_linear()

    def is_complete_system(self) -> bool:
        """
        Проверяет, является ли функция полной системой (критерий Поста)
        Для полноты функция не должна принадлежать всем 5 классам одновременно
        """
        classes = [
            self.classes["T0"],
            self.classes["T1"],
            self.classes["S"],
            self.classes["M"],
            self.classes["L"],
        ]
        return not all(classes)

    def print_report(self):
        """Вывод отчета о принадлежности классам Поста"""
        print("\n" + "=" * 50)
        print("КЛАССЫ ПОСТА")
        print("=" * 50)

        class_names = {
            "T0": "Сохранение 0",
            "T1": "Сохранение 1",
            "S": "Самодвойственность",
            "M": "Монотонность",
            "L": "Линейность",
        }

        for class_key, belongs in self.classes.items():
            status = "✓ ПРИНАДЛЕЖИТ" if belongs else "✗ НЕ принадлежит"
            print(f"{class_key} ({class_names[class_key]}): {status}")

        print(f"\nСистема {'ПОЛНА' if self.is_complete_system() else 'НЕ полна'}")

    def get_missing_classes(self):
        listed = []
        for class_key, belongs in self.classes.items():
            if not belongs:
                listed.append(class_key)
        return listed


