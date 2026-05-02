"""
Модуль для вычисления булевых производных
ИСПОЛЬЗУЕТ ПОЛИНОМ ЖЕГАЛКИНА ДЛЯ ЭФФЕКТИВНЫХ ВЫЧИСЛЕНИЙ
"""

from typing import List, Dict
from logic_parser import LogicParser
from truth_table import TruthTable
from zhg_polynomial import ZhgPolynomial
from itertools import combinations


class BooleanDerivative:
    """Вычислитель булевых производных (использует полином Жегалкина)"""

    def __init__(self, parser: LogicParser, truth_table: TruthTable):
        """
        Инициализация с использованием полинома Жегалкина
        """
        self.parser = parser
        self.tt = truth_table
        self.variables = truth_table.variables
        self.n_vars = len(self.variables)

        # Главное изменение: используем полином Жегалкина для вычислений
        self.zhg = ZhgPolynomial(truth_table)

    def partial_derivative(self, var: str) -> str:
        """
        Частная производная через полином Жегалкина
        """
        return self.zhg.partial_derivative_analytic(var)

    def mixed_derivative(self, variables: List[str]) -> str:
        """
        Смешанная производная через полином Жегалкина
        """
        return self.zhg.mixed_derivative_analytic(variables)

    def print_derivatives(self):
        """
        Вывод всех производных
        """
        self.zhg.print_derivatives_zhg()
