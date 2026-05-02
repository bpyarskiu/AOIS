"""
Лабораторная работа №2
Построение СКНФ и СДНФ на основании таблиц истинности

Главный модуль с интерактивным интерфейсом
Поддерживает все 12 пунктов задания
"""

import sys
import os
from typing import Optional
from itertools import combinations

# Импортируем все наши модули
from logic_parser import LogicParser
from truth_table import TruthTable
from normal_forms import NormalForms
from post_classes import PostClasses
from zhg_polynomial import ZhgPolynomial
from boolean_derivative import BooleanDerivative
from minimizer import Minimizer


class Colors:
    """Цвета для красивого вывода в консоли"""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_header(text: str, width: int = 70):
    """Выводит красивый заголовок"""
    print("\n" + "=" * width)
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^{width}}{Colors.ENDC}")
    print("=" * width)


def print_subheader(text: str, width: int = 50):
    """Выводит подзаголовок"""
    print(f"\n{Colors.CYAN}{'─' * width}{Colors.ENDC}")
    print(f"{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'─' * width}{Colors.ENDC}")


def print_success(text: str):
    """Выводит успешное сообщение"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Выводит сообщение об ошибке"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")


def print_info(text: str):
    """Выводит информационное сообщение"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Выводит предупреждение"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")


def show_help():
    """Показывает справку по командам"""
    print_header("СПРАВКА")
    print(f"""
{Colors.BOLD}Поддерживаемые операции:{Colors.ENDC}
  &  - конъюнкция (И)
  |  - дизъюнкция (ИЛИ)
  !  - отрицание (НЕ)
  -> - импликация
  ~  - эквивалентность

{Colors.BOLD}Переменные:{Colors.ENDC} a, b, c, d, e (до 5)

{Colors.BOLD}Примеры выражений:{Colors.ENDC}
  {Colors.GREEN}a & b{Colors.ENDC}           - конъюнкция
  {Colors.GREEN}a | b{Colors.ENDC}           - дизъюнкция
  {Colors.GREEN}!a -> b{Colors.ENDC}         - импликация с отрицанием
  {Colors.GREEN}!(a & b){Colors.ENDC}        - штрих Шеффера
  {Colors.GREEN}(a & b) | (!a & !b){Colors.ENDC} - эквивалентность через И-ИЛИ-НЕ
  {Colors.GREEN}!(!a -> !b) | c{Colors.ENDC}  - пример из задания

{Colors.BOLD}Команды:{Colors.ENDC}
  {Colors.YELLOW}help{Colors.ENDC}    - показать эту справку
  {Colors.YELLOW}demo{Colors.ENDC}    - запустить демонстрацию на примерах
  {Colors.YELLOW}clear{Colors.ENDC}   - очистить экран
  {Colors.YELLOW}exit{Colors.ENDC}    - выйти из программы
  {Colors.YELLOW}quit{Colors.ENDC}    - выйти из программы

{Colors.BOLD}Форматы ввода:{Colors.ENDC}
  Просто введите логическое выражение и нажмите Enter
  Программа автоматически выполнит все 12 пунктов анализа
""")


def show_welcome():
    """Показывает приветственное сообщение"""
    print_header("ЛАБОРАТОРНАЯ РАБОТА №2", 70)
    print(f"""
{Colors.BOLD}Построение СКНФ и СДНФ на основании таблиц истинности{Colors.ENDC}

{Colors.CYAN}Выполняемые пункты:{Colors.ENDC}
  1.  Принимать логическую функцию произвольного формата
  2.  Строить таблицу истинности
  3.  Строить СДНФ и СКНФ
  4.  Выводить числовую форму для СДНФ и СКНФ
  5.  Выводить индексную форму функции
  6.  Определять принадлежность функции к классам Поста
  7.  Строить полином Жегалкина
  8.  Искать фиктивные переменные
  9.  Вычислять булевы производные
  10. Минимизировать функцию расчётным методом
  11. Минимизировать функцию расчётно-табличным методом
  12. Минимизировать функцию табличным методом (карта Карно)

{Colors.YELLOW}Введите 'help' для получения справки{Colors.ENDC}
""")


def clear_screen():
    """Очищает экран консоли"""
    os.system("cls" if os.name == "nt" else "clear")


def process_function(expression: str, show_details: bool = True):
    """
    Полная обработка логической функции

    Args:
        expression: строка с логическим выражением
        show_details: показывать ли подробные выкладки
    """

    # ========== ПРОВЕРКА ВХОДНЫХ ДАННЫХ ==========
    if not expression or expression.isspace():
        print_error("Пустое выражение!")
        return None

    # Проверяем на недопустимые символы
    allowed_chars = set("abcde&|!()->~ ")
    expr_chars = set(expression.lower())
    invalid_chars = expr_chars - allowed_chars
    if invalid_chars:
        print_error(f"Недопустимые символы: {', '.join(invalid_chars)}")
        return None

    # Проверяем количество переменных
    vars_in_expr = set(c for c in expression.lower() if c in "abcde")
    if len(vars_in_expr) > 5:
        print_error("Максимальное количество переменных - 5!")
        return None
    if not vars_in_expr:
        print_error("В выражении нет переменных!")
        return None

    try:
        # ========== 1. ПАРСИНГ ==========
        print_header(f"АНАЛИЗ ФУНКЦИИ: {expression}")

        print_subheader("[1] ПАРСИНГ ВЫРАЖЕНИЯ")
        parser = LogicParser(expression)
        variables = parser.get_variables()
        print_info(f"Распознанные переменные: {', '.join(variables)}")
        print_info(f"Количество переменных: {len(variables)}")

        # ========== 2. ТАБЛИЦА ИСТИННОСТИ ==========
        print_subheader("[2] ТАБЛИЦА ИСТИННОСТИ")
        tt = TruthTable(parser)
        tt.print_table()
        print_info(f"Всего наборов: {2 ** len(variables)}")
        print_info(f"Минтермы (f=1): {tt.get_minterms()}")
        print_info(f"Макстермы (f=0): {tt.get_maxterms()}")

        # ========== 3-4. НОРМАЛЬНЫЕ ФОРМЫ ==========
        print_subheader("[3-4] НОРМАЛЬНЫЕ ФОРМЫ (СДНФ, СКНФ)")
        nf = NormalForms(tt)

        # СДНФ
        print(f"\n{Colors.BOLD}СДНФ:{Colors.ENDC}")
        print(f"  Аналитическая форма: f = {nf.get_sdnf()}")
        print(f"  Числовая форма:      {nf.get_sdnf_numeric()}")

        # СКНФ
        print(f"\n{Colors.BOLD}СКНФ:{Colors.ENDC}")
        print(f"  Аналитическая форма: f = {nf.get_sknf()}")
        print(f"  Числовая форма:      {nf.get_sknf_numeric()}")

        # ========== 5. ИНДЕКСНАЯ ФОРМА ==========
        print_subheader("[5] ИНДЕКСНАЯ ФОРМА")
        index_bin = nf.get_index_form_binary()
        index_dec = nf.get_index_form()
        print(f"  Двоичная форма:   {index_bin}")
        print(f"  Десятичная форма: {index_dec}")
        print_info(f"Индекс функции: {index_dec} (0x{index_dec:04X})")

        # ========== 7. ПОЛИНОМ ЖЕГАЛКИНА ==========
        print_subheader("[7] ПОЛИНОМ ЖЕГАЛКИНА")
        zhg = ZhgPolynomial(tt)
        print(f"  P = {zhg.get_polynomial()}")
        print_info(f"Функция {'ЛИНЕЙНА' if zhg.is_linear() else 'НЕЛИНЕЙНА'}")

        if show_details:
            print(f"\n{Colors.BOLD}Таблица коэффициентов:{Colors.ENDC}")
            print(zhg.get_coefficients_table())

        # ========== 8. ФИКТИВНЫЕ ПЕРЕМЕННЫЕ ==========
        print_subheader("[8] ФИКТИВНЫЕ ПЕРЕМЕННЫЕ")
        fictitious = zhg.find_fictitious_variables()
        essential = zhg.get_essential_variables()

        print(f"  Все переменные:    {', '.join(variables)}")
        print(f"  Существенные:      {', '.join(essential) if essential else 'нет'}")
        print(f"  Фиктивные:         {', '.join(fictitious) if fictitious else 'нет'}")

        if fictitious:
            print_info("Фиктивные переменные не влияют на значение функции")
            print_info("Их можно исключить без изменения таблицы истинности")
        else:
            print_success("Все переменные существенные")

        # ========== 6. КЛАССЫ ПОСТА ==========
        print_subheader("[6] КЛАССЫ ПОСТА")
        pc = PostClasses(tt)
        pc.print_report()

        # ========== 9. БУЛЕВЫ ПРОИЗВОДНЫЕ ==========
        print_subheader("[9] БУЛЕВЫ ПРОИЗВОДНЫЕ")
        print_info("Вычисление через полином Жегалкина (аналитический метод)")

        # Частные производные 1-го порядка
        print(f"\n{Colors.BOLD}Частные производные 1-го порядка:{Colors.ENDC}")
        for var in variables:
            deriv = zhg.partial_derivative_analytic(var)
            print(f"  ∂f/∂{var} = {deriv}")

        # Смешанные производные (если есть минимум 2 переменные)
        if len(variables) >= 2:
            print(f"\n{Colors.BOLD}Смешанные производные 2-го порядка:{Colors.ENDC}")
            for combo in combinations(variables, 2):
                vars_list = list(combo)
                deriv = zhg.mixed_derivative_analytic(vars_list)
                vars_str = "".join(vars_list)
                print(f"  ∂²f/∂{vars_str} = {deriv}")

        # Смешанные производные 3-го порядка
        if len(variables) >= 3:
            print(f"\n{Colors.BOLD}Смешанные производные 3-го порядка:{Colors.ENDC}")
            for combo in combinations(variables, 3):
                vars_list = list(combo)
                deriv = zhg.mixed_derivative_analytic(vars_list)
                vars_str = "".join(vars_list)
                print(f"  ∂³f/∂{vars_str} = {deriv}")

        # Смешанные производные 4-го порядка
        if len(variables) >= 4:
            print(f"\n{Colors.BOLD}Смешанные производные 4-го порядка:{Colors.ENDC}")
            for combo in combinations(variables, 4):
                vars_list = list(combo)
                deriv = zhg.mixed_derivative_analytic(vars_list)
                vars_str = "".join(vars_list)
                print(f"  ∂⁴f/∂{vars_str} = {deriv}")

        # ========== 10-12. МИНИМИЗАЦИЯ ==========
        print_subheader("[10-12] МИНИМИЗАЦИЯ")

        minimizer = Minimizer(tt)

        # Расчётный метод
        print(f"\n{Colors.BOLD}10. Расчётный метод (Квайна):{Colors.ENDC}")
        dnf_quine = minimizer.minimize_quine_dnf(verbose=False)
        knf_quine = minimizer.minimize_quine_knf(verbose=False)
        print(f"  ДНФ: f = {dnf_quine}")
        print(f"  КНФ: f = {knf_quine}")

        # Расчётно-табличный метод
        print(
            f"\n{Colors.BOLD}11. Расчётно-табличный метод (Квайна-МакКласки):{Colors.ENDC}"
        )
        dnf_mccluskey = minimizer.minimize_mccluskey_dnf(verbose=False)
        print(f"  ДНФ: f = {dnf_mccluskey}")

        # Карты Карно
        if len(variables) <= 5:
            print(f"\n{Colors.BOLD}12. Табличный метод (карты Карно):{Colors.ENDC}")
            dnf_karnaugh = minimizer.minimize_karnaugh_dnf(verbose=False)
            print(f"  ДНФ: f = {dnf_karnaugh}")

            # Сравнение результатов
            print(f"\n{Colors.BOLD}Сравнение результатов минимизации:{Colors.ENDC}")
            print(f"  Метод Квайна:          {dnf_quine}")
            print(f"  Метод Квайна-МакКласки: {dnf_mccluskey}")
            print(f"  Метод Карт Карно:      {dnf_karnaugh}")

            # Проверяем, совпадают ли результаты
            results = {dnf_quine, dnf_mccluskey, dnf_karnaugh}
            if len(results) == 1:
                print_success("Все методы дали одинаковый результат!")
            else:
                print_warning(
                    "Методы дали разные результаты (возможны эквивалентные формы)"
                )
        else:
            print_warning("Карты Карно поддерживают только до 5 переменных")
            print(f"  Текущее количество переменных: {len(variables)}")

        return {
            "parser": parser,
            "truth_table": tt,
            "normal_forms": nf,
            "post_classes": pc,
            "zhg_polynomial": zhg,
            "minimizer": minimizer,
            "expression": expression,
            "variables": variables,
        }

    except Exception as e:
        print_error(f"Ошибка при обработке выражения: {str(e)}")
        print_info("Проверьте синтаксис выражения и попробуйте снова")
        if show_details:
            import traceback

            print(f"\n{Colors.RED}Детали ошибки:{Colors.ENDC}")
            traceback.print_exc()
        return None


def run_demo():
    """Запускает демонстрацию на нескольких примерах"""
    print_header("ДЕМОНСТРАЦИЯ НА ПРИМЕРАХ")

    examples = [
        ("a & b", "Конъюнкция (И)"),
        ("a | b", "Дизъюнкция (ИЛИ)"),
        ("!a", "Отрицание (НЕ)"),
        ("a -> b", "Импликация"),
        ("a ~ b", "Эквивалентность"),
        ("!(a & b)", "Штрих Шеффера (И-НЕ)"),
        ("!(a | b)", "Стрелка Пирса (ИЛИ-НЕ)"),
        ("(a & b) | (!a & !b)", "Эквивалентность через И-ИЛИ-НЕ"),
        ("!(!a -> !b) | c", "Пример из задания (3 переменные)"),
        ("(a & b) | (b & c) | (a & c)", "Медиана/голосование (3 переменные)"),
    ]

    for i, (expr, desc) in enumerate(examples, 1):
        print(f"\n{Colors.YELLOW}{'─' * 70}{Colors.ENDC}")
        print(f"{Colors.BOLD}Пример {i}: {desc}{Colors.ENDC}")
        print(f"Выражение: {Colors.GREEN}{expr}{Colors.ENDC}")

        # Спрашиваем, показывать ли подробно
        if i > 1:
            choice = (
                input(
                    f"\n{Colors.CYAN}Показать полный анализ? (y/n, Enter = нет): {Colors.ENDC}"
                )
                .strip()
                .lower()
            )
            if choice != "y":
                # Показываем только ключевые результаты
                try:
                    parser = LogicParser(expr)
                    tt = TruthTable(parser)
                    nf = NormalForms(tt)
                    zhg = ZhgPolynomial(tt)
                    minimizer = Minimizer(tt)

                    print(f"  Переменные: {', '.join(parser.get_variables())}")
                    print(f"  Вектор значений: {tt.get_truth_vector_int()}")
                    print(f"  СДНФ: {nf.get_sdnf()}")
                    print(f"  Полином Жегалкина: {zhg.get_polynomial()}")
                    print(f"  Мин. ДНФ: {minimizer.minimize_quine_dnf(verbose=False)}")
                except Exception as e:
                    print_error(f"Ошибка: {e}")
                continue

        process_function(expr, show_details=False)

        if i < len(examples):
            choice = (
                input(
                    f"\n{Colors.CYAN}Продолжить демонстрацию? (y/n, Enter = да): {Colors.ENDC}"
                )
                .strip()
                .lower()
            )
            if choice == "n":
                break

    print_header("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print_info("Теперь вы можете вводить свои выражения")


def main():
    """Главная функция программы"""

    # Очищаем экран и показываем приветствие
    clear_screen()
    show_welcome()

    # История введённых выражений
    history = []

    # Основной цикл программы
    while True:
        try:
            # Показываем приглашение
            print(
                f"\n{Colors.BOLD}{Colors.CYAN}Введите логическое выражение:{Colors.ENDC}"
            )
            # print(
            #     f"{Colors.YELLOW}(команды: help, demo, history, clear, exit){Colors.ENDC}"
            # )

            # Если есть история, показываем последнее выражение
            if history:
                print(f"{Colors.GREEN}Последнее: {history[-1]}{Colors.ENDC}")

            # Получаем ввод
            user_input = input(f"\n{Colors.BOLD}> {Colors.ENDC}").strip()

            # Обработка команд
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                print_header("ДО СВИДАНИЯ!")
                print_info("Спасибо за использование программы!")
                break

            elif user_input.lower() == "help":
                show_help()

            elif user_input.lower() == "demo":
                run_demo()

            elif user_input.lower() == "clear":
                clear_screen()
                show_welcome()

            elif user_input.lower() == "history":
                if history:
                    print_header("ИСТОРИЯ ВЫРАЖЕНИЙ")
                    for i, expr in enumerate(history, 1):
                        print(f"  {i}. {expr}")
                else:
                    print_info("История пуста")

            else:
                # Обрабатываем как логическое выражение
                result = process_function(user_input, show_details=False)

                if result is not None:
                    # Добавляем в историю
                    if not history or history[-1] != user_input:
                        history.append(user_input)

                    # Предлагаем дополнительные действия
                    print(f"\n{Colors.CYAN}Дополнительные действия:{Colors.ENDC}")
                    print(f"  1 - Показать подробный процесс минимизации")
                    print(f"  2 - Показать треугольник Паскаля для полинома Жегалкина")
                    print(f"  3 - Показать карту Карно (если до 5 переменных)")
                    print(f"  Enter - продолжить")

                    choice = input(f"\n{Colors.BOLD}Выбор: {Colors.ENDC}").strip()

                    if choice == "1":
                        print_header("ПОДРОБНАЯ МИНИМИЗАЦИЯ")
                        minimizer = result["minimizer"]
                        print(
                            "\n" + f"{Colors.BOLD}Расчётный метод (ДНФ):{Colors.ENDC}"
                        )
                        minimizer.minimize_quine_dnf(verbose=True)
                        print(
                            "\n"
                            + f"{Colors.BOLD}Расчётно-табличный метод:{Colors.ENDC}"
                        )
                        minimizer.minimize_mccluskey_dnf(verbose=True)
                        if len(result["variables"]) <= 5:
                            print("\n" + f"{Colors.BOLD}Карты Карно:{Colors.ENDC}")
                            minimizer.minimize_karnaugh_dnf(verbose=True)

                    elif choice == "2":
                        print_header("ТРЕУГОЛЬНИК ПАСКАЛЯ")
                        zhg = result["zhg_polynomial"]
                        print(zhg.get_triangle_visualization())

                    elif choice == "3":
                        if len(result["variables"]) <= 5:
                            print_header("КАРТА КАРНО")
                            minimizer = result["minimizer"]
                            minimizer.minimize_karnaugh_dnf(verbose=True)
                        else:
                            print_warning(
                                "Карты Карно поддерживают только до 5 переменных"
                            )

        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Прерывание...{Colors.ENDC}")
            choice = (
                input(f"{Colors.CYAN}Выйти из программы? (y/n): {Colors.ENDC}")
                .strip()
                .lower()
            )
            if choice == "y":
                break

        except EOFError:
            print(f"\n\n{Colors.YELLOW}Входной поток закрыт. Выход...{Colors.ENDC}")
            break

        except Exception as e:
            print_error(f"Неожиданная ошибка: {str(e)}")
            print_info("Попробуйте снова или введите 'help' для справки")


if __name__ == "__main__":
    main()
