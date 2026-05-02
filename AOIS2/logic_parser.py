"""
Модуль для парсинга и вычисления логических выражений.
Поддерживает операции: &, |, !, ->, ~, а также скобки.
Переменные: a, b, c, d, e (до 5)
"""

import re
from typing import Dict, Set, List, Callable


class LogicParser:
    """Парсер логических выражений с поддержкой стандартных операций"""

    # Приоритеты операций (чем больше число, тем выше приоритет)
    PRECEDENCE = {
        "!": 5,  # НЕ (наивысший)
        "&": 4,  # И
        "|": 3,  # ИЛИ
        "->": 2,  # Импликация
        "~": 1,  # Эквивалентность (наинизший)
    }

    def __init__(self, expression: str):
        """
        Инициализация парсера

        Args:
            expression: строка с логическим выражением
            Например: "!(!a->!b) | c" или "a & b -> c"
        """
        self.original = expression
        self.variables: Set[str] = set()
        self._postfix: List[str] = []
        self._parse()

    def _tokenize(self, expr: str) -> List[str]:
        """Разбивает выражение на токены"""
        # Удаляем все пробелы
        expr = re.sub(r"\s+", "", expr)

        # Заменяем операции на стандартные токены
        # Импликацию и эквивалентность обрабатываем особо
        expr = expr.replace("->", " → ")
        expr = expr.replace("~", " ~ ")

        # Разбиваем на токены
        tokens = []
        i = 0
        while i < len(expr):
            if expr[i] in "abcde":  # переменные
                self.variables.add(expr[i])
                tokens.append(expr[i])
                i += 1
            elif expr[i] in "!&|()":
                tokens.append(expr[i])
                i += 1
            elif expr[i] == "→":  # импликация
                tokens.append("->")
                i += 1
            elif expr[i] == "~":  # эквивалентность
                tokens.append("~")
                i += 1
            else:
                i += 1  # пропускаем пробелы

        return tokens

    def _to_postfix(self, tokens: List[str]) -> List[str]:
        """Преобразует инфиксную запись в постфиксную (обратную польскую)"""
        output = []
        stack = []

        for token in tokens:
            if token in self.variables:
                output.append(token)
            elif token == "(":
                stack.append(token)
            elif token == ")":
                while stack and stack[-1] != "(":
                    output.append(stack.pop())
                stack.pop()  # убираем '('
            elif token in self.PRECEDENCE:
                while (
                    stack
                    and stack[-1] != "("
                    and self.PRECEDENCE.get(stack[-1], 0) >= self.PRECEDENCE[token]
                ):
                    output.append(stack.pop())
                stack.append(token)

        # Выталкиваем оставшиеся операторы
        while stack:
            output.append(stack.pop())

        return output

    def _parse(self):
        """Полный парсинг выражения"""
        tokens = self._tokenize(self.original)
        self._postfix = self._to_postfix(tokens)

    def evaluate(self, values: Dict[str, bool]) -> bool:
        """
        Вычисляет значение функции при заданных значениях переменных

        Args:
            values: словарь вида {'a': True, 'b': False, 'c': True}

        Returns:
            bool: результат вычисления
        """
        stack = []

        # Операции
        ops = {
            "!": lambda x: not x,
            "&": lambda x, y: x and y,
            "|": lambda x, y: x or y,
            "->": lambda x, y: (not x) or y,  # a -> b = !a | b
            "~": lambda x, y: x == y,  # a ~ b = a == b
        }

        for token in self._postfix:
            if token in self.variables:
                stack.append(values[token])
            elif token == "!":
                stack.append(ops[token](stack.pop()))
            elif token in ["&", "|", "->", "~"]:
                b = stack.pop()
                a = stack.pop()
                stack.append(ops[token](a, b))

        return stack[0]

    def get_variables(self) -> List[str]:
        """Возвращает отсортированный список переменных"""
        return sorted(list(self.variables))

    def __str__(self):
        return f"LogicParser('{self.original}')"
