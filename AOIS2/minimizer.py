"""
Модуль для минимизации булевых функций
Поддерживает три метода:
1. Расчётный метод (Квайна)
2. Расчётно-табличный метод (Квайна-МакКласки)
3. Табличный метод (карты Карно)
"""

from typing import List, Dict, Set, Tuple
from truth_table import TruthTable
from itertools import combinations

class Minimizer:
    """Минимизатор булевых функций"""
    
    def __init__(self, truth_table: TruthTable):
        """
        Инициализация минимизатора
        
        Args:
            truth_table: таблица истинности функции
        """
        self.tt = truth_table
        self.variables = truth_table.variables
        self.n_vars = len(self.variables)
        
        # Получаем минтермы (наборы, где f=1) для ДНФ
        self.minterms = truth_table.get_minterms()
        
        # Получаем макстермы (наборы, где f=0) для КНФ
        self.maxterms = truth_table.get_maxterms()
        
        # Проверяем, что можем применить методы
        if self.n_vars > 5:
            print("Предупреждение: Карты Карно поддерживают до 5 переменных")
    
    # ========== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ==========
    
    def _to_binary(self, num: int, length: int = None) -> str:
        """
        ПРЕОБРАЗУЕТ ЧИСЛО В ДВОИЧНУЮ СТРОКУ ЗАДАННОЙ ДЛИНЫ
        
        Args:
            num: число для преобразования
            length: длина строки (если None, используется n_vars)
            
        Returns:
            Двоичная строка, например: 5 -> "101"
            
        Примеры:
            _to_binary(5, 3) -> "101"
            _to_binary(2, 4) -> "0010"
        """
        if length is None:
            length = self.n_vars
        return format(num, f'0{length}b')
    
    def _count_ones(self, binary_str: str) -> int:
        """
        ПОДСЧИТЫВАЕТ КОЛИЧЕСТВО ЕДИНИЦ В ДВОИЧНОЙ СТРОКЕ
        
        Это нужно для группировки импликант по числу единиц
        
        Примеры:
            _count_ones("101") -> 2
            _count_ones("000") -> 0
        """
        return binary_str.count('1')
    
    def _differ_by_one_bit(self, imp1: str, imp2: str) -> Tuple[bool, str]:
        """
        ПРОВЕРЯЕТ, ОТЛИЧАЮТСЯ ЛИ ДВЕ ИМПЛИКАНТЫ В ОДНОМ БИТЕ
        
        Импликанты могут содержать символы '0', '1', '-'
        '-' означает отсутствие переменной (уже склеенный бит)
        
        Args:
            imp1, imp2: строки импликант одинаковой длины
            
        Returns:
            (отличаются_ли_в_одном_бите, результат_склеивания)
            
        Примеры:
            _differ_by_one_bit("100", "101") -> (True, "10-")
            _differ_by_one_bit("1-0", "1-1") -> (True, "1--")
            _differ_by_one_bit("100", "110") -> (False, "")
        """
        if len(imp1) != len(imp2):
            return False, ""
        
        diff_count = 0
        diff_pos = -1
        result = list(imp1)
        
        for i in range(len(imp1)):
            if imp1[i] != imp2[i]:
                # Проверяем, что отличающиеся биты не являются '-'
                if imp1[i] == '-' or imp2[i] == '-':
                    return False, ""
                diff_count += 1
                diff_pos = i
                result[i] = '-'
        
        if diff_count == 1:
            return True, ''.join(result)
        return False, ""
    
    def _implicant_to_expression(self, implicant: str, negative: bool = False) -> str:
        """
        ПРЕОБРАЗУЕТ ИМПЛИКАНТУ В ЛОГИЧЕСКОЕ ВЫРАЖЕНИЕ
        
        Args:
            implicant: строка вида "10-1" (0, 1, -)
            negative: True для КНФ (инверсная логика)
            
        Returns:
            Строка с выражением, например "a & !b & d"
            
        Примеры:
            _implicant_to_expression("10-1") -> "a & !b & d"
            _implicant_to_expression("1-0") -> "a & !c"
        """
        literals = []
        
        for i, char in enumerate(implicant):
            if char == '-':
                continue  # Переменная отсутствует
            
            var = self.variables[i]
            
            if negative:
                # Для КНФ: 0 -> переменная, 1 -> отрицание
                if char == '0':
                    literals.append(var)
                else:  # char == '1'
                    literals.append(f"!{var}")
            else:
                # Для ДНФ: 1 -> переменная, 0 -> отрицание
                if char == '1':
                    literals.append(var)
                else:  # char == '0'
                    literals.append(f"!{var}")
        
        if not literals:
            return "1" if not negative else "0"
        
        if negative:
            # Для КНФ соединяем через |
            return f"({' | '.join(literals)})"
        else:
            # Для ДНФ соединяем через &
            return f"({' & '.join(literals)})"
    
    def _remove_redundant_implicants(self, implicants: List[str], 
                                    minterms: List[int]) -> List[str]:
        """
        УДАЛЯЕТ ЛИШНИЕ ИМПЛИКАНТЫ (метод Петрика или проверка покрытия)
        
        Args:
            implicants: список импликант
            minterms: список минтермов, которые нужно покрыть
            
        Returns:
            Список нелишних импликант
        """
        # Строим таблицу покрытия
        coverage = {}
        for imp in implicants:
            covered = self._get_covered_minterms(imp)
            coverage[imp] = set(covered) & set(minterms)
        
        # Находим существенные импликанты
        essential = set()
        all_minterms = set(minterms)
        
        # Проверяем каждый минтерм
        for mt in minterms:
            covering_imps = [imp for imp in implicants if mt in coverage[imp]]
            if len(covering_imps) == 1:
                # Если минтерм покрывается только одной импликантой,
                # эта импликанта существенна
                essential.add(covering_imps[0])
        
        # Покрываем оставшиеся минтермы
        covered_by_essential = set()
        for imp in essential:
            covered_by_essential.update(coverage[imp])
        
        remaining_minterms = all_minterms - covered_by_essential
        
        if not remaining_minterms:
            return list(essential)
        
        # Для оставшихся выбираем минимальное покрытие (жадный алгоритм)
        remaining_imps = [imp for imp in implicants if imp not in essential]
        
        while remaining_minterms:
            # Выбираем импликанту, покрывающую больше всего оставшихся минтермов
            best_imp = None
            best_coverage = set()
            
            for imp in remaining_imps:
                current_coverage = coverage[imp] & remaining_minterms
                if len(current_coverage) > len(best_coverage):
                    best_imp = imp
                    best_coverage = current_coverage
            
            if best_imp is None:
                break
                
            essential.add(best_imp)
            remaining_minterms -= best_coverage
            remaining_imps.remove(best_imp)
        
        return list(essential)
    
    def _get_covered_minterms(self, implicant: str) -> List[int]:
        """
        ВОЗВРАЩАЕТ СПИСОК МИНТЕРМОВ, ПОКРЫВАЕМЫХ ИМПЛИКАНТОЙ
        
        Args:
            implicant: строка с '-' (например "1-0")
            
        Returns:
            Список номеров минтермов
        """
        # Находим позиции '-'
        dash_positions = [i for i, c in enumerate(implicant) if c == '-']
        
        if not dash_positions:
            # Нет '-' - только один минтерм
            return [int(implicant, 2)]
        
        # Генерируем все комбинации для позиций с '-'
        covered = []
        num_dashes = len(dash_positions)
        
        for i in range(2 ** num_dashes):
            # Создаём копию импликанты
            temp = list(implicant)
            
            # Заполняем позиции с '-' значениями из i
            for j, pos in enumerate(dash_positions):
                bit = (i >> (num_dashes - 1 - j)) & 1
                temp[pos] = str(bit)
            
            # Преобразуем в число
            binary_str = ''.join(temp)
            covered.append(int(binary_str, 2))
        
        return sorted(covered)
    
    # ========== 1. РАСЧЁТНЫЙ МЕТОД (КВАЙНА) ==========
    
    def minimize_quine_dnf(self, verbose: bool = True) -> str:
        """
        МИНИМИЗАЦИЯ ДНФ РАСЧЁТНЫМ МЕТОДОМ КВАЙНА
        
        Алгоритм:
        1. Находим все простые импликанты (склеивание)
        2. Удаляем лишние импликанты (проверка покрытия)
        
        Args:
            verbose: выводить ли промежуточные этапы
            
        Returns:
            Строка с минимизированной ДНФ
        """
        if verbose:
            print("\n" + "=" * 60)
            print("МИНИМИЗАЦИЯ ДНФ РАСЧЁТНЫМ МЕТОДОМ (КВАЙНА)")
            print("=" * 60)
            print(f"\nИсходные минтермы: {self.minterms}")
        
        if not self.minterms:
            return "0"
        
        # Этап 1: Нахождение простых импликант
        current_implicants = [self._to_binary(mt) for mt in self.minterms]
        all_implicants = set()
        stage = 1
        
        if verbose:
            print(f"\nЭтап {stage}: Склеивание")
            print(f"Исходные импликанты ({len(current_implicants)} шт.):")
            print(current_implicants)
        
        while True:
            next_implicants = set()
            used = set()
            
            # Группируем по количеству единиц для оптимизации
            groups = {}
            for imp in current_implicants:
                ones = self._count_ones(imp)
                if ones not in groups:
                    groups[ones] = []
                groups[ones].append(imp)
            
            # Склеиваем импликанты из соседних групп
            for ones in sorted(groups.keys()):
                if ones + 1 not in groups:
                    continue
                    
                for imp1 in groups[ones]:
                    for imp2 in groups[ones + 1]:
                        can_merge, merged = self._differ_by_one_bit(imp1, imp2)
                        if can_merge:
                            next_implicants.add(merged)
                            used.add(imp1)
                            used.add(imp2)
            
            # Сохраняем неиспользованные импликанты (простые)
            for imp in current_implicants:
                if imp not in used:
                    all_implicants.add(imp)
            
            if not next_implicants:
                break
                
            current_implicants = list(next_implicants)
            stage += 1
            
            if verbose:
                print(f"\nЭтап {stage}: Результат склеивания")
                print(f"Получено импликант: {len(current_implicants)}")
                print(current_implicants)
        
        # Этап 2: Удаление лишних импликант
        if verbose:
            print(f"\nЭтап {stage + 1}: Удаление лишних импликант")
            print(f"Всего простых импликант: {len(all_implicants)}")
        
        essential = self._remove_redundant_implicants(list(all_implicants), self.minterms)
        
        if verbose:
            print(f"Существенных импликант: {len(essential)}")
            print("Выражения:")
            for imp in essential:
                print(f"  {imp} -> {self._implicant_to_expression(imp)}")
        
        # Формируем результат
        result_terms = [self._implicant_to_expression(imp) for imp in essential]
        result = ' | '.join(result_terms)
        
        if verbose:
            print(f"\nРЕЗУЛЬТАТ ДНФ: f = {result}")
        
        return result
    
    def minimize_quine_knf(self, verbose: bool = True) -> str:
        """
        МИНИМИЗАЦИЯ КНФ РАСЧЁТНЫМ МЕТОДОМ
        
        Алгоритм аналогичен ДНФ, но работаем с макстермами
        и используем инверсную логику
        
        Args:
            verbose: выводить ли промежуточные этапы
            
        Returns:
            Строка с минимизированной КНФ
        """
        if verbose:
            print("\n" + "=" * 60)
            print("МИНИМИЗАЦИЯ КНФ РАСЧЁТНЫМ МЕТОДОМ")
            print("=" * 60)
            print(f"\nИсходные макстермы: {self.maxterms}")
        
        if not self.maxterms:
            return "1"
        
        # Для КНФ работаем с инвертированными значениями (0<->1)
        # Макстермы - это наборы где f=0
        
        current_implicants = [self._to_binary(mt) for mt in self.maxterms]
        all_implicants = set()
        
        if verbose:
            print(f"\nЭтап 1: Склеивание макстермов")
            print(f"Исходные импликанты ({len(current_implicants)} шт.):")
            print(current_implicants)
        
        while True:
            next_implicants = set()
            used = set()
            
            for i, imp1 in enumerate(current_implicants):
                for j, imp2 in enumerate(current_implicants):
                    if i >= j:
                        continue
                    can_merge, merged = self._differ_by_one_bit(imp1, imp2)
                    if can_merge:
                        next_implicants.add(merged)
                        used.add(imp1)
                        used.add(imp2)
            
            for imp in current_implicants:
                if imp not in used:
                    all_implicants.add(imp)
            
            if not next_implicants:
                break
                
            current_implicants = list(next_implicants)
            
            if verbose:
                print(f"\nРезультат склеивания: {len(current_implicants)} импликант")
                print(current_implicants)
        
        # Удаление лишних
        essential = self._remove_redundant_implicants(list(all_implicants), self.maxterms)
        
        # Формируем КНФ (с инверсией)
        result_terms = [self._implicant_to_expression(imp, negative=True) for imp in essential]
        result = ' & '.join(result_terms)
        
        if verbose:
            print(f"\nРЕЗУЛЬТАТ КНФ: f = {result}")
        
        return result
    
    # ========== 2. РАСЧЁТНО-ТАБЛИЧНЫЙ МЕТОД (КВАЙНА-МАККЛАСКИ) ==========
    
    def minimize_mccluskey_dnf(self, verbose: bool = True) -> str:
        """
        МИНИМИЗАЦИЯ ДНФ РАСЧЁТНО-ТАБЛИЧНЫМ МЕТОДОМ
        
        Отличие от расчётного: выводим таблицу покрытия
        """
        if verbose:
            print("\n" + "=" * 60)
            print("МИНИМИЗАЦИЯ ДНФ РАСЧЁТНО-ТАБЛИЧНЫМ МЕТОДОМ (Квайна-МакКласки)")
            print("=" * 60)
        
        # Этап склеивания (как в расчётном методе)
        if verbose:
            print("\n=== ЭТАП 1: СКЛЕИВАНИЕ ===")
        
        current_implicants = [self._to_binary(mt) for mt in self.minterms]
        all_implicants = set()
        stage = 1
        
        # Группируем для вывода
        groups = {}
        for imp in current_implicants:
            ones = self._count_ones(imp)
            if ones not in groups:
                groups[ones] = []
            groups[ones].append(imp)
        
        if verbose:
            print(f"\nГруппировка по числу единиц:")
            for ones in sorted(groups.keys()):
                print(f"  {ones} единиц: {groups[ones]}")
        
        while True:
            next_implicants = set()
            used = set()
            merges = []  # Для вывода
            
            for i, imp1 in enumerate(current_implicants):
                for j, imp2 in enumerate(current_implicants):
                    if i >= j:
                        continue
                    can_merge, merged = self._differ_by_one_bit(imp1, imp2)
                    if can_merge:
                        next_implicants.add(merged)
                        used.add(imp1)
                        used.add(imp2)
                        merges.append((imp1, imp2, merged))
            
            if verbose and merges:
                print(f"\nСклеивание (этап {stage}):")
                for imp1, imp2, merged in merges[:5]:  # Показываем первые 5
                    print(f"  {imp1} ∨ {imp2} => {merged}")
                if len(merges) > 5:
                    print(f"  ... и ещё {len(merges) - 5} склеиваний")
            
            for imp in current_implicants:
                if imp not in used:
                    all_implicants.add(imp)
            
            if not next_implicants:
                break
                
            current_implicants = list(next_implicants)
            stage += 1
        
        # Этап 2: Построение таблицы покрытия
        if verbose:
            print("\n=== ЭТАП 2: ТАБЛИЦА ПОКРЫТИЯ ===")
            self._print_coverage_table(list(all_implicants), self.minterms)
        
        # Удаление лишних
        essential = self._remove_redundant_implicants(list(all_implicants), self.minterms)
        
        # Результат
        result_terms = [self._implicant_to_expression(imp) for imp in essential]
        result = ' | '.join(result_terms)
        
        if verbose:
            print(f"\n=== РЕЗУЛЬТАТ ===")
            print(f"f = {result}")
        
        return result
    
    def _print_coverage_table(self, implicants: List[str], minterms: List[int]):
        """
        ВЫВОДИТ ТАБЛИЦУ ПОКРЫТИЯ
        """
        # Заголовок
        header = "Импликанта | " + " | ".join([f"{mt:2d}" for mt in minterms])
        print(header)
        print("-" * len(header))
        
        for imp in implicants:
            covered = self._get_covered_minterms(imp)
            row = f"{imp:11} | "
            for mt in minterms:
                if mt in covered:
                    row += " X |"
                else:
                    row += "   |"
            print(row)
    
    # ========== 3. ТАБЛИЧНЫЙ МЕТОД (КАРТЫ КАРНО) ==========
    
    def minimize_karnaugh_dnf(self, verbose: bool = True) -> str:
        """
        МИНИМИЗАЦИЯ ДНФ МЕТОДОМ КАРТ КАРНО
        
        Поддерживает от 2 до 5 переменных
        """
        if verbose:
            print("\n" + "=" * 60)
            print("МИНИМИЗАЦИЯ ДНФ МЕТОДОМ КАРТ КАРНО")
            print("=" * 60)
        
        if self.n_vars == 2:
            return self._karnaugh_2_vars(verbose)
        elif self.n_vars == 3:
            return self._karnaugh_3_vars(verbose)
        elif self.n_vars == 4:
            return self._karnaugh_4_vars(verbose)
        elif self.n_vars == 5:
            return self._karnaugh_5_vars(verbose)
        else:
            return "Карты Карно поддерживают только 2-5 переменных"
    
    def _karnaugh_2_vars(self, verbose: bool) -> str:
        """Карта Карно для 2 переменных"""
        # Карта 2x2
        #   b
        # a 0 1
        # 0
        # 1
        
        if verbose:
            print("\nКарта Карно (2 переменные):")
            print("   b")
            print("a  0 1")
            
            for a in [0, 1]:
                row = f"{a}  "
                for b in [0, 1]:
                    idx = (a << 1) | b
                    val = 1 if idx in self.minterms else 0
                    row += f"{val} "
                print(row)
        
        # Поиск областей (упрощённо)
        return self._find_regions_2_vars()
    
    def _karnaugh_3_vars(self, verbose: bool) -> str:
        """Карта Карно для 3 переменных"""
        # Карта 2x4
        #    bc
        # a  00 01 11 10
        # 0
        # 1
        
        if verbose:
            print("\nКарта Карно (3 переменные):")
            print("    bc")
            print("a   00 01 11 10")
            print("-" * 20)
            
            # Коды Грея для bc: 00, 01, 11, 10
            gray_codes = [(0,0), (0,1), (1,1), (1,0)]
            
            for a in [0, 1]:
                row = f"{a}   "
                for b, c in gray_codes:
                    idx = (a << 2) | (b << 1) | c
                    val = 1 if idx in self.minterms else 0
                    row += f" {val}  "
                print(row)
        
        return self._find_regions_3_vars(verbose)
    
    def _karnaugh_4_vars(self, verbose: bool) -> str:
        """Карта Карно для 4 переменных"""
        # Карта 4x4
        #      cd
        # ab   00 01 11 10
        # 00
        # 01
        # 11
        # 10
        
        if verbose:
            print("\nКарта Карно (4 переменные):")
            print("      cd")
            print("ab    00 01 11 10")
            print("-" * 25)
            
            # Коды Грея для ab и cd
            gray_ab = [(0,0), (0,1), (1,1), (1,0)]
            gray_cd = [(0,0), (0,1), (1,1), (1,0)]
            
            for a, b in gray_ab:
                row = f"{a}{b}   "
                for c, d in gray_cd:
                    idx = (a << 3) | (b << 2) | (c << 1) | d
                    val = 1 if idx in self.minterms else 0
                    row += f" {val}  "
                print(row)
        
        return self._find_regions_4_vars(verbose)
    
    def _karnaugh_5_vars(self, verbose: bool) -> str:
        """Карта Карно для 5 переменных (две 4x4 карты)"""
        if verbose:
            print("\nКарта Карно (5 переменных) - две карты 4x4:")
            print("\nДля e=0:")
            print("      cd")
            print("ab    00 01 11 10")
            print("-" * 25)
            
            gray_ab = [(0,0), (0,1), (1,1), (1,0)]
            gray_cd = [(0,0), (0,1), (1,1), (1,0)]
            
            for a, b in gray_ab:
                row = f"{a}{b}   "
                for c, d in gray_cd:
                    idx = (a << 4) | (b << 3) | (c << 2) | (d << 1) | 0
                    val = 1 if idx in self.minterms else 0
                    row += f" {val}  "
                print(row)
            
            print("\nДля e=1:")
            print("      cd")
            print("ab    00 01 11 10")
            print("-" * 25)
            
            for a, b in gray_ab:
                row = f"{a}{b}   "
                for c, d in gray_cd:
                    idx = (a << 4) | (b << 3) | (c << 2) | (d << 1) | 1
                    val = 1 if idx in self.minterms else 0
                    row += f" {val}  "
                print(row)
        
        return self._find_regions_5_vars(verbose)
    
    def _find_regions_2_vars(self) -> str:
        """Поиск областей для 2 переменных"""
        regions = []
        minterms_set = set(self.minterms)
        
        # Проверяем возможные области
        # Одиночные клетки
        for mt in self.minterms:
            regions.append({mt})
        
        # Пары
        pairs = [
            {0, 1},  # !a
            {2, 3},  # a
            {0, 2},  # !b
            {1, 3},  # b
        ]
        
        # Квартет (вся карта)
        if len(self.minterms) == 4:
            return "1"
        
        # Выбираем минимальное покрытие
        covered = set()
        selected_regions = []
        
        # Сначала большие области
        for region in pairs:
            if region.issubset(minterms_set) and not region.issubset(covered):
                selected_regions.append(region)
                covered.update(region)
        
        # Добавляем оставшиеся
        for mt in self.minterms:
            if mt not in covered:
                selected_regions.append({mt})
        
        # Преобразуем в выражения
        terms = []
        for region in selected_regions:
            terms.append(self._region_to_expression_2(region))
        
        return ' | '.join(terms) if terms else "0"
    
    def _region_to_expression_2(self, region: Set[int]) -> str:
        """Преобразует область в выражение для 2 переменных"""
        if len(region) == 1:
            mt = list(region)[0]
            a, b = (mt >> 1) & 1, mt & 1
            literals = []
            if a: literals.append('a')
            else: literals.append('!a')
            if b: literals.append('b')
            else: literals.append('!b')
            return f"({' & '.join(literals)})"
        elif region == {0, 1}:
            return "(!a)"
        elif region == {2, 3}:
            return "(a)"
        elif region == {0, 2}:
            return "(!b)"
        elif region == {1, 3}:
            return "(b)"
        return ""
    
    def _find_regions_3_vars(self, verbose: bool) -> str:
        """Упрощённый поиск областей для 3 переменных"""
        # В реальном коде здесь должен быть алгоритм поиска
        # максимальных прямоугольных областей на карте Карно
        # Для простоты используем уже реализованный метод Квайна
        if verbose:
            print("\nПоиск областей...")
        return self.minimize_quine_dnf(verbose=False)
    
    def _find_regions_4_vars(self, verbose: bool) -> str:
        """Упрощённый поиск областей для 4 переменных"""
        if verbose:
            print("\nПоиск областей...")
        return self.minimize_quine_dnf(verbose=False)
    
    def _find_regions_5_vars(self, verbose: bool) -> str:
        """Упрощённый поиск областей для 5 переменных"""
        if verbose:
            print("\nПоиск областей...")
        return self.minimize_quine_dnf(verbose=False)
    
    # ========== ОБЩИЙ МЕТОД ВЫВОДА ==========
    
    def print_all_methods(self):
        """
        ВЫВОД РЕЗУЛЬТАТОВ ВСЕХ МЕТОДОВ МИНИМИЗАЦИИ
        """
        print("\n" + "=" * 70)
        print("МИНИМИЗАЦИЯ БУЛЕВОЙ ФУНКЦИИ")
        print("=" * 70)
        
        # 1. Расчётный метод
        dnf_quine = self.minimize_quine_dnf(verbose=True)
        knf_quine = self.minimize_quine_knf(verbose=False)
        
        # 2. Расчётно-табличный метод
        dnf_mccluskey = self.minimize_mccluskey_dnf(verbose=True)
        
        # 3. Карты Карно
        if self.n_vars <= 5:
            dnf_karnaugh = self.minimize_karnaugh_dnf(verbose=True)
            
            print("\n" + "=" * 70)
            print("СРАВНЕНИЕ РЕЗУЛЬТАТОВ")
            print("=" * 70)
            print(f"Метод Квайна (ДНФ):      {dnf_quine}")
            print(f"Метод Квайна-МакКласки:  {dnf_mccluskey}")
            print(f"Метод Карт Карно:        {dnf_karnaugh}")
            print(f"Метод Квайна (КНФ):      {knf_quine}")