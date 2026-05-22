#!/usr/bin/env python3
"""
Консольное приложение для демонстрации работы хеш-таблицы
с разрешением коллизий методом цепочек на АВЛ-деревьях.
"""

from hash_table import HashTable
import sys
import traceback


def print_menu():
    """Вывод главного меню."""
    print("\n" + "=" * 60)
    print("ХЕШ-ТАБЛИЦА С РАЗРЕШЕНИЕМ КОЛЛИЗИЙ (АВЛ-ДЕРЕВЬЯ)")
    print("=" * 60)
    print("1. Добавить элемент")
    print("2. Получить элемент по ключу")
    print("3. Обновить элемент")
    print("4. Удалить элемент")
    print("5. Проверить наличие ключа")
    print("6. Вывести все элементы")
    print("7. Показать статистику")
    print("8. Показать размеры корзин")
    print("9. Очистить таблицу")
    print("10. Демонстрация коллизий")
    print("11. Создать новую таблицу")
    print("0. Выход")
    print("-" * 60)


def add_element(ht: HashTable):
    """Добавление нового элемента."""
    print("\n--- Добавление элемента ---")
    key = input("Введите ключ (русскими буквами): ").strip()
    if not key:
        print("Ключ не может быть пустым!")
        return
    value = input("Введите значение: ").strip()

    try:
        is_new = key not in ht
        ht.put(key, value)
        if is_new:
            print(f"✓ Добавлен новый элемент: {key} -> {value}")
        else:
            print(f"✓ Обновлён существующий элемент: {key} -> {value}")
    except Exception as e:
        print(f"✗ Ошибка: {e}")


def get_element(ht: HashTable):
    """Получение элемента по ключу."""
    print("\n--- Получение элемента ---")
    key = input("Введите ключ: ").strip()

    try:
        value = ht.get(key)
        if value is not None:
            print(f"✓ Значение: {value}")
        else:
            print(f"✗ Ключ '{key}' не найден")
    except Exception as e:
        print(f"✗ Ошибка: {e}")


def update_element(ht: HashTable):
    """Обновление значения по ключу."""
    print("\n--- Обновление элемента ---")
    key = input("Введите ключ: ").strip()

    if key not in ht:
        print(f"✗ Ключ '{key}' не найден. Используйте операцию добавления.")
        return

    old_value = ht.get(key)
    new_value = input(
        f"Текущее значение: {old_value}\nВведите новое значение: "
    ).strip()

    try:
        ht.put(key, new_value)
        print(f"✓ Значение обновлено: {key} -> {new_value}")
    except Exception as e:
        print(f"✗ Ошибка: {e}")


def remove_element(ht: HashTable):
    """Удаление элемента."""
    print("\n--- Удаление элемента ---")
    key = input("Введите ключ: ").strip()

    try:
        if ht.remove(key):
            print(f"✓ Элемент '{key}' удалён")
        else:
            print(f"✗ Ключ '{key}' не найден")
    except Exception as e:
        print(f"✗ Ошибка: {e}")


def check_key(ht: HashTable):
    """Проверка наличия ключа."""
    print("\n--- Проверка наличия ключа ---")
    key = input("Введите ключ: ").strip()

    if key in ht:
        print(f"✓ Ключ '{key}' присутствует. Значение: {ht.get(key)}")
    else:
        print(f"✗ Ключ '{key}' отсутствует")


def print_all_elements(ht: HashTable):
    """Вывод всех элементов таблицы."""
    print("\n--- Все элементы хеш-таблицы ---")
    items = ht.get_all_items()
    if not items:
        print("Таблица пуста")
        return

    # Сортируем по ключам для удобства чтения
    items.sort(key=lambda x: x[0])

    print(f"Всего элементов: {len(items)}")
    print("-" * 40)

    # Группируем по корзинам
    bucket_map = {}
    for key, value in items:
        index = ht._hash_function(key)
        if index not in bucket_map:
            bucket_map[index] = []
        bucket_map[index].append((key, value))

    for bucket_idx in sorted(bucket_map.keys()):
        bucket_items = bucket_map[bucket_idx]
        print(f"\nКорзина {bucket_idx} ({len(bucket_items)} элементов):")
        for key, value in bucket_items:
            print(f"  • {key} -> {value}")


def show_statistics(ht: HashTable):
    """Показать статистику хеш-таблицы."""
    print("\n--- Статистика хеш-таблицы ---")
    stats = ht.get_collision_stats()

    print(f"Размер таблицы (корзин): {stats['total_buckets']}")
    print(f"Количество элементов: {ht.get_size()}")
    print(f"Заполненных корзин: {stats['non_empty_buckets']}")
    print(f"Пустых корзин: {stats['empty_buckets']}")
    print(f"Максимальный размер корзины: {stats['max_bucket_size']}")
    print(f"Общее количество коллизий: {stats['total_collisions']}")
    print(f"Коэффициент загрузки: {stats['load_factor']:.3f}")


def show_bucket_sizes(ht: HashTable):
    """Показать размеры всех корзин."""
    print("\n--- Размеры корзин ---")
    sizes = ht.get_bucket_sizes()

    for i, size in enumerate(sizes):
        bar = "█" * min(size, 20)  # Максимум 20 символов для графика
        if size > 0:
            print(f"Корзина {i:3d}: {size:2d} {bar}")

    print(f"\nВсего корзин: {len(sizes)}")
    print(f"Пустых корзин: {sum(1 for s in sizes if s == 0)}")


def demo_collisions(ht: HashTable):
    """Демонстрация работы с коллизиями."""
    print("\n--- Демонстрация коллизий ---")
    print("Добавляем элементы, которые попадут в одну корзину...")

    # Создаём временную таблицу маленького размера для наглядности
    demo_ht = HashTable(initial_capacity=4)
    test_data = [
        ("арбуз", "ягода"),
        ("арфа", "инструмент"),
        ("артист", "профессия"),
        ("армия", "организация"),
        ("арка", "архитектура"),
        ("арена", "место"),
    ]

    print(f"\nРазмер таблицы: {demo_ht.capacity} корзины\n")

    for key, value in test_data:
        index = demo_ht._hash_function(key)
        demo_ht.put(key, value)
        print(f"Добавлен '{key}' -> хеш: {index}, корзина {index}")

    print(f"\nИтоговая статистика после {len(test_data)} вставок:")
    stats = demo_ht.get_collision_stats()
    print(f"  Элементов всего: {demo_ht.get_size()}")
    print(f"  Заполненных корзин: {stats['non_empty_buckets']}")
    print(f"  Коллизий: {stats['total_collisions']}")
    print(f"  Максимальный размер корзины: {stats['max_bucket_size']}")

    print("\nСодержимое таблицы:")
    for i in range(demo_ht.capacity):
        items = demo_ht.table[i].get_all_items()
        if items:
            print(f"  Корзина {i}: {items}")

    print("\nВсе операции (поиск, удаление) работают за O(log n) благодаря АВЛ-дереву!")


def create_new_table() -> HashTable:
    """Создание новой таблицы с указанной ёмкостью."""
    print("\n--- Создание новой таблицы ---")
    try:
        capacity = int(input("Введите размер таблицы (по умолчанию 16): ") or "16")
        if capacity < 1:
            print("Размер должен быть положительным. Использую 16.")
            capacity = 16
        new_ht = HashTable(initial_capacity=capacity)
        print(f"✓ Создана новая таблица размером {capacity}")
        return new_ht
    except ValueError:
        print("Некорректный ввод. Использую размер 16.")
        return HashTable(initial_capacity=16)


def main():
    """Главная функция консольного приложения."""
    print("=" * 60)
    print("ХЕШ-ТАБЛИЦА С РАЗРЕШЕНИЕМ КОЛЛИЗИЙ ЧЕРЕЗ АВЛ-ДЕРЕВЬЯ")
    print("Реализация на основе статей с neerc.ifmo.ru")
    print("=" * 60)

    ht = HashTable(initial_capacity=8)
    print(f"\nСоздана таблица с {ht.capacity} корзинами.\n")

    # Предзаполним таблицу примерами
    sample_data = [
        ("Петров", "инженер"),
        ("Иванов", "врач"),
        ("Сидоров", "учитель"),
        ("Кузнецов", "программист"),
        ("Андреева", "дизайнер"),
    ]

    print("Добавлены демонстрационные элементы:")
    for key, value in sample_data:
        ht.put(key, value)
        bucket = ht._hash_function(key)
        print(f"  {key} -> {value} (корзина {bucket})")

    while True:
        print_menu()
        choice = input("Выберите действие (0-11): ").strip()

        try:
            if choice == "1":
                add_element(ht)
            elif choice == "2":
                get_element(ht)
            elif choice == "3":
                update_element(ht)
            elif choice == "4":
                remove_element(ht)
            elif choice == "5":
                check_key(ht)
            elif choice == "6":
                print_all_elements(ht)
            elif choice == "7":
                show_statistics(ht)
            elif choice == "8":
                show_bucket_sizes(ht)
            elif choice == "9":
                ht.clear()
                print("✓ Таблица очищена")
            elif choice == "10":
                demo_collisions(ht)
            elif choice == "11":
                ht = create_new_table()
            elif choice == "0":
                print("\nДо свидания!")
                sys.exit(0)
            else:
                print("Неверный выбор. Попробуйте снова.")
        except KeyboardInterrupt:
            print("\n\nВыход из программы...")
            sys.exit(0)
        except Exception as e:
            print(f"✗ Неожиданная ошибка: {e}")
            traceback.print_exc()

        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    main()
