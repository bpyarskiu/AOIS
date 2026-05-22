#!/usr/bin/env python3
"""
Модульные тесты для хеш-таблицы с АВЛ-деревьями.
"""

import unittest
import sys
import os

# Добавляем путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hash_table import AVLNode, AVLTree, HashTable


class TestAVLNode(unittest.TestCase):
    """Тесты для узла АВЛ-дерева."""

    def test_node_creation(self):
        """Тест создания узла."""
        node = AVLNode("key1", "value1")
        self.assertEqual(node.key, "key1")
        self.assertEqual(node.value, "value1")
        self.assertEqual(node.height, 1)
        self.assertIsNone(node.left)
        self.assertIsNone(node.right)

    def test_node_with_different_types(self):
        """Тест узла с разными типами данных."""
        node = AVLNode(123, [1, 2, 3])
        self.assertEqual(node.key, 123)
        self.assertEqual(node.value, [1, 2, 3])

        node2 = AVLNode("key", None)
        self.assertIsNone(node2.value)


class TestAVLTree(unittest.TestCase):
    """Тесты для АВЛ-дерева."""

    def setUp(self):
        self.tree = AVLTree()

    def test_empty_tree(self):
        """Тест пустого дерева."""
        self.assertIsNone(self.tree.root)
        self.assertTrue(self.tree.is_empty())
        self.assertEqual(len(self.tree.get_all_items()), 0)

    def test_insert_single(self):
        """Тест вставки одного элемента."""
        self.tree.insert("b", 2)
        self.assertFalse(self.tree.is_empty())
        self.assertEqual(self.tree.search("b"), 2)
        self.assertEqual(len(self.tree.get_all_items()), 1)

    def test_insert_multiple(self):
        """Тест вставки нескольких элементов."""
        data = [("c", 3), ("a", 1), ("b", 2), ("e", 5), ("d", 4)]
        for key, value in data:
            self.tree.insert(key, value)

        for key, value in data:
            self.assertEqual(self.tree.search(key), value)

        self.assertEqual(len(self.tree.get_all_items()), 5)

    def test_insert_duplicate_key(self):
        """Тест вставки дубликата ключа (обновление значения)."""
        self.tree.insert("a", 1)
        self.tree.insert("a", 100)
        self.assertEqual(self.tree.search("a"), 100)
        self.assertEqual(len(self.tree.get_all_items()), 1)

    def test_search_empty_tree(self):
        """Тест поиска в пустом дереве."""
        self.assertIsNone(self.tree.search("anything"))

    def test_search_nonexistent(self):
        """Тест поиска несуществующего ключа."""
        self.tree.insert("a", 1)
        self.tree.insert("b", 2)
        self.assertIsNone(self.tree.search("c"))
        self.assertIsNone(self.tree.search("z"))

    def test_delete_leaf(self):
        """Тест удаления листового узла."""
        self.tree.insert("b", 2)
        self.tree.insert("a", 1)
        self.tree.insert("c", 3)

        self.tree.delete("a")
        self.assertIsNone(self.tree.search("a"))
        self.assertEqual(self.tree.search("b"), 2)
        self.assertEqual(self.tree.search("c"), 3)
        self.assertEqual(len(self.tree.get_all_items()), 2)

    def test_delete_node_with_one_child(self):
        """Тест удаления узла с одним потомком."""
        self.tree.insert("b", 2)
        self.tree.insert("a", 1)
        self.tree.insert("c", 3)
        self.tree.insert("d", 4)

        self.tree.delete("c")
        self.assertIsNone(self.tree.search("c"))
        self.assertEqual(self.tree.search("d"), 4)
        self.assertEqual(len(self.tree.get_all_items()), 3)

    def test_delete_node_with_two_children(self):
        """Тест удаления узла с двумя потомками."""
        self.tree.insert("c", 3)
        self.tree.insert("a", 1)
        self.tree.insert("b", 2)
        self.tree.insert("e", 5)
        self.tree.insert("d", 4)

        self.tree.delete("c")
        self.assertIsNone(self.tree.search("c"))
        self.assertEqual(len(self.tree.get_all_items()), 4)
        # Проверяем, что все остальные ключи на месте
        for key in ["a", "b", "d", "e"]:
            self.assertIsNotNone(self.tree.search(key))

    def test_delete_from_empty_tree(self):
        """Тест удаления из пустого дерева."""
        self.tree.delete("a")
        self.assertTrue(self.tree.is_empty())

    def test_delete_nonexistent(self):
        """Тест удаления несуществующего ключа."""
        self.tree.insert("a", 1)
        self.tree.delete("b")
        self.assertEqual(len(self.tree.get_all_items()), 1)
        self.assertEqual(self.tree.search("a"), 1)

    def test_delete_root(self):
        """Тест удаления корневого узла."""
        self.tree.insert("b", 2)
        self.tree.insert("a", 1)
        self.tree.insert("c", 3)

        self.tree.delete("b")
        self.assertIsNone(self.tree.search("b"))
        self.assertEqual(len(self.tree.get_all_items()), 2)

    def test_balance_after_insert_left_left(self):
        """Тест балансировки Left-Left случай."""
        self.tree.insert("c", 3)
        self.tree.insert("b", 2)
        self.tree.insert("a", 1)

        # Дерево должно быть сбалансировано, "b" должен быть корнем
        self.assertEqual(self.tree.root.key, "b")
        self.assertEqual(self.tree.root.left.key, "a")
        self.assertEqual(self.tree.root.right.key, "c")

    def test_balance_after_insert_right_right(self):
        """Тест балансировки Right-Right случай."""
        self.tree.insert("a", 1)
        self.tree.insert("b", 2)
        self.tree.insert("c", 3)

        # Дерево должно быть сбалансировано, "b" должен быть корнем
        self.assertEqual(self.tree.root.key, "b")
        self.assertEqual(self.tree.root.left.key, "a")
        self.assertEqual(self.tree.root.right.key, "c")

    def test_balance_after_insert_left_right(self):
        """Тест балансировки Left-Right случай."""
        self.tree.insert("c", 3)
        self.tree.insert("a", 1)
        self.tree.insert("b", 2)

        # "b" должен стать корнем после балансировки
        self.assertEqual(self.tree.root.key, "b")
        self.assertEqual(self.tree.root.left.key, "a")
        self.assertEqual(self.tree.root.right.key, "c")

    def test_balance_after_insert_right_left(self):
        """Тест балансировки Right-Left случай."""
        self.tree.insert("a", 1)
        self.tree.insert("c", 3)
        self.tree.insert("b", 2)

        # "b" должен стать корнем после балансировки
        self.assertEqual(self.tree.root.key, "b")
        self.assertEqual(self.tree.root.left.key, "a")
        self.assertEqual(self.tree.root.right.key, "c")

    def test_balance_after_delete(self):
        """Тест балансировки после удаления."""
        self.tree.insert("d", 4)
        self.tree.insert("b", 2)
        self.tree.insert("f", 6)
        self.tree.insert("a", 1)
        self.tree.insert("c", 3)
        self.tree.insert("e", 5)

        # Удаляем "a", что может нарушить баланс
        self.tree.delete("a")

        # Проверяем, что дерево сбалансировано (разница высот <= 1)
        self._check_balance(self.tree.root)

        # Проверяем, что все оставшиеся ключи доступны
        for key in ["b", "c", "d", "e", "f"]:
            self.assertIsNotNone(
                self.tree.search(key), f"Ключ {key} должен быть найден"
            )

    def _check_balance(self, node):
        """Рекурсивная проверка балансировки дерева."""
        if node is None:
            return True

        balance = abs(
            (node.left.height if node.left else 0)
            - (node.right.height if node.right else 0)
        )

        self.assertLessEqual(balance, 1, f"Нарушен баланс в узле {node.key}")

        self._check_balance(node.left)
        self._check_balance(node.right)

    def test_get_all_items_sorted(self):
        """Тест получения всех элементов (должны быть отсортированы)."""
        self.tree.insert("c", 3)
        self.tree.insert("a", 1)
        self.tree.insert("b", 2)
        self.tree.insert("e", 5)
        self.tree.insert("d", 4)

        items = self.tree.get_all_items()
        keys = [item[0] for item in items]
        self.assertEqual(keys, ["a", "b", "c", "d", "e"])

    def test_get_keys(self):
        """Тест получения всех ключей."""
        self.tree.insert("b", 2)
        self.tree.insert("a", 1)
        self.tree.insert("c", 3)

        self.assertEqual(self.tree.get_keys(), ["a", "b", "c"])

    def test_get_values(self):
        """Тест получения всех значений."""
        self.tree.insert("b", 2)
        self.tree.insert("a", 1)
        self.tree.insert("c", 3)

        self.assertEqual(self.tree.get_values(), [1, 2, 3])

    def test_large_tree_balance(self):
        """Тест балансировки большого дерева."""
        import random

        random.seed(42)

        keys = list(range(100))
        random.shuffle(keys)

        for key in keys:
            self.tree.insert(key, f"value_{key}")

        # Проверяем балансировку
        self._check_balance(self.tree.root)

        # Проверяем, что все элементы доступны
        for key in keys:
            self.assertEqual(self.tree.search(key), f"value_{key}")

    def test_large_tree_delete(self):
        """Тест удаления из большого дерева."""
        import random

        random.seed(42)

        keys = list(range(50))
        random.shuffle(keys)

        for key in keys:
            self.tree.insert(key, f"value_{key}")

        # Удаляем половину ключей
        to_delete = random.sample(keys, 25)
        for key in to_delete:
            self.tree.delete(key)

        # Проверяем балансировку
        if self.tree.root:
            self._check_balance(self.tree.root)

        # Проверяем, что удалённые ключи отсутствуют
        for key in to_delete:
            self.assertIsNone(self.tree.search(key))

        # Проверяем, что оставшиеся ключи доступны
        remaining = set(keys) - set(to_delete)
        for key in remaining:
            self.assertIsNotNone(self.tree.search(key))


class TestHashTable(unittest.TestCase):
    """Тесты для хеш-таблицы."""

    def setUp(self):
        self.ht = HashTable(initial_capacity=8)

    # --- Тесты хеш-функции ---
    def test_hash_function_basic(self):
        """Тест базовой работы хеш-функции."""
        index = self.ht._hash_function("абв")
        self.assertIsInstance(index, int)
        self.assertGreaterEqual(index, 0)
        self.assertLess(index, self.ht.capacity)

    def test_hash_function_same_key_same_hash(self):
        """Тест: одинаковые ключи дают одинаковый хеш."""
        h1 = self.ht._hash_function("привет")
        h2 = self.ht._hash_function("привет")
        self.assertEqual(h1, h2)

    def test_hash_function_different_keys(self):
        """Тест: разные ключи дают разные хеши (не всегда, но обычно)."""
        h1 = self.ht._hash_function("абв")
        h2 = self.ht._hash_function("где")
        # Технически они могут совпасть, но функция должна работать
        self.assertIsInstance(h1, int)
        self.assertIsInstance(h2, int)

    def test_hash_function_single_char(self):
        """Тест хеш-функции с одним символом."""
        index = self.ht._hash_function("а")
        self.assertGreaterEqual(index, 0)
        self.assertLess(index, self.ht.capacity)

    def test_hash_function_empty_string(self):
        """Тест хеш-функции с пустой строкой."""
        index = self.ht._hash_function("")
        self.assertEqual(index, 0)

    def test_hash_function_non_russian(self):
        """Тест хеш-функции с не-русскими символами."""
        index = self.ht._hash_function("abc")
        self.assertGreaterEqual(index, 0)
        self.assertLess(index, self.ht.capacity)

    def test_hash_function_with_yo(self):
        """Тест хеш-функции с буквой 'ё'."""
        index1 = self.ht._hash_function("ёж")
        index2 = self.ht._hash_function("ёж")
        self.assertEqual(index1, index2)

    # --- CRUD операции ---
    def test_put_and_get(self):
        """Тест вставки и получения элемента."""
        self.ht.put("Иванов", 25)
        self.assertEqual(self.ht.get("Иванов"), 25)

    def test_put_multiple(self):
        """Тест вставки нескольких элементов."""
        data = [
            ("Иванов", 25),
            ("Петров", 30),
            ("Сидоров", 35),
        ]
        for key, value in data:
            self.ht.put(key, value)

        for key, value in data:
            self.assertEqual(self.ht.get(key), value)

    def test_put_update_existing(self):
        """Тест обновления существующего элемента."""
        self.ht.put("Иванов", 25)
        self.ht.put("Иванов", 26)
        self.assertEqual(self.ht.get("Иванов"), 26)
        self.assertEqual(self.ht.get_size(), 1)

    def test_get_nonexistent(self):
        """Тест получения несуществующего элемента."""
        self.assertIsNone(self.ht.get("Несуществующий"))

    def test_get_from_empty_table(self):
        """Тест получения из пустой таблицы."""
        self.assertIsNone(self.ht.get("любой"))

    def test_remove_existing(self):
        """Тест удаления существующего элемента."""
        self.ht.put("Иванов", 25)
        result = self.ht.remove("Иванов")
        self.assertTrue(result)
        self.assertIsNone(self.ht.get("Иванов"))
        self.assertEqual(self.ht.get_size(), 0)

    def test_remove_nonexistent(self):
        """Тест удаления несуществующего элемента."""
        result = self.ht.remove("Несуществующий")
        self.assertFalse(result)

    def test_remove_from_empty_table(self):
        """Тест удаления из пустой таблицы."""
        result = self.ht.remove("любой")
        self.assertFalse(result)

    def test_contains_existing(self):
        """Тест contains для существующего элемента."""
        self.ht.put("Иванов", 25)
        self.assertTrue(self.ht.contains("Иванов"))

    def test_contains_nonexistent(self):
        """Тест contains для несуществующего элемента."""
        self.assertFalse(self.ht.contains("Несуществующий"))

    def test_size_after_operations(self):
        """Тест размера таблицы после операций."""
        self.assertEqual(self.ht.get_size(), 0)
        self.ht.put("a", 1)
        self.assertEqual(self.ht.get_size(), 1)
        self.ht.put("b", 2)
        self.assertEqual(self.ht.get_size(), 2)
        self.ht.put("a", 3)  # обновление, не увеличение размера
        self.assertEqual(self.ht.get_size(), 2)
        self.ht.remove("a")
        self.assertEqual(self.ht.get_size(), 1)
        self.ht.remove("b")
        self.assertEqual(self.ht.get_size(), 0)

    def test_is_empty(self):
        """Тест проверки на пустоту."""
        self.assertTrue(self.ht.is_empty())
        self.ht.put("a", 1)
        self.assertFalse(self.ht.is_empty())
        self.ht.remove("a")
        self.assertTrue(self.ht.is_empty())

    def test_clear(self):
        """Тест очистки таблицы."""
        self.ht.put("a", 1)
        self.ht.put("b", 2)
        self.ht.put("c", 3)
        self.ht.clear()
        self.assertTrue(self.ht.is_empty())
        self.assertEqual(self.ht.get_size(), 0)
        self.assertIsNone(self.ht.get("a"))

    # --- Тесты коллизий ---
    def test_collision_handling(self):
        """Тест обработки коллизий."""
        # Создаём таблицу размера 2, чтобы гарантировать коллизии
        small_ht = HashTable(initial_capacity=2)

        data = [
            ("Петров", "инженер"),
            ("Павлов", "врач"),  # Может попасть в ту же корзину
            ("Петрова", "учитель"),
        ]

        for key, value in data:
            small_ht.put(key, value)

        # Проверяем, что все элементы доступны
        for key, value in data:
            self.assertEqual(small_ht.get(key), value)

        self.assertEqual(small_ht.get_size(), 3)

    def test_collision_with_delete(self):
        """Тест удаления при коллизиях."""
        small_ht = HashTable(initial_capacity=2)

        small_ht.put("Иванов", 1)
        small_ht.put("Иванова", 2)
        small_ht.put("Иванченко", 3)

        small_ht.remove("Иванова")

        self.assertIsNone(small_ht.get("Иванова"))
        self.assertEqual(small_ht.get("Иванов"), 1)
        self.assertEqual(small_ht.get("Иванченко"), 3)
        self.assertEqual(small_ht.get_size(), 2)

    # --- Тесты специальных методов ---
    def test_len(self):
        """Тест __len__."""
        self.assertEqual(len(self.ht), 0)
        self.ht.put("a", 1)
        self.assertEqual(len(self.ht), 1)

    def test_contains_dunder(self):
        """Тест оператора in."""
        self.ht.put("Иванов", 25)
        self.assertIn("Иванов", self.ht)
        self.assertNotIn("Петров", self.ht)

    def test_getitem(self):
        """Тест оператора []."""
        self.ht["Иванов"] = 25
        self.assertEqual(self.ht["Иванов"], 25)

    def test_getitem_keyerror(self):
        """Тест KeyError при обращении к несуществующему ключу."""
        with self.assertRaises(KeyError):
            _ = self.ht["несуществующий"]

    def test_setitem(self):
        """Тест оператора присваивания."""
        self.ht["Иванов"] = 25
        self.assertEqual(self.ht["Иванов"], 25)
        self.ht["Иванов"] = 30
        self.assertEqual(self.ht["Иванов"], 30)

    def test_delitem(self):
        """Тест оператора del."""
        self.ht["Иванов"] = 25
        del self.ht["Иванов"]
        self.assertNotIn("Иванов", self.ht)

    def test_delitem_keyerror(self):
        """Тест KeyError при удалении несуществующего ключа."""
        with self.assertRaises(KeyError):
            del self.ht["несуществующий"]

    def test_str(self):
        """Тест строкового представления."""
        self.ht.put("Иванов", 25)
        self.ht.put("Петров", 30)
        s = str(self.ht)
        self.assertIsInstance(s, str)
        self.assertIn("Иванов", s)
        self.assertIn("Петров", s)

    # --- Тесты ошибок ---
    def test_type_error_on_non_string_key(self):
        """Тест TypeError при нестроковом ключе."""
        with self.assertRaises(TypeError):
            self.ht.put(123, "value")

        with self.assertRaises(TypeError):
            self.ht.get(123)

        with self.assertRaises(TypeError):
            self.ht.remove(123)

    # --- Тесты статистики ---
    def test_get_all_items(self):
        """Тест получения всех элементов."""
        self.ht.put("b", 2)
        self.ht.put("a", 1)
        items = self.ht.get_all_items()
        self.assertEqual(len(items), 2)
        # Сортируем для предсказуемости
        items.sort(key=lambda x: x[0])
        self.assertEqual(items, [("a", 1), ("b", 2)])

    def test_get_all_keys(self):
        """Тест получения всех ключей."""
        self.ht.put("b", 2)
        self.ht.put("a", 1)
        keys = sorted(self.ht.get_all_keys())
        self.assertEqual(keys, ["a", "b"])

    def test_get_all_values(self):
        """Тест получения всех значений."""
        self.ht.put("b", 2)
        self.ht.put("a", 1)
        values = sorted(self.ht.get_all_values())
        self.assertEqual(values, [1, 2])

    def test_get_bucket_sizes(self):
        """Тест получения размеров корзин."""
        self.ht.put("Иванов", 1)
        self.ht.put("Петров", 2)
        sizes = self.ht.get_bucket_sizes()
        self.assertEqual(len(sizes), self.ht.capacity)
        self.assertEqual(sum(sizes), 2)

    def test_get_collision_stats(self):
        """Тест статистики коллизий."""
        self.ht.put("Иванов", 1)
        self.ht.put("Петров", 2)
        stats = self.ht.get_collision_stats()

        self.assertIn("total_buckets", stats)
        self.assertIn("non_empty_buckets", stats)
        self.assertIn("empty_buckets", stats)
        self.assertIn("max_bucket_size", stats)
        self.assertIn("total_collisions", stats)
        self.assertIn("load_factor", stats)

        self.assertEqual(stats["total_buckets"], self.ht.capacity)
        self.assertGreaterEqual(stats["non_empty_buckets"], 1)
        self.assertGreaterEqual(stats["total_collisions"], 0)

    # --- Интеграционные тесты ---
    def test_complex_scenario(self):
        """Тест комплексного сценария использования."""
        # Создание записей
        employees = [
            ("Иванов", "инженер"),
            ("Петров", "менеджер"),
            ("Сидоров", "аналитик"),
            ("Кузнецов", "разработчик"),
            ("Андреева", "дизайнер"),
            ("Борисова", "тестировщик"),
        ]

        # Добавление
        for name, role in employees:
            self.ht.put(name, role)

        self.assertEqual(self.ht.get_size(), 6)

        # Поиск
        self.assertEqual(self.ht.get("Петров"), "менеджер")

        # Обновление
        self.ht.put("Петров", "старший менеджер")
        self.assertEqual(self.ht.get("Петров"), "старший менеджер")

        # Удаление
        self.ht.remove("Сидоров")
        self.assertIsNone(self.ht.get("Сидоров"))
        self.assertEqual(self.ht.get_size(), 5)

        # Проверка наличия
        self.assertIn("Иванов", self.ht)
        self.assertNotIn("Сидоров", self.ht)

        # Очистка
        self.ht.clear()
        self.assertTrue(self.ht.is_empty())

    def test_large_table(self):
        """Тест работы с большим количеством элементов."""
        large_ht = HashTable(initial_capacity=32)

        # Добавляем 200 элементов
        for i in range(200):
            key = f"ключ{i:03d}"
            value = f"значение{i}"
            large_ht.put(key, value)

        self.assertEqual(large_ht.get_size(), 200)

        # Проверяем выборку
        for i in [0, 50, 100, 150, 199]:
            self.assertEqual(large_ht.get(f"ключ{i:03d}"), f"значение{i}")

        # Удаляем половину
        for i in range(0, 200, 2):
            large_ht.remove(f"ключ{i:03d}")

        self.assertEqual(large_ht.get_size(), 100)

        # Проверяем, что чётные удалены, нечётные остались
        for i in range(200):
            key = f"ключ{i:03d}"
            if i % 2 == 0:
                self.assertIsNone(large_ht.get(key), f"Ключ {key} должен быть удалён")
            else:
                self.assertIsNotNone(
                    large_ht.get(key), f"Ключ {key} должен существовать"
                )

    def test_different_capacities(self):
        """Тест таблиц с разной ёмкостью."""
        for cap in [1, 2, 5, 10, 50, 100]:
            ht = HashTable(initial_capacity=cap)
            self.assertEqual(ht.capacity, cap)

            ht.put("тест", "значение")
            self.assertEqual(ht.get("тест"), "значение")

            stats = ht.get_collision_stats()
            self.assertEqual(stats["total_buckets"], cap)

    def test_hash_distribution(self):
        """Тест распределения хеш-функции."""
        ht = HashTable(initial_capacity=16)
        test_keys = [
            "Иванов",
            "Петров",
            "Сидоров",
            "Кузнецов",
            "Андреев",
            "Борисов",
            "Григорьев",
            "Дмитриев",
            "Егоров",
            "Жуков",
            "Зайцев",
            "Игнатов",
            "Кириллов",
            "Лебедев",
            "Морозов",
            "Николаев",
        ]

        used_buckets = set()
        for key in test_keys:
            idx = ht._hash_function(key)
            used_buckets.add(idx)
            ht.put(key, f"value_{key}")

        # Хотя бы несколько корзин должны быть использованы
        self.assertGreater(
            len(used_buckets),
            1,
            "Хеш-функция должна распределять ключи по разным корзинам",
        )


class TestEdgeCases(unittest.TestCase):
    """Тесты граничных случаев."""

    def test_single_bucket_table(self):
        """Тест таблицы с одной корзиной."""
        ht = HashTable(initial_capacity=1)

        ht.put("a", 1)
        ht.put("b", 2)
        ht.put("c", 3)

        self.assertEqual(ht.get_size(), 3)
        self.assertEqual(ht.get("a"), 1)
        self.assertEqual(ht.get("b"), 2)
        self.assertEqual(ht.get("c"), 3)

        # Все ключи в одной корзине — проверяем коллизии
        stats = ht.get_collision_stats()
        self.assertEqual(stats["total_collisions"], 2)

    def test_empty_key_handling(self):
        """Тест обработки пустого ключа."""
        ht = HashTable(initial_capacity=4)
        ht.put("", "empty")
        self.assertEqual(ht.get(""), "empty")

    def test_very_long_key(self):
        """Тест очень длинного ключа."""
        ht = HashTable()
        long_key = "а" * 1000
        ht.put(long_key, "long")
        self.assertEqual(ht.get(long_key), "long")

    def test_special_characters(self):
        """Тест ключей со специальными символами."""
        ht = HashTable()
        ht.put("тест!", "value1")
        ht.put("тест?", "value2")
        self.assertEqual(ht.get("тест!"), "value1")
        self.assertEqual(ht.get("тест?"), "value2")

    def test_numeric_values(self):
        """Тест с числовыми значениями."""
        ht = HashTable()
        ht.put("счет", 1000)
        ht.put("баланс", -500.50)
        self.assertEqual(ht.get("счет"), 1000)
        self.assertEqual(ht.get("баланс"), -500.50)

    def test_none_values(self):
        """Тест с None значениями."""
        ht = HashTable()
        ht.put("нуль", None)
        self.assertIsNone(ht.get("нуль"))

    def test_bool_values(self):
        """Тест с булевыми значениями."""
        ht = HashTable()
        ht.put("активен", True)
        ht.put("заблокирован", False)
        self.assertTrue(ht.get("активен"))
        self.assertFalse(ht.get("заблокирован"))

    def test_list_values(self):
        """Тест со значениями-списками."""
        ht = HashTable()
        ht.put("список", [1, 2, 3])
        self.assertEqual(ht.get("список"), [1, 2, 3])


def run_tests():
    """Запуск всех тестов."""
    # Создаём тестовый набор
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestAVLNode))
    suite.addTests(loader.loadTestsFromTestCase(TestAVLTree))
    suite.addTests(loader.loadTestsFromTestCase(TestHashTable))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    # Запускаем с подробным выводом
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


if __name__ == "__main__":
    run_tests()
