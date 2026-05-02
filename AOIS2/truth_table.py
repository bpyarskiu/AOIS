"""
Модуль для построения таблиц истинности
"""

from itertools import product
from typing import List, Dict, Tuple
from logic_parser import LogicParser


class TruthTable:
    """Генератор и хранилище таблицы истинности"""

    def __init__(self, parser: LogicParser):
        """
        Args:
            parser: объект LogicParser с распарсенным выражением
        """
        self.parser = parser
        self.variables = parser.get_variables()
        self.n_vars = len(self.variables)

        # Строим таблицу
        self.rows: List[Tuple[Dict[str, bool], bool]] = []
        self._build()

    def _build(self):
        """Построение таблицы истинности"""
        # Генерируем все возможные комбинации значений переменных
        for bool_values in product([False, True], repeat=self.n_vars):
            values_dict = dict(zip(self.variables, bool_values))
            result = self.parser.evaluate(values_dict)
            self.rows.append((values_dict, result))

    def get_truth_vector(self) -> List[bool]:
        """Возвращает вектор значений функции"""
        return [result for _, result in self.rows]

    def get_truth_vector_int(self) -> List[int]:
        """Возвращает вектор значений функции в виде 0/1"""
        return [1 if result else 0 for _, result in self.rows]

    def print_table(self):
        """Красивый вывод таблицы истинности"""
        # Заголовок
        header = " ".join(self.variables) + " | f"
        print(header)
        print("-" * len(header))

        # Строки таблицы
        for values_dict, result in self.rows:
            row = " ".join(str(int(values_dict[var])) for var in self.variables)
            row += f" | {int(result)}"
            print(row)

    def get_row_by_number(self, num: int) -> Tuple[Dict[str, bool], bool]:
        """
        Получает строку таблицы по десятичному номеру набора

        Args:
            num: десятичный номер набора (от 0 до 2^n - 1)
        """
        return self.rows[num]

    def get_minterms(self) -> List[int]:
        """Возвращает номера наборов, где функция равна 1 (минтермы)"""
        return [i for i, (_, result) in enumerate(self.rows) if result]

    def get_maxterms(self) -> List[int]:
        """Возвращает номера наборов, где функция равна 0 (макстермы)"""
        return [i for i, (_, result) in enumerate(self.rows) if not result]



