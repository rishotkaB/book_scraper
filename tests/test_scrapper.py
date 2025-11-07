# tests/test_scraper.py
import sys
import os
import pytest

# Добавляем путь к корневой директории для импорта модулей
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scraper import *


class TestGetBookData:
    """Тесты для функции get_book_data"""

    def test_returns_dict_with_required_keys(self):
        """Проверяет, что функция возвращает словарь с нужными ключами"""
        book_url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
        result = get_book_data(book_url)

        # Проверяем тип возвращаемых данных
        assert isinstance(result, dict), "Функция должна возвращать словарь"

        # Проверяем обязательные ключи
        required_keys = ['name', 'rating', 'description']
        for key in required_keys:
            assert key in result, f"Отсутствует обязательный ключ: {key}"

    def test_name_field_correct(self):
        """Проверяет корректность поля названия книги"""
        book_url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
        result = get_book_data(book_url)

        assert 'name' in result, "Ключ 'name' должен присутствовать"
        assert result['name'] == 'A Light in the Attic', "Название книги не соответствует ожидаемому"
        assert isinstance(result['name'], str), "Название должно быть строкой"


class TestScrapeBooks:
    """Тесты для функции scrape_books"""

    def test_returns_list_of_books(self):
        """Проверяет, что функция возвращает список книг"""
        result = scrape_books(is_save=False)
        assert isinstance(result, list), "Функция должна возвращать список"
        assert len(result) > 0, "Список книг не должен быть пустым"

    def test_books_count_correct(self):
        """Проверяет, что количество собранных книг соответствует ожиданиям"""
        result = scrape_books(is_save=False)
        # На сайте 50 страниц по 20 книг = 1000 книг
        assert len(result) == 1000, f"Ожидалось 1000 книг, получено {len(result)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])