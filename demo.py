import requests
from bs4 import BeautifulSoup
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


book_url = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'
print(get_book_data(book_url))
