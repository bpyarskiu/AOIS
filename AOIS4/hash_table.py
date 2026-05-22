# Класс, представляющий узел АВЛ-дерева для хранения пары ключ-значение
class AVLNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.height = 1  # Высота узла, лист имеет высоту 1
        self.left = None
        self.right = None


# Реализация АВЛ-дерева для использования в качестве корзины хеш-таблицы
class AVLTree:
    def __init__(self):
        self.root = None

    def _get_height(self, node):
        if not node:
            return 0
        return node.height

    def _get_balance(self, node):
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _update_height(self, node):
        if node:
            node.height = 1 + max(
                self._get_height(node.left), self._get_height(node.right)
            )

    def _rotate_right(self, y):
        x = y.left
        T2 = x.right

        x.right = y
        y.left = T2

        self._update_height(y)
        self._update_height(x)

        return x

    def _rotate_left(self, x):
        y = x.right
        T2 = y.left

        y.left = x
        x.right = T2

        self._update_height(x)
        self._update_height(y)

        return y

    def _balance(self, node):
        if not node:
            return node

        self._update_height(node)
        balance = self._get_balance(node)

        # Левое поддерево перевешивает
        if balance > 1:
            # Случай Left Right (большой правый)
            if self._get_balance(node.left) < 0:
                node.left = self._rotate_left(node.left)
            # Случай Left Left (малый правый)
            return self._rotate_right(node)

        # Правое поддерево перевешивает
        if balance < -1:
            # Случай Right Left (большой левый)
            if self._get_balance(node.right) > 0:
                node.right = self._rotate_right(node.right)
            # Случай Right Right (малый левый)
            return self._rotate_left(node)

        return node

    def _insert(self, node, key, value):
        if not node:
            return AVLNode(key, value)

        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            # Ключ уже существует, обновляем значение
            node.value = value
            return node

        return self._balance(node)

    def _get_min_value_node(self, node):
        current = node
        while current.left:
            current = current.left
        return current

    def _delete(self, node, key):
        if not node:
            return node

        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            if not node.left:
                return node.right
            elif not node.right:
                return node.left
            else:
                temp = self._get_min_value_node(node.right)
                node.key = temp.key
                node.value = temp.value
                node.right = self._delete(node.right, temp.key)

        if not node:
            return node

        return self._balance(node)

    def insert(self, key, value):
        self.root = self._insert(self.root, key, value)

    def delete(self, key):
        self.root = self._delete(self.root, key)

    def search(self, key):
        node = self.root
        while node:
            if key < node.key:
                node = node.left
            elif key > node.key:
                node = node.right
            else:
                return node.value
        return None

    def is_empty(self):
        return self.root is None

    def get_all_items(self):
        """Возвращает все пары (ключ, значение) из дерева."""
        items = []
        self._inorder_collect(self.root, items)
        return items

    def _inorder_collect(self, node, items):
        if node:
            self._inorder_collect(node.left, items)
            items.append((node.key, node.value))
            self._inorder_collect(node.right, items)

    def get_keys(self):
        """Возвращает все ключи из дерева."""
        return [item[0] for item in self.get_all_items()]

    def get_values(self):
        """Возвращает все значения из дерева."""
        return [item[1] for item in self.get_all_items()]


# Реализация хеш-таблицы с методом цепочек на АВЛ-деревьях
class HashTable:
    # Словарь для русских букв и их позиций в алфавите (1-33)
    RUSSIAN_ALPHABET_MAP = {
        "а": 1,
        "б": 2,
        "в": 3,
        "г": 4,
        "д": 5,
        "е": 6,
        "ё": 7,
        "ж": 8,
        "з": 9,
        "и": 10,
        "й": 11,
        "к": 12,
        "л": 13,
        "м": 14,
        "н": 15,
        "о": 16,
        "п": 17,
        "р": 18,
        "с": 19,
        "т": 20,
        "у": 21,
        "ф": 22,
        "х": 23,
        "ц": 24,
        "ч": 25,
        "ш": 26,
        "щ": 27,
        "ъ": 28,
        "ы": 29,
        "ь": 30,
        "э": 31,
        "ю": 32,
        "я": 33,
    }

    def __init__(self, initial_capacity=16):
        self.capacity = initial_capacity
        self.table = [AVLTree() for _ in range(self.capacity)]
        self.size = 0

    def _char_to_number(self, char):
        """Возвращает позицию буквы в алфавите (1-33) или 0, если символ не найден."""
        if not char or not isinstance(char, str):
            return 0
        return self.RUSSIAN_ALPHABET_MAP.get(char.lower(), 0)

    def _hash_function(self, key):
        """Вычисляет хеш на основе первых двух русских букв ключа."""
        if not isinstance(key, str) or len(key) == 0:
            return 0

        # Получаем коды первых двух символов
        num1 = self._char_to_number(key[0]) if len(key) >= 1 else 0
        num2 = self._char_to_number(key[1]) if len(key) >= 2 else 0

        # Вычисляем число в системе с основанием 33: num1 * 33 + num2
        combined_number = num1 * 33 + num2

        # Прибавляем константу 5 и берём остаток от деления
        return (combined_number + 5) % self.capacity

    def put(self, key, value):
        """Вставка или обновление значения по ключу."""
        if not isinstance(key, str):
            raise TypeError("Ключ должен быть строкой")

        index = self._hash_function(key)
        tree = self.table[index]
        old_value = tree.search(key)
        if old_value is None:
            self.size += 1
        tree.insert(key, value)

    def get(self, key):
        """Получение значения по ключу."""
        if not isinstance(key, str):
            raise TypeError("Ключ должен быть строкой")

        index = self._hash_function(key)
        tree = self.table[index]
        return tree.search(key)

    def remove(self, key):
        """Удаление пары ключ-значение."""
        if not isinstance(key, str):
            raise TypeError("Ключ должен быть строкой")

        index = self._hash_function(key)
        tree = self.table[index]
        if tree.search(key) is not None:
            tree.delete(key)
            self.size -= 1
            return True
        return False

    def contains(self, key):
        """Проверка наличия ключа в таблице."""
        return self.get(key) is not None

    def get_size(self):
        """Возвращает количество элементов в таблице."""
        return self.size

    def is_empty(self):
        """Проверяет, пуста ли таблица."""
        return self.size == 0

    def get_all_items(self):
        """Возвращает все пары (ключ, значение) из таблицы."""
        all_items = []
        for tree in self.table:
            all_items.extend(tree.get_all_items())
        return all_items

    def get_all_keys(self):
        """Возвращает все ключи из таблицы."""
        return [item[0] for item in self.get_all_items()]

    def get_all_values(self):
        """Возвращает все значения из таблицы."""
        return [item[1] for item in self.get_all_items()]

    def clear(self):
        """Очищает хеш-таблицу."""
        self.table = [AVLTree() for _ in range(self.capacity)]
        self.size = 0

    def get_bucket_sizes(self):
        """Возвращает список размеров каждой корзины."""
        return [len(tree.get_all_items()) for tree in self.table]

    def get_collision_stats(self):
        """Возвращает статистику по коллизиям."""
        bucket_sizes = self.get_bucket_sizes()
        non_empty = [s for s in bucket_sizes if s > 0]
        collisions = sum(max(0, s - 1) for s in bucket_sizes)

        return {
            "total_buckets": self.capacity,
            "non_empty_buckets": len(non_empty),
            "empty_buckets": self.capacity - len(non_empty),
            "max_bucket_size": max(bucket_sizes) if bucket_sizes else 0,
            "total_collisions": collisions,
            "load_factor": self.size / self.capacity if self.capacity > 0 else 0,
        }

    def __len__(self):
        return self.size

    def __str__(self):
        return "{" + ", ".join(f"{k}: {v}" for k, v in self.get_all_items()) + "}"

    def __contains__(self, key):
        return self.contains(key)

    def __getitem__(self, key):
        result = self.get(key)
        if result is None:
            raise KeyError(f"Ключ '{key}' не найден")
        return result

    def __setitem__(self, key, value):
        self.put(key, value)

    def __delitem__(self, key):
        if not self.remove(key):
            raise KeyError(f"Ключ '{key}' не найден")
