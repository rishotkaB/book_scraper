"""
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time

import time


def get_total_pages(base_url: str = "http://books.toscrape.com/catalogue/") -> int:
    page = 1
    start_time = time.time()
    print("Начинаю поиск количества страниц...")

    while True:
        url = f"{base_url}page-{page}.html"
        print(f"Страница {page}: ", end="")

        response = requests.get(url)
        if response.status_code != 200:
            print(f"не существует")
            break

        print(f"существует")
        page += 1

    total_pages = page - 1
    end_time = time.time()
    print(f"Поиск завершен за {end_time - start_time:.2f} секунд")
    print(f"Всего страниц: {total_pages}")
    return total_pages


def scrape_books(result):
    all_books = []  # Список для хранения всех книг

    for N in range(1, result + 1):
        link = f"http://books.toscrape.com/catalogue/page-{N}.html"
        soup = BeautifulSoup(requests.get(link).content, "html.parser")
        books = soup.find_all('article', class_='product_pod')
        print(f"На странице {N} найдено {len(books)} книг")

        for book in books:
            # Находим ссылку внутри карточки книги
            link_tag = book.find('h3').find('a')
            if link_tag and link_tag.get('href'):
                book_url = "http://books.toscrape.com/catalogue/" + link_tag['href'].replace('../../../', '')
                all_books.append(book_url)  # Добавляем книгу в список

    print(f"Итого книг: {len(all_books)}")  # Выводим общее количество
    return all_books  # Возвращаем список всех книг

with ThreadPoolExecutor(max_workers=20) as executor:
    result = executor.submit(get_total_pages)
    books_list = executor.submit(scrape_books,result)


import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json
from scraper import get_book_data


def get_total_pages(base_url: str = "http://books.toscrape.com/catalogue/") -> int:
    page = 1
    start_time = time.time()
    print("Начинаю поиск количества страниц...")

    while True:
        url = f"{base_url}page-{page}.html"
        print(f"Страница {page}: ", end="")

        response = requests.get(url)
        if response.status_code != 200:
            print(f"не существует")
            break

        print(f"существует")
        page += 1

    total_pages = page - 1
    end_time = time.time()
    print(f"Поиск завершен за {end_time - start_time:.2f} секунд")
    print(f"Всего страниц: {total_pages}")
    return total_pages


def scrape_books_parallel(total_pages):
    def scrape_page(page_num):
        link = f"http://books.toscrape.com/catalogue/page-{page_num}.html"
        soup = BeautifulSoup(requests.get(link).content, "html.parser")
        books = soup.find_all('article', class_='product_pod')

        book_urls = []
        for book in books:
            link_tag = book.find('h3').find('a')
            if link_tag and link_tag.get('href'):
                book_url = "http://books.toscrape.com/catalogue/" + link_tag['href'].replace('../../../', '')
                book_urls.append(book_url)

        print(f"Страница {page_num}: {len(book_urls)} книг")
        return book_urls

    all_books = []

    print("Начинаю парсинг книг...")
    scraping_start_time = time.time()

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Создаем задачи для всех страниц
        future_to_page = {executor.submit(scrape_page, page): page for page in range(1, total_pages + 1)}

        # Собираем результаты по мере готовности
        for future in as_completed(future_to_page):
            page_books = future.result()
            all_books.extend(page_books)

    scraping_end_time = time.time()
    print(f"Парсинг завершен за {scraping_end_time - scraping_start_time:.2f} секунд")
    print(f"Итого книг: {len(all_books)}")
    return all_books


def get_all_books_data(book_urls, max_workers=5):
    #Получает данные для всех книг используя многопоточность
    print(f"\nНачинаю сбор данных для {len(book_urls)} книг...")
    start_time = time.time()

    all_books_data = []
    processed_count = 0

    def process_book(book_url):
        try:
            book_data = get_book_data(book_url)
            return book_data, None
        except Exception as e:
            return None, f"Ошибка при обработке {book_url}: {str(e)}"

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Создаем задачи для всех книг
        future_to_url = {executor.submit(process_book, url): url for url in book_urls}

        # Собираем результаты по мере готовности
        for future in as_completed(future_to_url):
            book_data, error = future.result()

            if book_data:
                all_books_data.append(book_data)
                processed_count += 1
                print(f"Обработано книг: {processed_count}/{len(book_urls)}")
            else:
                print(f"Пропущена книга: {error}")

    end_time = time.time()
    print(f"Сбор данных завершен за {end_time - start_time:.2f} секунд")
    print(f"Успешно обработано: {len(all_books_data)} книг")

    return all_books_data


def save_to_json(data, filename="books_data.json"):
    #Сохраняет данные в JSON файл
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Данные сохранены в файл: {filename}")


if __name__ == "__main__":
    total_start_time = time.time()

    # Получаем общее количество страниц
    total_pages = get_total_pages()

    # Собираем все ссылки на книги
    book_urls = scrape_books_parallel(total_pages)

    # Получаем данные для всех книг
    books_data = get_all_books_data(book_urls, max_workers=10)

    # Сохраняем в JSON
    save_to_json(books_data, "all_books_data.json")

    total_end_time = time.time()
    print(f"\nОбщее время выполнения программы: {total_end_time - total_start_time:.2f} секунд")
    print(f"Итоговый результат: {len(books_data)} книг с полными данными")

"""
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json
from scraper import get_book_data


def scrape_books(is_save=False):
    # Встроенная функция для получения количества страниц
    def get_total_pages(base_url: str = "http://books.toscrape.com/catalogue/") -> int:
        page = 1
        start_time = time.time()
        print("Начинаю поиск количества страниц...")

        while True:
            url = f"{base_url}page-{page}.html"
            print(f"Страница {page}: ", end="")

            response = requests.get(url)
            if response.status_code != 200:
                print(f"не существует")
                break

            print(f"существует")
            page += 1

        total_pages = page - 1
        end_time = time.time()
        print(f"Поиск завершен за {end_time - start_time:.2f} секунд")
        print(f"Всего страниц: {total_pages}")
        return total_pages

    # Получаем общее количество страниц
    total_pages = get_total_pages()

    all_books_data = []

    def scrape_page(page_num):
        """Парсит одну страницу и возвращает данные книг"""
        link = f"http://books.toscrape.com/catalogue/page-{page_num}.html"
        soup = BeautifulSoup(requests.get(link).content, "html.parser")
        books = soup.find_all('article', class_='product_pod')

        page_books_data = []
        for book in books:
            link_tag = book.find('h3').find('a')
            if link_tag and link_tag.get('href'):
                book_url = "http://books.toscrape.com/catalogue/" + link_tag['href'].replace('../../../', '')
                try:
                    book_data = get_book_data(book_url)
                    page_books_data.append(book_data)
                except Exception as e:
                    print(f"Ошибка при обработке книги {book_url}: {e}")

        print(f"Страница {page_num}: обработано {len(page_books_data)} книг")
        return page_books_data

    print("Начинаю парсинг книг...")
    scraping_start_time = time.time()

    # Парсим все страницы параллельно
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Создаем задачи для всех страниц
        future_to_page = {executor.submit(scrape_page, page): page for page in range(1, total_pages + 1)}

        # Собираем результаты по мере готовности
        for future in as_completed(future_to_page):
            page_books_data = future.result()
            all_books_data.extend(page_books_data)

    scraping_end_time = time.time()
    print(f"Парсинг завершен за {scraping_end_time - scraping_start_time:.2f} секунд")
    print(f"Итого книг: {len(all_books_data)}")

    # Сохранение в файл если is_save=True
    if is_save:
        filename = "books_data.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            for book in all_books_data:
                f.write(str(book) + '\n')
        print(f"Данные сохранены в файл: {filename}")

    return all_books_data


# Проверка работы функции
if __name__ == "__main__":
    start_time = time.time()

    res = scrape_books(is_save=True)
    print(type(res), len(res))

    end_time = time.time()
    print(f"Общее время выполнения: {end_time - start_time:.2f} секунд")


