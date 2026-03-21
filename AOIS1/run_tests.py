# run_tests.py
#!/usr/bin/env python
"""Скрипт для запуска тестов с покрытием"""

import pytest
import sys

if __name__ == "__main__":
    # Запускаем тесты с покрытием
    result = pytest.main(
        [
            "tests/",
            "-v",
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html:coverage_report",
            "--cov-report=xml:coverage.xml",
            "--tb=short",
        ]
    )

    # Выводим информацию о покрытии
    print("\n" + "=" * 80)
    print("ОТЧЕТ О ПОКРЫТИИ КОДА")
    print("=" * 80)
    print("HTML отчет: coverage_report/index.html")
    print("XML отчет: coverage.xml")
    print("=" * 80)

    sys.exit(result)
