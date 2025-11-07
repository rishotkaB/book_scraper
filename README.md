# Books Scraper

Проект для парсинга данных о книгах с сайта [Books to Scrape](http://books.toscrape.com/).

## Описание
Скрипт собирает информацию о всех книгах на сайте: название, рейтинг, описание, цены, налоги, доступность, UPC код, количество отзывов и другую мета-информацию.

## Установка
1. Клонируйте репозиторий:
```bash
git clone https://github.com/rishotkaB/book_scraper
cd books-scraper
```
2. Установите зависимости:
```bash
pip install -r requirements.txt
```
## Использование
1. Основной скрипт
```bash
from main import scrape_books

# Запуск парсинга без сохранения
books = scrape_books(is_save=False)

# Запуск парсинга с сохранением в файл
books = scrape_books(is_save=True)
```
2. Планировщик (для автоматического запуска каждый день в 19:00):
```bash
python main.py
```
3. Тестирование
```bash
pytest tests/ -v
```
## Особенности
Многопоточный парсинг страниц

Автоматическое определение количества страниц

Обработка ошибок и пропуск битых ссылок

Логирование прогресса выполнения

## Требования
Python 3.8+

requests

beautifulsoup4

schedule (для планировщика)

pytest (для тестирования)

time