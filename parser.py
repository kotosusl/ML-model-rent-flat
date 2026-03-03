import requests
import pandas as pd
from pycparser.c_ast import Union
from tqdm import tqdm
import time
import random
import logging
import typing as tp

logging.basicConfig(
    filename='parsing.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "https://arenda.mirkvartir.ru",
    "Referer": "https://arenda.mirkvartir.ru/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9",
}

API_URL = "https://www.mirkvartir.ru/listingapi/ListingPageModel/"


def make_request(page:int) -> tp.Dict[str, tp.Union[int, str]]:
    """
    функция возвращает набор параметров для запроса к API
    :param page: номер страницы, которую парсим
    :return: набор параметров для поиска подходящих объявлений
    """
    return {
        "locationIds": "MK_Region|78",
        "site": 16,  # 16 - аренда, 1 - продажа
        "p": page,
        "pricePeriod": 4  # 2 - краткосрочная аренда, 4 - долгосрочная
    }


def parse_response(offer: dict) -> tp.Dict[str, tp.Union[str, int, float]]:
    """
    парсим необходимые параметры из массива
    :param offer: словарь данных из ответа API
    :return: словарь необходимых данных
    """
    loc = offer.get('locationInfo', {}) or {}
    coords = loc.get('coordinate', {}) or {}
    subway = loc.get('subwayInfo', {}) or {}

    return {
        "id": offer.get("id"),
        "url": offer.get("url"),
        "title": offer.get("title"),
        "price": offer.get("price"),
        "latitude": coords.get("lat"),
        "longitude": coords.get("lon"),
        "metro_name": subway.get("subwayName"),
        "metro_distance": subway.get("minutesToMove"),
        "distanceType": subway.get("distanceType"),
        "update_time": offer.get("updateTime"),
        "page_number": offer.get("_page")
    }


def check_API(session: tp.Union[requests.Session]) -> int:
    """
    функция проверяет доступность API и получает общее количество объявлений
    :param session: сессия для HTTP запроса
    :return: общее количество объявлений
    """
    try:
        initial_response = session.post(API_URL, json=make_request(1))
        initial_data = initial_response.json()
        total_offers = initial_data.get("listingModel", {}).get("count", 0)
        return total_offers
    except Exception as e:
        logging.critical(f"[!] Ошибка при проверке общего количества объявлений: {e}")
        exit()


def collect_offers(max_pages:int=100, min_delay:int=2, max_delay:int=5)\
        -> tp.List[tp.Dict[str, tp.Union[str, int, float]]]:
    """
    функция проверяет доступность API, отправляяет POST запрос для каждого номера страницы,
    получает результат и парсит его
    :param max_pages: количество страниц, которые планируем спарсить
    :param min_delay: минимальная граница промежутка времени задержки
    :param max_delay: максимальная граница промежутка времени задержки
    :return: список словарей с информацией об искомых объявлениях
    """
    all_data = []
    session = requests.Session()
    session.headers.update(HEADERS)

    # Проверка доступности API, получаем общее количество объявлений
    total_offers = check_API(session)
    logging.info(f"Всего найдено объявлений: {total_offers}")

    # Создаем перемешанный список страниц
    pages = list(range(1, max_pages + 1))
    random.shuffle(pages)
    used_pages = set()

    with tqdm(total=max_pages, desc="Сбор данных") as pbar:
        for page in pages:
            if page in used_pages:
                continue

            payload = make_request(page)
            try:
                response = session.post(API_URL, json=payload, timeout=15)
                response.raise_for_status()

                data = response.json()
                listing_model = data.get("listingModel", {})
                offers = listing_model.get("offers", [])

                if not offers:
                    logging.warning(f"[!] Страница {page} пустая, пропускаем")
                    used_pages.add(page)
                    pbar.update(1)
                    continue

                for offer in offers:
                    offer["_page"] = page

                # Обрабатываем объявления
                page_data = []
                for offer in offers:
                    parsed = parse_response(offer)
                    if parsed:
                        page_data.append(parsed)

                all_data.extend(page_data)
                used_pages.add(page)
                pbar.update(1)

                # Логирование
                logging.info(f"[+] Страница {page}: собрано {len(page_data)} объявлений")

                # Случайная задержка
                delay = random.uniform(min_delay, max_delay)
                time.sleep(delay)

                # Дополнительная задержка каждые 5 страниц
                if len(used_pages) % 5 == 0:
                    extra_delay = random.uniform(5, 15)
                    print(f"\n[Пауза] Дополнительная задержка {extra_delay:.1f} сек")
                    time.sleep(extra_delay)

            except requests.exceptions.RequestException as e:
                logging.error(f"[!] Ошибка сети на странице {page}: {e}")
                time.sleep(10)
            except Exception as e:
                logging.error(f"[!] Ошибка на странице {page}: {e}")
                time.sleep(5)

            if len(used_pages) >= max_pages:
                break
    return all_data


if __name__ == "__main__":
    MAX_PAGES = 1
    MIN_DELAY = 2
    MAX_DELAY = 5
    logging.info("-" * 80)
    logging.info("Начало сбора данных со случайным порядком страниц...")
    offers_data = collect_offers(max_pages=MAX_PAGES, min_delay=MIN_DELAY, max_delay=MAX_DELAY)

    # Преобразуем массив данных в csv формат и сохраним в файле
    if offers_data:
        df = pd.DataFrame(offers_data)

        if 'page_number' in df.columns:
            df.drop('page_number', axis=1, inplace=True)

        filename = "data_for_ml.csv"
        df.to_csv(filename, index=False)
        logging.info(f"Собрано и сохранено {len(df)} объявлений в {filename}")

        unique_pages = len(set([o.get('_page', 0) for o in offers_data]))
        logging.info(f"Обработано уникальных страниц: {unique_pages}")
    else:
        logging.error("Не удалось собрать данные. Проверьте соединение и параметры запроса.")