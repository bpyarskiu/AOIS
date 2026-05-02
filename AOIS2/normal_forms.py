"""
Модуль для построения СДНФ, СКНФ, числовых и индексных форм
"""

from typing import List, Tuple
from truth_table import TruthTable


class NormalForms:
    """Построитель нормальных форм"""

    def __init__(self, truth_table: TruthTable):
        self.tt = truth_table
        self.variables = truth_table.variables
        self.n_vars = len(self.variables)

        # Строим все формы
        self._build()

    def _build(self):
        """Построение всех нормальных форм"""
        self.sdnf_terms = []  # Термы СДНФ (строки)
        self.sknf_terms = []  # Термы СКНФ (строки)
        self.sdnf_numbers = []  # Числовая форма СДНФ
        self.sknf_numbers = []  # Числовая форма СКНФ

        for i, (values_dict, result) in enumerate(self.tt.rows):
            if result:  # f = 1 -> СДНФ
                self.sdnf_numbers.append(i)
                term = self._build_conjunction(values_dict, positive=True)
                self.sdnf_terms.append(term)
            else:  # f = 0 -> СКНФ
                self.sknf_numbers.append(i)
                term = self._build_disjunction(values_dict, positive=False)
                self.sknf_terms.append(term)

    def _build_conjunction(self, values_dict: dict, positive: bool = True) -> str:
        """
        Строит элементарную конъюнкцию

        Args:
            values_dict: значения переменных
            positive: True - переменная без отрицания если 1, False - если 0
        """
        literals = []
        for var in self.variables:
            val = values_dict[var]
            if positive:
                # В СДНФ: если 1 -> переменная, если 0 -> отрицание
                literals.append(var if val else f"!{var}")
            else:
                # В СКНФ: если 0 -> переменная, если 1 -> отрицание
                literals.append(var if not val else f"!{var}")

        return f"({' & '.join(literals)})"

    def _build_disjunction(self, values_dict: dict, positive: bool = False) -> str:
        """
        Строит элементарную дизъюнкцию
        """
        literals = []
        for var in self.variables:
            val = values_dict[var]
            if positive:
                literals.append(var if val else f"!{var}")
            else:
                # В СКНФ: если 0 -> переменная, если 1 -> отрицание
                literals.append(var if not val else f"!{var}")

        return f"({' | '.join(literals)})"

    def get_sdnf(self) -> str:
        """Возвращает строку с СДНФ"""
        if not self.sdnf_terms:
            return "0"
        return " | ".join(self.sdnf_terms)

    def get_sknf(self) -> str:
        """Возвращает строку с СКНФ"""
        if not self.sknf_terms:
            return "1"
        return " & ".join(self.sknf_terms)

    def get_sdnf_numeric(self) -> str:
        """Числовая форма СДНФ: V(1,3,5,7)"""
        if not self.sdnf_numbers:
            return "Nah"
        return f"∨({','.join(map(str, self.sdnf_numbers))})"

    def get_sknf_numeric(self) -> str:
        """Числовая форма СКНФ: Λ(0,2,4,6)"""
        if not self.sknf_numbers:
            return "Nah"
        return f"∧({','.join(map(str, self.sknf_numbers))})"

    def get_index_form(self) -> int:
        """
        Индексная форма функции - десятичное число, соответствующее
        вектору значений (старший бит - последний набор)
        """
        return int(self.get_index_form_binary(), 2)

    def get_index_form_binary(self) -> str:
        """Индексная форма в двоичном виде"""
        vector = self.tt.get_truth_vector_int()
        return "".join(map(str, reversed(vector)))

    def print_all(self):
        """Вывод всех форм"""
        print("=" * 50)
        print("НОРМАЛЬНЫЕ ФОРМЫ")
        print("=" * 50)

        print(f"\nСДНФ: f = {self.get_sdnf()}")
        print(f"Числовая форма СДНФ: {self.get_sdnf_numeric()}")

        print(f"\nСКНФ: f = {self.get_sknf()}")
        print(f"Числовая форма СКНФ: {self.get_sknf_numeric()}")

        print(f"\nИндексная форма:")
        print(f"  Двоичная: {self.get_index_form_binary()}")
        print(f"  Десятичная: {self.get_index_form()}")


