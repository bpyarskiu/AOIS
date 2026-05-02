"""
Модуль для построения полинома Жегалкина
Использует метод треугольника (метод Паскаля по модулю 2)
"""

from typing import List, Dict, Tuple
from truth_table import TruthTable
from itertools import combinations


class ZhgPolynomial:
    """Построитель полинома Жегалкина"""

    def __init__(self, truth_table: TruthTable):
        """
        Инициализация построителя полинома Жегалкина

        Args:
            truth_table: объект TruthTable с таблицей истинности
        """
        self.tt = truth_table
        self.variables = truth_table.variables
        self.n_vars = len(self.variables)

        # Вектор значений функции (столбец f в таблице)
        self.truth_vector = truth_table.get_truth_vector_int()

        # Коэффициенты полинома Жегалкина
        self.coefficients = []

        # Список всех возможных конъюнкций переменных
        self.conjunctions = []

        # Строим полином
        self._build()

    def _build(self):
        """
        ПОСТРОЕНИЕ ПОЛИНОМА ЖЕГАЛКИНА МЕТОДОМ ТРЕУГОЛЬНИКА

        Алгоритм:
        1. Берём вектор значений функции (2^n элементов)
        2. Строим треугольник Паскаля по модулю 2
        3. Первый столбец треугольника - это коэффициенты полинома
        """

        n = len(self.truth_vector)
        triangle = [self.truth_vector[:]]

        # Строим треугольник
        current_row = self.truth_vector
        for i in range(n - 1):
            next_row = []
            for j in range(len(current_row) - 1):
                next_row.append(current_row[j] ^ current_row[j + 1])

            triangle.append(next_row)
            current_row = next_row

        # Коэффициенты - это первые элементы каждой строки
        self.coefficients = [row[0] for row in triangle]

        # Генерируем все возможные конъюнкции переменных
        self._generate_conjunctions()

    def _generate_conjunctions(self):
        """
        ГЕНЕРАЦИЯ ВСЕХ ВОЗМОЖНЫХ КОНЪЮНКЦИЙ ПЕРЕМЕННЫХ
        """
        self.conjunctions = []

        # Генерируем 2^n конъюнкций
        for i in range(2**self.n_vars):
            if i == 0:
                # Нулевой индекс - константа 1
                self.conjunctions.append("1")
            else:
                # Преобразуем индекс в двоичный вид
                binary = format(i, f"0{self.n_vars}b")

                # Собираем переменные, соответствующие единичным битам
                vars_in_conj = []
                for bit_pos, bit in enumerate(binary):
                    if bit == "1":
                        # Переменные нумеруются слева направо: a, b, c, d, e
                        vars_in_conj.append(self.variables[bit_pos])

                # Соединяем переменные через &
                self.conjunctions.append(" & ".join(vars_in_conj))

    def get_polynomial(self) -> str:
        """
        ВОЗВРАЩАЕТ ПОЛИНОМ ЖЕГАЛКИНА В ВИДЕ СТРОКИ

        Returns:
            Строка вида "1 ⊕ a ⊕ b ⊕ a&b"
            или "0" если все коэффициенты нулевые
        """
        terms = []

        # Проходим по всем коэффициентам
        for i, coeff in enumerate(self.coefficients):
            if coeff == 1:
                if i < len(self.conjunctions):
                    terms.append(self.conjunctions[i])

        # Если нет термов, функция тождественно равна 0
        if not terms:
            return "0"

        # Соединяем термы через ⊕ (XOR)
        return " ⊕ ".join(terms)

    def get_coefficients_table(self) -> str:
        """
        ВОЗВРАЩАЕТ ТАБЛИЦУ СООТВЕТСТВИЯ КОНЪЮНКЦИЙ И КОЭФФИЦИЕНТОВ

        Returns:
            Отформатированную строку с таблицей
        """
        table = []
        table.append("Конъюнкция | Коэффициент")
        table.append("-" * 30)

        for conj, coeff in zip(self.conjunctions, self.coefficients):
            # Выравниваем для красивого вывода
            table.append(f"{conj:12} | {coeff}")

        return "\n".join(table)

    def is_linear(self) -> bool:
        """
        ПРОВЕРЯЕТ, ЯВЛЯЕТСЯ ЛИ ФУНКЦИЯ ЛИНЕЙНОЙ

        Функция линейна, если в её полиноме Жегалкина:
        - Нет конъюнкций длиной > 1 (только одиночные переменные или константа)
        - Нет произведений переменных (a&b, a&b&c и т.д.)

        Returns:
            True - функция линейная
            False - функция нелинейная
        """
        for i, coeff in enumerate(self.coefficients):
            if coeff == 1:
                conj = self.conjunctions[i]
                # Считаем количество & в конъюнкции
                # Если & есть - значит это произведение переменных
                if "&" in conj:
                    return False
        return True

    def get_linear_form(self) -> str:
        """
        ВОЗВРАЩАЕТ ЛИНЕЙНУЮ ФОРМУ (если функция линейна)

        Returns:
            Строка вида "1 ⊕ a ⊕ c"
            или сообщение, что функция нелинейна
        """
        if not self.is_linear():
            return "Функция не является линейной"

        terms = []
        for i, coeff in enumerate(self.coefficients):
            if coeff == 1:
                conj = self.conjunctions[i]
                if conj == "1":
                    terms.append("1")
                else:
                    terms.append(conj)  # для линейной это только одиночные переменные

        if not terms:
            return "0"

        return " ⊕ ".join(terms)

    def find_fictitious_variables(self) -> List[str]:
        """ПОИСК ФИКТИВНЫХ ПЕРЕМЕННЫХ"""

        active_variables = set()

        for i, coeff in enumerate(self.coefficients):
            if coeff == 1:
                conj = self.conjunctions[i]

                if conj == "1":
                    continue

                # Разбиваем конъюнкцию на переменные
                vars_in_conj = [v.strip() for v in conj.split("&")]
                active_variables.update(vars_in_conj)

        all_vars = set(self.variables)
        fictitious = list(all_vars - active_variables)

        return sorted(fictitious)

    def is_variable_fictitious(self, var: str) -> bool:
        """
        ПРОВЕРЯЕТ, ЯВЛЯЕТСЯ ЛИ КОНКРЕТНАЯ ПЕРЕМЕННАЯ ФИКТИВНОЙ

        Args:
            var: имя переменной для проверки

        Returns:
            True - переменная фиктивная
            False - переменная существенная
        """
        return var in self.find_fictitious_variables()

    def get_essential_variables(self) -> List[str]:
        """
        ВОЗВРАЩАЕТ СПИСОК СУЩЕСТВЕННЫХ ПЕРЕМЕННЫХ

        Существенные переменные - те, которые реально влияют на значение функции

        Returns:
            Список существенных переменных
        """
        fictitious = set(self.find_fictitious_variables())
        all_vars = set(self.variables)
        essential = list(all_vars - fictitious)
        return sorted(essential)

    def partial_derivative_zhg(self, var: str) -> "ZhgPolynomial":
        """
        ВЫЧИСЛЕНИЕ ЧАСТНОЙ ПРОИЗВОДНОЙ ЧЕРЕЗ ПОЛИНОМ ЖЕГАЛКИНА
        """

        # Вычисляем вектор значений производной
        derivative_vector = []

        for i, (values_dict, _) in enumerate(self.tt.rows):
            # Создаём наборы с var=0 и var=1
            vals0 = values_dict.copy()
            vals0[var] = False

            vals1 = values_dict.copy()
            vals1[var] = True

            # Находим значения функции на этих наборах
            # Используем исходную функцию (через парсер)
            f0 = self._evaluate_vector(vals0)
            f1 = self._evaluate_vector(vals1)

            # Производная = f0 ⊕ f1
            derivative = f0 ^ f1
            derivative_vector.append(1 if derivative else 0)

        # Создаём новую таблицу истинности для производной
        # (упрощённо - используем существующий класс)
        derivative_tt = self._create_truth_table_from_vector(derivative_vector)

        # Возвращаем полином Жегалкина для производной
        return ZhgPolynomial(derivative_tt)

    def partial_derivative_analytic(self, var: str) -> str:
        """
        АНАЛИТИЧЕСКОЕ ВЫЧИСЛЕНИЕ ПРОИЗВОДНОЙ ЧЕРЕЗ ПОЛИНОМ ЖЕГАЛКИНА
        """

        derivative_terms = []

        for i, coeff in enumerate(self.coefficients):
            if coeff == 1:
                conj = self.conjunctions[i]

                # Проверяем, содержит ли конъюнкция переменную var
                vars_in_conj = set(conj.split(" & ")) if conj != "1" else set()

                if var in vars_in_conj:
                    # Удаляем var из конъюнкции
                    remaining_vars = [v for v in vars_in_conj if v != var]

                    if not remaining_vars:
                        # Если переменных не осталось - это константа 1
                        derivative_terms.append("1")
                    else:
                        # Иначе соединяем оставшиеся переменные через &
                        new_conj = " & ".join(sorted(remaining_vars))
                        derivative_terms.append(new_conj)

        # Суммируем по модулю 2 (XOR)
        if not derivative_terms:
            return "0"

        # Упрощаем: удаляем дубликаты (a ⊕ a = 0)
        from collections import Counter

        term_counts = Counter(derivative_terms)
        simplified_terms = [
            term for term, count in term_counts.items() if count % 2 == 1
        ]

        if not simplified_terms:
            return "0"

        return " ⊕ ".join(sorted(simplified_terms))

    def mixed_derivative_analytic(self, variables: List[str]) -> str:
        """
        АНАЛИТИЧЕСКОЕ ВЫЧИСЛЕНИЕ СМЕШАННОЙ ПРОИЗВОДНОЙ
        """

        derivative_terms = []
        vars_set = set(variables)

        for i, coeff in enumerate(self.coefficients):
            if coeff == 1:
                conj = self.conjunctions[i]

                if conj == "1":
                    continue

                vars_in_conj = set(conj.split(" & "))

                # Проверяем, содержит ли конъюнкция ВСЕ указанные переменные
                if vars_set.issubset(vars_in_conj):
                    # Удаляем все переменные из vars_set
                    remaining_vars = [v for v in vars_in_conj if v not in vars_set]

                    if not remaining_vars:
                        derivative_terms.append("1")
                    else:
                        new_conj = " & ".join(sorted(remaining_vars))
                        derivative_terms.append(new_conj)

        # Упрощаем
        if not derivative_terms:
            return "0"

        from collections import Counter

        term_counts = Counter(derivative_terms)
        simplified_terms = [
            term for term, count in term_counts.items() if count % 2 == 1
        ]

        if not simplified_terms:
            return "0"

        return " ⊕ ".join(sorted(simplified_terms))

    def _evaluate_vector(self, values_dict: Dict[str, bool]) -> bool:
        """
        ВЫЧИСЛЯЕТ ЗНАЧЕНИЕ ФУНКЦИИ НА ЗАДАННОМ НАБОРЕ

        Использует полином Жегалкина для вычисления
        """
        result = False  # Начальное значение 0

        for i, coeff in enumerate(self.coefficients):
            if coeff == 1:
                conj = self.conjunctions[i]

                if conj == "1":
                    # Константа 1
                    term_value = True
                else:
                    # Вычисляем значение конъюнкции
                    vars_in_conj = conj.split(" & ")
                    term_value = all(values_dict[v] for v in vars_in_conj)

                # XOR с текущим результатом
                result = result ^ term_value

        return result

    def _create_truth_table_from_vector(self, vector: List[int]) -> TruthTable:
        """
        СОЗДАЁТ ОБЪЕКТ TRUTHTABLE ИЗ ВЕКТОРА ЗНАЧЕНИЙ

        Это вспомогательный метод для создания производных
        """
        # Создаём фиктивный парсер (не используется)
        from logic_parser import LogicParser

        dummy_parser = LogicParser("a")  # Временно

        # Создаём таблицу истинности
        tt = TruthTable(dummy_parser)

        # Подменяем данные
        tt.vector = vector
        tt.rows = []
        for i, val in enumerate(vector):
            values_dict = {}
            for j, var in enumerate(self.variables):
                bit = (i >> (self.n_vars - 1 - j)) & 1
                values_dict[var] = bool(bit)
            tt.rows.append((values_dict, bool(val)))

        return tt

    def print_fictitious_analysis(self):
        """
        ВЫВОД АНАЛИЗА ФИКТИВНЫХ ПЕРЕМЕННЫХ
        """
        print("\n" + "=" * 50)
        print("АНАЛИЗ ФИКТИВНЫХ ПЕРЕМЕННЫХ (через полином Жегалкина)")
        print("=" * 50)

        fictitious = self.find_fictitious_variables()
        essential = self.get_essential_variables()

        print(f"\nВсе переменные: {', '.join(self.variables)}")
        print(f"Существенные: {', '.join(essential) if essential else 'нет'}")
        print(f"Фиктивные: {', '.join(fictitious) if fictitious else 'нет'}")

        if fictitious:
            print("\nПояснение:")
            print("Фиктивные переменные не входят ни в одну конъюнкцию полинома")
            print(f"Полином: {self.get_polynomial()}")

    def print_derivatives_zhg(self):
        """
        ВЫВОД ВСЕХ ПРОИЗВОДНЫХ ЧЕРЕЗ ПОЛИНОМ ЖЕГАЛКИНА
        """
        print("\n" + "=" * 50)
        print("ПРОИЗВОДНЫЕ ЧЕРЕЗ ПОЛИНОМ ЖЕГАЛКИНА")
        print("=" * 50)

        # Частные производные
        print("\nЧастные производные 1-го порядка:")
        for var in self.variables:
            deriv = self.partial_derivative_analytic(var)
            print(f"∂f/∂{var} = {deriv}")

        # Смешанные производные (если есть хотя бы 2 переменные)
        if self.n_vars >= 2:
            print("\nСмешанные производные 2-го порядка:")
            for combo in combinations(self.variables, 2):
                vars_list = list(combo)
                deriv = self.mixed_derivative_analytic(vars_list)
                vars_str = "".join(vars_list)
                print(f"∂²f/∂{vars_str} = {deriv}")

        # Третьего порядка
        if self.n_vars >= 3:
            print("\nСмешанные производные 3-го порядка:")
            for combo in combinations(self.variables, 3):
                vars_list = list(combo)
                deriv = self.mixed_derivative_analytic(vars_list)
                vars_str = "".join(vars_list)
                print(f"∂³f/∂{vars_str} = {deriv}")

    def print_polynomial(self):
        """
        КРАСИВЫЙ ВЫВОД ПОЛИНОМА ЖЕГАЛКИНА
        """
        print("=" * 50)
        print("ПОЛИНОМ ЖЕГАЛКИНА")
        print("=" * 50)

        print(f"\nВектор значений: {self.truth_vector}")
        print(f"\nПолином: f = {self.get_polynomial()}")
        print(f"\nЛинейность: {'ДА' if self.is_linear() else 'НЕТ'}")

        if self.is_linear():
            print(f"Линейная форма: f = {self.get_linear_form()}")

        print("\nТаблица коэффициентов:")
        print(self.get_coefficients_table())

    def get_triangle_visualization(self) -> str:
        """
        ВИЗУАЛИЗАЦИЯ ТРЕУГОЛЬНИКА ПАСКАЛЯ ДЛЯ ОТЛАДКИ

        Returns:
            Строка с визуализацией треугольника
        """
        n = len(self.truth_vector)
        triangle = [self.truth_vector[:]]

        current_row = self.truth_vector
        for i in range(n - 1):
            next_row = []
            for j in range(len(current_row) - 1):
                next_row.append(current_row[j] ^ current_row[j + 1])
            triangle.append(next_row)
            current_row = next_row

        result = []
        result.append("Треугольник Паскаля (mod 2):")

        # Вычисляем максимальную ширину для центрирования
        max_width = len(" ".join(map(str, triangle[0])))

        for row in triangle:
            row_str = " ".join(map(str, row))
            # Центрируем строку
            padding = (max_width - len(row_str)) // 2
            result.append(" " * padding + row_str)

        result.append("\nКоэффициенты (первый столбец):")
        result.append(str([row[0] for row in triangle]))

        return "\n".join(result)


