import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def get_book_data(book_url: str) -> dict:
    soup = BeautifulSoup(requests.get(book_url).content, 'html.parser')

    # Основная информация
    name = soup.find('h1').text.strip()

    # Рейтинг
    star_rating_element = soup.find('p', class_=lambda x: x and 'star-rating' in x)
    rating = None
    if star_rating_element:
        classes = star_rating_element.get('class', [])
        rating = next((cls for cls in classes if cls != 'star-rating'), None)

    # Таблица с деталями
    table = soup.find('table', attrs={'class': 'table table-striped'})
    product_data = {}

    for tr in table.find_all('tr'):
        tds = tr.find_all('td')
        th = tr.find('th')
        if th and tds:
            key = th.text.strip().lower().replace(' ', '_').replace('(', '').replace(')', '')
            value = tds[0].text.strip()
            product_data[key] = value

    # Описание
    product_description_elem = soup.find('div', id='product_description')
    product_description = ""
    if product_description_elem:
        product_description = product_description_elem.find_next_sibling('p').text.strip()

    # Объединяем все в один плоский словарь
    return {
        'name': name,
        'rating': rating,
        'description': product_description,
        **product_data  # распаковываем словарь с деталями
    }
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
        import os
        # Создаем директорию artifacts если её нет
        os.makedirs("artifacts", exist_ok=True)
        filename = "artifacts/books_data.txt"
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


