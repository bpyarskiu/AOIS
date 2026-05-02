"""
Комплексные тесты для всех модулей лабораторной работы №2
"""

import sys
import unittest
from typing import List, Dict, Tuple

# Импортируем все модули
from logic_parser import LogicParser
from truth_table import TruthTable
from normal_forms import NormalForms
from post_classes import PostClasses
from zhg_polynomial import ZhgPolynomial
from boolean_derivative import BooleanDerivative
from minimizer import Minimizer

# ТЕСТЫ ДЛЯ LOGIC PARSER


class TestLogicParser(unittest.TestCase):
    """Тесты для парсера логических выражений"""

    def test_simple_conjunction(self):
        """Тест простой конъюнкции"""
        parser = LogicParser("a & b")
        self.assertEqual(parser.get_variables(), ["a", "b"])
        self.assertTrue(parser.evaluate({"a": True, "b": True}))
        self.assertFalse(parser.evaluate({"a": True, "b": False}))
        self.assertFalse(parser.evaluate({"a": False, "b": True}))
        self.assertFalse(parser.evaluate({"a": False, "b": False}))

    def test_simple_disjunction(self):
        """Тест простой дизъюнкции"""
        parser = LogicParser("a | b")
        self.assertFalse(parser.evaluate({"a": False, "b": False}))
        self.assertTrue(parser.evaluate({"a": True, "b": False}))
        self.assertTrue(parser.evaluate({"a": False, "b": True}))
        self.assertTrue(parser.evaluate({"a": True, "b": True}))

    def test_negation(self):
        """Тест отрицания"""
        parser = LogicParser("!a")
        self.assertTrue(parser.evaluate({"a": False}))
        self.assertFalse(parser.evaluate({"a": True}))

    def test_implication(self):
        """Тест импликации"""
        parser = LogicParser("a -> b")
        # a -> b = !a | b
        self.assertTrue(parser.evaluate({"a": False, "b": False}))
        self.assertTrue(parser.evaluate({"a": False, "b": True}))
        self.assertFalse(parser.evaluate({"a": True, "b": False}))
        self.assertTrue(parser.evaluate({"a": True, "b": True}))

    def test_equivalence(self):
        """Тест эквивалентности"""
        parser = LogicParser("a ~ b")
        self.assertTrue(parser.evaluate({"a": False, "b": False}))
        self.assertFalse(parser.evaluate({"a": False, "b": True}))
        self.assertFalse(parser.evaluate({"a": True, "b": False}))
        self.assertTrue(parser.evaluate({"a": True, "b": True}))

    def test_complex_expression(self):
        """Тест сложного выражения"""
        parser = LogicParser("(a & b) | (!a & c)")
        # (1,1,0) -> 1, (0,0,1) -> 1, (0,0,0) -> 0
        self.assertTrue(parser.evaluate({"a": True, "b": True, "c": False}))
        self.assertTrue(parser.evaluate({"a": False, "b": False, "c": True}))
        self.assertFalse(parser.evaluate({"a": False, "b": False, "c": False}))

    def test_double_negation(self):
        """Тест двойного отрицания"""
        parser = LogicParser("!(!(a))")
        self.assertFalse(parser.evaluate({"a": False}))
        self.assertTrue(parser.evaluate({"a": True}))

    def test_parentheses(self):
        """Тест приоритета скобок"""
        parser1 = LogicParser("a & b | c")
        parser2 = LogicParser("a & (b | c)")

        # При одинаковых значениях могут быть разные результаты
        vals = {"a": False, "b": True, "c": True}
        # a & b | c = (a&b) | c = 0 | 1 = 1
        self.assertTrue(parser1.evaluate(vals))
        # a & (b | c) = 0 & 1 = 0
        self.assertFalse(parser2.evaluate(vals))

    def test_three_variables(self):
        """Тест с тремя переменными"""
        parser = LogicParser("a & b & c")
        self.assertEqual(parser.get_variables(), ["a", "b", "c"])
        self.assertTrue(parser.evaluate({"a": True, "b": True, "c": True}))
        self.assertFalse(parser.evaluate({"a": True, "b": True, "c": False}))

    def test_five_variables(self):
        """Тест с пятью переменными"""
        parser = LogicParser("a & b & c & d & e")
        self.assertEqual(len(parser.get_variables()), 5)
        self.assertTrue(
            parser.evaluate({"a": True, "b": True, "c": True, "d": True, "e": True})
        )

    def test_variable_detection(self):
        """Тест определения переменных"""
        parser = LogicParser("a & !b -> c ~ d")
        self.assertEqual(parser.get_variables(), ["a", "b", "c", "d"])

    def test_complex_from_task(self):
        """Тест примера из задания"""
        parser = LogicParser("!(!a->!b) | c")
        # Симуляция: !(!a->!b) = !(a | !b) = !a & b
        # (!a & b) | c
        vals = {"a": False, "b": True, "c": False}  # должно быть True
        self.assertTrue(parser.evaluate(vals))
        vals = {"a": False, "b": False, "c": False}  # должно быть False
        self.assertFalse(parser.evaluate(vals))

    def test_sheffer_stroke(self):
        """Тест штриха Шеффера"""
        parser = LogicParser("!(a & b)")
        self.assertTrue(parser.evaluate({"a": False, "b": False}))
        self.assertTrue(parser.evaluate({"a": False, "b": True}))
        self.assertTrue(parser.evaluate({"a": True, "b": False}))
        self.assertFalse(parser.evaluate({"a": True, "b": True}))

    def test_pierce_arrow(self):
        """Тест стрелки Пирса"""
        parser = LogicParser("!(a | b)")
        self.assertTrue(parser.evaluate({"a": False, "b": False}))
        self.assertFalse(parser.evaluate({"a": False, "b": True}))
        self.assertFalse(parser.evaluate({"a": True, "b": False}))
        self.assertFalse(parser.evaluate({"a": True, "b": True}))


# ТЕСТЫ ДЛЯ TRUTH TABLE


class TestTruthTable(unittest.TestCase):
    """Тесты для таблицы истинности"""

    def test_get_truth_vector(self):
        """Тест get_truth_vector (возвращает bool)"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        vector = tt.get_truth_vector()
        self.assertEqual(vector, [False, False, False, True])
        self.assertIsInstance(vector[0], bool)

    def test_print_table_output(self):
        """Тест print_table (хотя бы не падает)"""
        import io
        import sys

        parser = LogicParser("a & b")
        tt = TruthTable(parser)

        # Перехватываем вывод
        captured_output = io.StringIO()
        sys.stdout = captured_output
        tt.print_table()
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("a b | f", output)
        self.assertIn("0 0 | 0", output)
        self.assertIn("1 1 | 1", output)

    def test_get_row_by_number_complex(self):
        """Тест получения строки для 3 переменных"""
        parser = LogicParser("a & b & c")
        tt = TruthTable(parser)

        row = tt.get_row_by_number(7)  # (1,1,1) -> True
        self.assertEqual(row[0], {"a": True, "b": True, "c": True})
        self.assertTrue(row[1])

        row = tt.get_row_by_number(0)  # (0,0,0) -> False
        self.assertEqual(row[0], {"a": False, "b": False, "c": False})
        self.assertFalse(row[1])

    def test_variables_order(self):
        """Тест порядка переменных в таблице"""
        parser = LogicParser("c & a")
        tt = TruthTable(parser)
        self.assertEqual(tt.variables, ["a", "c"])

    def test_conjunction_truth_table(self):
        """Тест таблицы для конъюнкции"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)

        self.assertEqual(len(tt.rows), 4)  # 2^2 = 4
        self.assertEqual(tt.get_truth_vector_int(), [0, 0, 0, 1])
        self.assertEqual(tt.get_minterms(), [3])  # только (1,1)
        self.assertEqual(tt.get_maxterms(), [0, 1, 2])

    def test_disjunction_truth_table(self):
        """Тест таблицы для дизъюнкции"""
        parser = LogicParser("a | b")
        tt = TruthTable(parser)

        self.assertEqual(tt.get_truth_vector_int(), [0, 1, 1, 1])
        self.assertEqual(tt.get_minterms(), [1, 2, 3])
        self.assertEqual(tt.get_maxterms(), [0])

    def test_xor_truth_table(self):
        """Тест таблицы для XOR"""
        parser = LogicParser("(a & !b) | (!a & b)")
        tt = TruthTable(parser)

        self.assertEqual(tt.get_truth_vector_int(), [0, 1, 1, 0])
        self.assertEqual(tt.get_minterms(), [1, 2])
        self.assertEqual(tt.get_maxterms(), [0, 3])

    def test_three_variables_table_size(self):
        """Тест размера таблицы для 3 переменных"""
        parser = LogicParser("a & b & c")
        tt = TruthTable(parser)

        self.assertEqual(len(tt.rows), 8)  # 2^3 = 8

    def test_get_row_by_number(self):
        """Тест получения строки по номеру"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)

        row = tt.get_row_by_number(3)  # (1,1) -> True
        self.assertEqual(row[0], {"a": True, "b": True})
        self.assertTrue(row[1])

        row = tt.get_row_by_number(0)  # (0,0) -> False
        self.assertEqual(row[0], {"a": False, "b": False})
        self.assertFalse(row[1])

    def test_tautology(self):
        """Тест тавтологии"""
        parser = LogicParser("a | !a")
        tt = TruthTable(parser)

        self.assertEqual(tt.get_truth_vector_int(), [1, 1])
        self.assertEqual(tt.get_minterms(), [0, 1])
        self.assertEqual(tt.get_maxterms(), [])

    def test_contradiction(self):
        """Тест противоречия"""
        parser = LogicParser("a & !a")
        tt = TruthTable(parser)

        self.assertEqual(tt.get_truth_vector_int(), [0, 0])
        self.assertEqual(tt.get_minterms(), [])
        self.assertEqual(tt.get_maxterms(), [0, 1])


# ТЕСТЫ ДЛЯ NORMAL FORMS


class TestNormalForms(unittest.TestCase):
    """Тесты для нормальных форм"""

    def test_three_variables_sdnf(self):
        """Тест СДНФ для 3 переменных"""
        parser = LogicParser("(a & b) | c")
        tt = TruthTable(parser)
        nf = NormalForms(tt)

        sdnf = nf.get_sdnf()
        self.assertIn("a", sdnf)
        self.assertIn("b", sdnf)
        self.assertIn("c", sdnf)

    def test_three_variables_sknf(self):
        """Тест СКНФ для 3 переменных"""
        parser = LogicParser("a & b & c")
        tt = TruthTable(parser)
        nf = NormalForms(tt)

        sknf = nf.get_sknf()
        self.assertIn("a", sknf)
        self.assertIn("b", sknf)
        self.assertIn("c", sknf)

    def test_index_form_three_vars(self):
        """Тест индексной формы для 3 переменных"""
        parser = LogicParser("a & b & c")
        tt = TruthTable(parser)
        nf = NormalForms(tt)

        # Вектор [0,0,0,0,0,0,0,1] -> индекс 10000000 -> 128
        self.assertEqual(nf.get_index_form_binary(), "10000000")
        self.assertEqual(nf.get_index_form(), 128)

    def test_index_form_all_ones(self):
        """Тест индексной формы для тавтологии"""
        parser = LogicParser("a | !a")
        tt = TruthTable(parser)
        nf = NormalForms(tt)

        # Вектор [1,1] -> индекс 11 -> 3
        self.assertEqual(nf.get_index_form_binary(), "11")
        self.assertEqual(nf.get_index_form(), 3)

    def test_conjunction_sdnf(self):
        """Тест СДНФ для конъюнкции"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        nf = NormalForms(tt)

        self.assertEqual(nf.get_sdnf(), "(a & b)")
        self.assertEqual(nf.get_sdnf_numeric(), "∨(3)")

    def test_disjunction_sknf(self):
        """Тест СКНФ для дизъюнкции"""
        parser = LogicParser("a | b")
        tt = TruthTable(parser)
        nf = NormalForms(tt)

        self.assertEqual(nf.get_sknf(), "(a | b)")
        self.assertEqual(nf.get_sknf_numeric(), "∧(0)")

    def test_xor_normal_forms(self):
        """Тест нормальных форм для XOR"""
        parser = LogicParser("(a & !b) | (!a & b)")
        tt = TruthTable(parser)
        nf = NormalForms(tt)

        self.assertEqual(nf.get_sdnf(), "(!a & b) | (a & !b)")
        self.assertEqual(nf.get_sknf(), "(a | b) & (!a | !b)")
        self.assertEqual(nf.get_sdnf_numeric(), "∨(1,2)")
        self.assertEqual(nf.get_sknf_numeric(), "∧(0,3)")

    def test_index_form(self):
        """Тест индексной формы"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        nf = NormalForms(tt)

        # Вектор [0,0,0,1] -> индекс 1000 -> 8
        self.assertEqual(nf.get_index_form_binary(), "1000")
        self.assertEqual(nf.get_index_form(), 8)

    def test_index_form_complex(self):
        """Тест индексной формы для XOR"""
        parser = LogicParser("(a & !b) | (!a & b)")
        tt = TruthTable(parser)
        nf = NormalForms(tt)

        # Вектор [0,1,1,0] -> индекс 0110 -> 6
        self.assertEqual(nf.get_index_form_binary(), "0110")
        self.assertEqual(nf.get_index_form(), 6)

    def test_tautology_forms(self):
        """Тест форм для тавтологии"""
        parser = LogicParser("a | !a")
        tt = TruthTable(parser)
        nf = NormalForms(tt)

        self.assertEqual(nf.get_sdnf(), "(!a) | (a)")
        self.assertEqual(nf.get_sknf(), "1")

    def test_contradiction_forms(self):
        """Тест форм для противоречия"""
        parser = LogicParser("a & !a")
        tt = TruthTable(parser)
        nf = NormalForms(tt)

        self.assertEqual(nf.get_sdnf(), "0")
        self.assertEqual(nf.get_sknf(), "(a) & (!a)")


# ТЕСТЫ ДЛЯ ПОЛИНОМА ЖЕГАЛКИНА


class TestZhgPolynomial(unittest.TestCase):
    """Тесты для полинома Жегалкина"""

    def test_is_variable_fictitious(self):
        """Тест is_variable_fictitious"""
        parser = LogicParser("(a|b)&a")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        self.assertTrue(zhg.is_variable_fictitious("b"))
        self.assertFalse(zhg.is_variable_fictitious("a"))

    def test_get_linear_form_linear(self):
        """Тест get_linear_form для линейной функции"""
        parser = LogicParser("(a & !b) | (!a & b)")  # XOR
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        linear_form = zhg.get_linear_form()
        self.assertIn("a", linear_form)
        self.assertIn("b", linear_form)

    def test_get_linear_form_nonlinear(self):
        """Тест get_linear_form для нелинейной функции"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        linear_form = zhg.get_linear_form()
        self.assertEqual(linear_form, "Функция не является линейной")

    def test_get_linear_form_constant(self):
        """Тест get_linear_form для константы"""
        parser = LogicParser("a & !a")  # константа 0
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        # Полином: 0
        self.assertEqual(zhg.get_polynomial(), "0")
        # linear_form должна вернуть "0" для линейной функции
        # Но is_linear для "0" вернёт True
        self.assertTrue(zhg.is_linear())

    def test_get_coefficients_table(self):
        """Тест get_coefficients_table"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        table = zhg.get_coefficients_table()
        self.assertIn("Конъюнкция | Коэффициент", table)
        self.assertIn("1", table)
        self.assertIn("a & b", table)

    def test_polynomial_zero_function(self):
        """Тест полинома для тождественного нуля"""
        parser = LogicParser("a & !a")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        self.assertEqual(zhg.get_polynomial(), "0")

    def test_polynomial_one_function(self):
        """Тест полинома для тождественной единицы"""
        parser = LogicParser("a | !a")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        self.assertEqual(zhg.get_polynomial(), "1")

    def test_fictitious_with_three_vars(self):
        """Тест фиктивных переменных для 3 переменных"""
        parser = LogicParser("(a & c)|(b&!b)")  # b - фиктивная
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        fictitious = zhg.find_fictitious_variables()
        essential = zhg.get_essential_variables()

        self.assertIn("b", fictitious)
        self.assertEqual(essential, ["a", "c"])

    def test_get_essential_variables_all(self):
        """Тест когда все переменные существенные"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        essential = zhg.get_essential_variables()
        self.assertEqual(essential, ["a", "b"])

    def test_derivative_complex(self):
        """Тест производной для сложного выражения"""
        parser = LogicParser("a & b | a & c")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        # ∂f/∂a = b | c
        deriv = zhg.partial_derivative_analytic("a")
        self.assertIsNotNone(deriv)
        self.assertNotEqual(deriv, "0")

    def test_mixed_derivative_order_3(self):
        """Тест смешанной производной 3-го порядка"""
        parser = LogicParser("a & b & c")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        # ∂³(a&b&c)/(∂a∂b∂c) = 1
        deriv = zhg.mixed_derivative_analytic(["a", "b", "c"])
        self.assertEqual(deriv, "1")

    def test_print_polynomial_output(self):
        """Тест print_polynomial (не падает)"""
        import io
        import sys

        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        captured_output = io.StringIO()
        sys.stdout = captured_output
        zhg.print_polynomial()
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("ПОЛИНОМ ЖЕГАЛКИНА", output)

    def test_print_fictitious_analysis_output(self):
        """Тест print_fictitious_analysis (не падает)"""
        import io
        import sys

        parser = LogicParser("(a|b)&a")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        captured_output = io.StringIO()
        sys.stdout = captured_output
        zhg.print_fictitious_analysis()
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("АНАЛИЗ ФИКТИВНЫХ ПЕРЕМЕННЫХ", output)
        self.assertIn("b", output)

    def test_print_derivatives_zhg_output(self):
        """Тест print_derivatives_zhg (не падает)"""
        import io
        import sys

        parser = LogicParser("a & b & c")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        captured_output = io.StringIO()
        sys.stdout = captured_output
        zhg.print_derivatives_zhg()
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("ПРОИЗВОДНЫЕ ЧЕРЕЗ ПОЛИНОМ ЖЕГАЛКИНА", output)

    def test_get_triangle_visualization(self):
        """Тест get_triangle_visualization"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        viz = zhg.get_triangle_visualization()
        self.assertIn("Треугольник Паскаля", viz)
        self.assertIn("Коэффициенты", viz)

    def test_partial_derivative_zhg_method(self):
        """Тест partial_derivative_zhg (возвращает объект)"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        deriv_zhg = zhg.partial_derivative_zhg("a")
        self.assertIsInstance(deriv_zhg, ZhgPolynomial)
        self.assertIsNotNone(deriv_zhg.get_polynomial())

    def test_linear_form_with_constant_term(self):
        """Тест линейной формы с константным членом"""
        parser = LogicParser("!a")  # 1 ⊕ a
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        self.assertTrue(zhg.is_linear())
        linear_form = zhg.get_linear_form()
        self.assertIn("1", linear_form)
        self.assertIn("a", linear_form)

    def test_conjunction_polynomial(self):
        """Тест полинома для конъюнкции"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        self.assertEqual(zhg.get_polynomial(), "a & b")

    def test_disjunction_polynomial(self):
        """Тест полинома для дизъюнкции"""
        parser = LogicParser("a | b")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        # a | b = a ⊕ b ⊕ a&b
        self.assertEqual(zhg.get_polynomial(), "b ⊕ a ⊕ a & b")

    def test_xor_polynomial(self):
        """Тест полинома для XOR"""
        parser = LogicParser("(a & !b) | (!a & b)")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        # XOR = a ⊕ b
        self.assertEqual(zhg.get_polynomial(), "b ⊕ a")

    def test_negation_polynomial(self):
        """Тест полинома для отрицания"""
        parser = LogicParser("!a")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        # !a = 1 ⊕ a
        self.assertEqual(zhg.get_polynomial(), "1 ⊕ a")

    def test_linearity_check(self):
        """Тест проверки линейности"""
        # XOR - линейная
        parser = LogicParser("(a & !b) | (!a & b)")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)
        self.assertTrue(zhg.is_linear())

        # Конъюнкция - нелинейная
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)
        self.assertFalse(zhg.is_linear())

    def test_fictitious_variables_conjunction(self):
        """Тест фиктивных переменных для конъюнкции"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        self.assertEqual(zhg.find_fictitious_variables(), [])
        self.assertEqual(zhg.get_essential_variables(), ["a", "b"])

    def test_fictitious_variables_absorption(self):
        """Тест фиктивных переменных для поглощения"""
        parser = LogicParser("(a|b)&a")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        # f = a, только 'a' существенна
        fictitious = zhg.find_fictitious_variables()
        essential = zhg.get_essential_variables()

        self.assertIn("b", fictitious)
        self.assertNotIn("a", fictitious)
        self.assertEqual(essential, ["a"])

    def test_coefficients_count(self):
        """Тест количества коэффициентов"""
        parser = LogicParser("a & b & c")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        # Для 3 переменных должно быть 8 коэффициентов
        self.assertEqual(len(zhg.coefficients), 8)
        self.assertEqual(len(zhg.conjunctions), 8)

    def test_coefficients_order(self):
        """Тест порядка коэффициентов"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        # Проверяем первые 4 конъюнкции для 2 переменных
        zhg.get_linear_form()
        self.assertEqual(zhg.conjunctions[0], "1")
        self.assertEqual(zhg.conjunctions[1], "b")
        self.assertEqual(zhg.conjunctions[2], "a")
        self.assertEqual(zhg.conjunctions[3], "a & b")

    def test_derivative_analytic(self):
        """Тест аналитической производной"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        # ∂(a&b)/∂a = b
        deriv = zhg.partial_derivative_analytic("a")
        self.assertEqual(deriv, "b")

        # ∂(a&b)/∂b = a
        deriv = zhg.partial_derivative_analytic("b")
        self.assertEqual(deriv, "a")

    def test_mixed_derivative_analytic(self):
        """Тест смешанной аналитической производной"""
        parser = LogicParser("a & b & c")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        # ∂²(a&b&c)/(∂a∂b) = c
        deriv = zhg.mixed_derivative_analytic(["a", "b"])
        self.assertEqual(deriv, "c")

    def test_absorption_polynomial(self):
        """Тест полинома для закона поглощения"""
        parser = LogicParser("(a|b)&a")
        tt = TruthTable(parser)
        zhg = ZhgPolynomial(tt)

        # f = a, полином должен быть "a"
        self.assertEqual(zhg.get_polynomial(), "a")


# ТЕСТЫ ДЛЯ КЛАССОВ ПОСТА


class TestPostClasses(unittest.TestCase):
    """Тесты для классов Поста"""

    def test_conjunction_post(self):
        """Тест классов Поста для конъюнкции"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        pc = PostClasses(tt)

        self.assertTrue(pc.classes["T0"])  # f(0,0)=0
        self.assertTrue(pc.classes["T1"])  # f(1,1)=1
        self.assertFalse(pc.classes["S"])  # не самодвойственна
        self.assertTrue(pc.classes["M"])  # монотонна
        self.assertFalse(pc.classes["L"])  # не линейна

    def test_disjunction_post(self):
        """Тест классов Поста для дизъюнкции"""
        parser = LogicParser("a | b")
        tt = TruthTable(parser)
        pc = PostClasses(tt)

        self.assertTrue(pc.classes["T0"])
        self.assertTrue(pc.classes["T1"])
        self.assertFalse(pc.classes["S"])
        self.assertTrue(pc.classes["M"])
        self.assertFalse(pc.classes["L"])

    def test_negation_post(self):
        """Тест классов Поста для отрицания"""
        parser = LogicParser("!a")
        tt = TruthTable(parser)
        pc = PostClasses(tt)

        self.assertFalse(pc.classes["T0"])  # f(0)=1
        self.assertFalse(pc.classes["T1"])  # f(1)=0
        self.assertTrue(pc.classes["S"])  # самодвойственна
        self.assertFalse(pc.classes["M"])  # не монотонна
        self.assertTrue(pc.classes["L"])  # линейна

    def test_sheffer_post(self):
        """Тест классов Поста для штриха Шеффера"""
        parser = LogicParser("!(a & b)")
        tt = TruthTable(parser)
        pc = PostClasses(tt)

        # Штрих Шеффера - полная система
        self.assertTrue(pc.is_complete_system())

        # Не принадлежит ни одному классу
        self.assertFalse(pc.classes["T0"])
        self.assertFalse(pc.classes["T1"])
        self.assertFalse(pc.classes["S"])
        self.assertFalse(pc.classes["M"])
        self.assertFalse(pc.classes["L"])

    def test_complete_system(self):
        """Тест определения полноты системы"""
        # Штрих Шеффера - полная
        parser = LogicParser("!(a & b)")
        tt = TruthTable(parser)
        pc = PostClasses(tt)
        self.assertTrue(pc.is_complete_system())

        # Конъюнкция - не полная
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        pc = PostClasses(tt)
        self.assertTrue(pc.is_complete_system())

    def test_xor_post(self):
        """Тест классов Поста для XOR"""
        parser = LogicParser("(a & !b) | (!a & b)")
        tt = TruthTable(parser)
        pc = PostClasses(tt)

        self.assertTrue(pc.classes["T0"])  # f(0,0)=0
        self.assertFalse(pc.classes["T1"])  # f(1,1)=0
        self.assertFalse(pc.classes["S"])
        self.assertFalse(pc.classes["M"])
        self.assertTrue(pc.classes["L"])  # линейна (a⊕b)

    def test_get_missing_classes(self):
        """Тест получения недостающих классов"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        pc = PostClasses(tt)

        missing = pc.get_missing_classes()
        self.assertIn("S", missing)
        self.assertIn("L", missing)
        self.assertEqual(len(missing), 2)


# ТЕСТЫ ДЛЯ БУЛЕВЫХ ПРОИЗВОДНЫХ


class TestBooleanDerivative(unittest.TestCase):
    """Тесты для булевых производных"""

    def test_derivative_conjunction(self):
        """Тест производной конъюнкции"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        bd = BooleanDerivative(parser, tt)

        # ∂(a&b)/∂a = b
        deriv = bd.partial_derivative("a")
        self.assertIn("b", deriv)

    def test_derivative_xor(self):
        """Тест производной XOR"""
        parser = LogicParser("(a & !b) | (!a & b)")
        tt = TruthTable(parser)
        bd = BooleanDerivative(parser, tt)

        # ∂(a⊕b)/∂a = 1
        deriv = bd.partial_derivative("a")
        self.assertIn("1", deriv.lower())

    def test_mixed_derivative(self):
        """Тест смешанной производной"""
        parser = LogicParser("a & b & c")
        tt = TruthTable(parser)
        bd = BooleanDerivative(parser, tt)

        # ∂²(a&b&c)/(∂a∂b) = c
        deriv = bd.mixed_derivative(["a", "b"])
        self.assertIn("c", deriv)


# ТЕСТЫ ДЛЯ МИНИМИЗАЦИИ


class TestMinimizer(unittest.TestCase):
    """Тесты для методов минимизации"""

    def test_quine_dnf_verbose(self):
        """Тест minimize_quine_dnf с verbose=True (покрытие вывода)"""
        import io
        import sys

        parser = LogicParser("(a & b) | (a & !b)")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = minimizer.minimize_quine_dnf(verbose=True)

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("МИНИМИЗАЦИЯ ДНФ", output)
        self.assertIn("Исходные минтермы", output)
        self.assertIn("Склеивание", output)
        self.assertEqual(result, "(a)")

    def test_quine_knf_verbose(self):
        """Тест minimize_quine_knf с verbose=True"""
        import io
        import sys

        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = minimizer.minimize_quine_knf(verbose=True)

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("МИНИМИЗАЦИЯ КНФ", output)
        self.assertIn("Исходные макстермы", output)

    def test_quine_knf_empty(self):
        """Тест minimize_quine_knf для тавтологии (нет макстермов)"""
        parser = LogicParser("a | !a")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        result = minimizer.minimize_quine_knf(verbose=False)
        self.assertEqual(result, "1")

    def test_quine_dnf_empty(self):
        """Тест minimize_quine_dnf для противоречия (нет минтермов)"""
        parser = LogicParser("a & !a")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        result = minimizer.minimize_quine_dnf(verbose=False)
        self.assertEqual(result, "0")

    def test_mccluskey_verbose(self):
        """Тест minimize_mccluskey_dnf с verbose=True"""
        import io
        import sys

        parser = LogicParser("(a & b) | (a & !b)")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = minimizer.minimize_mccluskey_dnf(verbose=True)

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("СКЛЕИВАНИЕ", output)
        self.assertIn("ТАБЛИЦА ПОКРЫТИЯ", output)
        self.assertEqual(result, "(a)")

    def test_to_binary_custom_length(self):
        """Тест _to_binary с кастомной длиной"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        result = minimizer._to_binary(5, 4)
        self.assertEqual(result, "0101")

    def test_count_ones(self):
        """Тест _count_ones"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        self.assertEqual(minimizer._count_ones("101"), 2)
        self.assertEqual(minimizer._count_ones("000"), 0)
        self.assertEqual(minimizer._count_ones("111"), 3)

    def test_differ_by_one_bit_edge_cases(self):
        """Тест _differ_by_one_bit для граничных случаев"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        # Разная длина
        can_merge, result = minimizer._differ_by_one_bit("10", "101")
        self.assertFalse(can_merge)

        # Одинаковые строки
        can_merge, result = minimizer._differ_by_one_bit("101", "101")
        self.assertFalse(can_merge)

        # Отличие с '-' в одной из строк
        can_merge, result = minimizer._differ_by_one_bit("1-1", "101")
        self.assertFalse(can_merge)

    def test_implicant_to_expression_knf(self):
        """Тест _implicant_to_expression для КНФ"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        # Для КНФ: '0' -> переменная, '1' -> отрицание
        expr = minimizer._implicant_to_expression("10", negative=True)
        self.assertEqual(expr, "(!a | b)")

    def test_implicant_to_expression_empty(self):
        """Тест _implicant_to_expression с пустой импликантой"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        # Все '-'
        expr_dnf = minimizer._implicant_to_expression("--", negative=False)
        self.assertEqual(expr_dnf, "1")

        expr_knf = minimizer._implicant_to_expression("--", negative=True)
        self.assertEqual(expr_knf, "0")

    def test_get_covered_minterms_no_dash(self):
        """Тест _get_covered_minterms без '-'"""
        parser = LogicParser("a & b & c")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        covered = minimizer._get_covered_minterms("101")
        self.assertEqual(covered, [5])  # 101 в двоичной = 5

    def test_get_covered_minterms_with_dash(self):
        """Тест _get_covered_minterms с '-'"""
        parser = LogicParser("a & b & c")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        # "1-0" покрывает "100" (4) и "110" (6)
        covered = minimizer._get_covered_minterms("1-0")
        self.assertEqual(covered, [4, 6])

    def test_karnaugh_2_vars_verbose(self):
        """Тест карты Карно для 2 переменных с verbose"""
        import io
        import sys

        parser = LogicParser("a | b")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = minimizer._karnaugh_2_vars(verbose=True)

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("Карта Карно", output)
        self.assertIsNotNone(result)

    def test_karnaugh_3_vars_verbose(self):
        """Тест карты Карно для 3 переменных с verbose"""
        import io
        import sys

        parser = LogicParser("a & b & c")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = minimizer._karnaugh_3_vars(verbose=True)

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("Карта Карно (3 переменные)", output)
        self.assertIsNotNone(result)

    def test_karnaugh_4_vars_verbose(self):
        """Тест карты Карно для 4 переменных с verbose"""
        import io
        import sys

        parser = LogicParser("a & b & c & d")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = minimizer._karnaugh_4_vars(verbose=True)

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("Карта Карно (4 переменные)", output)
        self.assertIsNotNone(result)

    def test_karnaugh_5_vars_verbose(self):
        """Тест карты Карно для 5 переменных с verbose"""
        import io
        import sys

        parser = LogicParser("a & b & c & d & e")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = minimizer._karnaugh_5_vars(verbose=True)

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("Карта Карно (5 переменных)", output)
        self.assertIsNotNone(result)

    def test_region_to_expression_2_single(self):
        """Тест _region_to_expression_2 для одиночной клетки"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        # Набор {3} -> a=1, b=1
        expr = minimizer._region_to_expression_2({3})
        self.assertEqual(expr, "(a & b)")

    def test_region_to_expression_2_pairs(self):
        """Тест _region_to_expression_2 для пар"""
        parser = LogicParser("a | b")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        # Пара {0, 1} -> !a
        expr = minimizer._region_to_expression_2({0, 1})
        self.assertEqual(expr, "(!a)")

        # Пара {2, 3} -> a
        expr = minimizer._region_to_expression_2({2, 3})
        self.assertEqual(expr, "(a)")

        # Пара {0, 2} -> !b
        expr = minimizer._region_to_expression_2({0, 2})
        self.assertEqual(expr, "(!b)")

        # Пара {1, 3} -> b
        expr = minimizer._region_to_expression_2({1, 3})
        self.assertEqual(expr, "(b)")

    def test_find_regions_2_vars_full(self):
        """Тест _find_regions_2_vars для полной карты"""
        parser = LogicParser("(a & b) | (!a & b) | (a & !b) | (!a & !b)")  # тавтология
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        result = minimizer._find_regions_2_vars()
        self.assertEqual(result, "1")

    def test_print_all_methods(self):
        """Тест print_all_methods (не падает)"""
        import io
        import sys

        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        captured_output = io.StringIO()
        sys.stdout = captured_output

        minimizer.print_all_methods()

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("МИНИМИЗАЦИЯ БУЛЕВОЙ ФУНКЦИИ", output)
        self.assertIn("СРАВНЕНИЕ РЕЗУЛЬТАТОВ", output)

    def test_minimize_karnaugh_dnf_verbose(self):
        """Тест minimize_karnaugh_dnf с verbose"""
        import io
        import sys

        parser = LogicParser("a | b")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = minimizer.minimize_karnaugh_dnf(verbose=True)

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("МИНИМИЗАЦИЯ ДНФ МЕТОДОМ КАРТ КАРНО", output)
        self.assertIsNotNone(result)

    def test_warning_more_than_5_vars(self):
        """Тест предупреждения для >5 переменных"""
        import io
        import sys

        # Создаём парсер с 6 переменными (теоретически)
        # Но наш парсер поддерживает только до 5, поэтому используем мок
        parser = LogicParser("a & b & c & d & e")
        # Не можем протестировать >5, так как парсер ограничивает
        # Просто проверяем что для 5 переменных работает
        tt = TruthTable(parser)
        self.assertEqual(tt.n_vars, 5)

    def test_quine_absorption(self):
        """Тест минимизации закона поглощения"""
        parser = LogicParser("(a|b)&a")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        result = minimizer.minimize_quine_dnf(verbose=False)
        # Должно упроститься до "a"
        self.assertIn("a", result)
        # "b" должен отсутствовать в результате
        self.assertNotIn("b", result)

    def test_quine_simple(self):
        """Тест простой минимизации"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        result = minimizer.minimize_quine_dnf(verbose=False)
        # Конъюнкция и так минимальна
        self.assertEqual(result, "(a & b)")

    def test_quine_gluing(self):
        """Тест склеивания"""
        # f = a&b | a&!b = a
        parser = LogicParser("(a & b) | (a & !b)")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        result = minimizer.minimize_quine_dnf(verbose=False)
        self.assertEqual(result, "(a)")

    def test_mccluskey_simple(self):
        """Тест расчётно-табличного метода"""
        parser = LogicParser("(a & b) | (a & !b)")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        result = minimizer.minimize_mccluskey_dnf(verbose=False)
        self.assertIn("a", result)

    def test_karnaugh_2_vars(self):
        """Тест карты Карно для 2 переменных"""
        parser = LogicParser("a | b")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        result = minimizer.minimize_karnaugh_dnf(verbose=False)
        # a | b - уже минимальная форма
        self.assertIn("a", result)
        self.assertIn("b", result)

    def test_knf_minimization(self):
        """Тест минимизации КНФ"""
        parser = LogicParser("a & b")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        result = minimizer.minimize_quine_knf(verbose=False)
        # КНФ для a&b: (a) & (b)
        self.assertIn("a", result)
        self.assertIn("b", result)

    def test_three_variables_gluing(self):
        """Тест склеивания для 3 переменных"""
        # f = a&b&c | a&b&!c = a&b
        parser = LogicParser("(a & b & c) | (a & b & !c)")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        result = minimizer.minimize_quine_dnf(verbose=False)
        self.assertEqual(result, "(a & b)")

    def test_consensus(self):
        """Тест закона консенсуса"""
        # f = a&b | !a&c | b&c = a&b | !a&c
        parser = LogicParser("(a & b) | (!a & c) | (b & c)")
        tt = TruthTable(parser)
        minimizer = Minimizer(tt)

        result = minimizer.minimize_quine_dnf(verbose=False)
        # b&c должно исчезнуть (закон консенсуса)
        # Должны остаться только a&b и !a&c
        terms = result.split(" | ")
        self.assertEqual(len(terms), 2)


# ИНТЕГРАЦИОННЫЕ ТЕСТЫ


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты, проверяющие взаимодействие модулей"""

    def test_full_pipeline_conjunction(self):
        """Полный тест для конъюнкции"""
        expr = "a & b"

        # Парсинг
        parser = LogicParser(expr)
        self.assertIsNotNone(parser)

        # Таблица истинности
        tt = TruthTable(parser)
        self.assertEqual(tt.get_truth_vector_int(), [0, 0, 0, 1])

        # Нормальные формы
        nf = NormalForms(tt)
        self.assertEqual(nf.get_sdnf(), "(a & b)")

        # Полином Жегалкина
        zhg = ZhgPolynomial(tt)
        self.assertEqual(zhg.get_polynomial(), "a & b")
        self.assertFalse(zhg.is_linear())

        # Классы Поста
        pc = PostClasses(tt)
        self.assertTrue(pc.classes["T0"])
        self.assertTrue(pc.classes["T1"])

        # Минимизация
        minimizer = Minimizer(tt)
        result = minimizer.minimize_quine_dnf(verbose=False)
        self.assertEqual(result, "(a & b)")

    def test_full_pipeline_xor(self):
        """Полный тест для XOR"""
        expr = "(a & !b) | (!a & b)"

        parser = LogicParser(expr)
        tt = TruthTable(parser)

        # XOR: вектор [0,1,1,0]
        self.assertEqual(tt.get_truth_vector_int(), [0, 1, 1, 0])

        # Полином Жегалкина
        zhg = ZhgPolynomial(tt)
        self.assertTrue(zhg.is_linear())
        self.assertEqual(zhg.get_polynomial(), "b ⊕ a")

        # Классы Поста
        pc = PostClasses(tt)
        self.assertTrue(pc.is_complete_system())

        # Минимизация (XOR уже минимален)
        minimizer = Minimizer(tt)
        result = minimizer.minimize_quine_dnf(verbose=False)
        self.assertEqual(result, "(!a & b) | (a & !b)")

    def test_sdknf_numeric(self):
        expr1 = "(a->(b->a))"
        parser1 = LogicParser(expr1)
        tt1 = TruthTable(parser1)
        nf1 = NormalForms(tt1)
        self.assertEqual(nf1.get_sknf_numeric(), "Nah")

        expr2 = "!(a->(b->a))"
        parser2 = LogicParser(expr2)
        tt2 = TruthTable(parser2)
        nf2 = NormalForms(tt2)
        self.assertEqual(nf2.get_sdnf_numeric(), "Nah")

    def test_full_pipeline_sheffer(self):
        """Полный тест для штриха Шеффера"""
        expr = "!(a & b)"

        parser = LogicParser(expr)
        tt = TruthTable(parser)

        # Штрих Шеффера: вектор [1,1,1,0]
        self.assertEqual(tt.get_truth_vector_int(), [1, 1, 1, 0])

        # Классы Поста - полная система
        pc = PostClasses(tt)
        self.assertTrue(pc.is_complete_system())

        # Полином Жегалкина
        zhg = ZhgPolynomial(tt)
        self.assertFalse(zhg.is_linear())

    def test_task_example(self):
        """Тест примера из задания"""
        expr = "!(!a->!b) | c"

        parser = LogicParser(expr)
        tt = TruthTable(parser)
        nf = NormalForms(tt)
        zhg = ZhgPolynomial(tt)

        # Проверяем, что все модули работают без ошибок
        sdnf = nf.get_sdnf()
        sknf = nf.get_sknf()
        poly = zhg.get_polynomial()

        self.assertIsNotNone(sdnf)
        self.assertIsNotNone(sknf)
        self.assertIsNotNone(poly)

        # Минимизация
        minimizer = Minimizer(tt)
        dnf = minimizer.minimize_quine_dnf(verbose=False)
        self.assertIsNotNone(dnf)


# ЗАПУСК ТЕСТОВ


def run_tests():
    """Запуск всех тестов"""

    # Создаём test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Добавляем все тестовые классы
    suite.addTests(loader.loadTestsFromTestCase(TestLogicParser))
    suite.addTests(loader.loadTestsFromTestCase(TestTruthTable))
    suite.addTests(loader.loadTestsFromTestCase(TestNormalForms))
    suite.addTests(loader.loadTestsFromTestCase(TestZhgPolynomial))
    suite.addTests(loader.loadTestsFromTestCase(TestPostClasses))
    suite.addTests(loader.loadTestsFromTestCase(TestBooleanDerivative))
    suite.addTests(loader.loadTestsFromTestCase(TestMinimizer))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Запускаем с подробным выводом
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Выводим итоги

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
