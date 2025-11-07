import schedule
from scrape_books import *
# Настройка планировщика задач
# Запускает функцию парсинга каждый день в 19:00 с сохранением данных в файл
schedule.every().day.at("19:00").do(lambda: scrape_books(is_save=True))
print("Планировщик запущен. Ожидание выполнения задач...")
# Основной цикл планировщика
# Проверяет наличие задач для выполнения каждые 60 секунд для оптимизации нагрузки
while True:
    schedule.run_pending()
    time.sleep(60)