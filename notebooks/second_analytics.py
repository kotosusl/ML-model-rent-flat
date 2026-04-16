import pandas as pd
import numpy as np
from geopy.distance import geodesic
from model_test import model_test
from graphs import draw_distribution, draw_different_graph, draw_corr, draw_main_corr


def handle(input_file: str) -> pd.DataFrame:
    """
    ручка - выводит первые 5 строк указанного файла
    :param input_file: название файла
    :return: dataframe с записями файла
    """
    offers = pd.read_csv(input_file)
    print(len(offers))
    offers.head(5)
    return offers



def filter_parse_strings(offers_file: str, output_file: str):
    """
    парсим заголовок и разделяем данные на столбцы (rooms, area, floor, max_floor),
    сохраняем в новый файл
    :param offers_file: входной файл
    :param output_file: файл для вывода
    :return: None
    """
    offers = pd.read_csv(offers_file)
    rooms = []
    area = []
    floor = []
    max_floor = []
    for i in range(len(offers)):
        offer = offers.iloc[i]
        room, ar, fl = offer.title.split(', ')
        if room == 'Студия':
            room = 0
        else:
            room = int(room[0])

        ar = float(ar.split()[0])
        if '/' not in fl:
          mx_fl = np.nan
        else:
          mx_fl = int(fl.split()[0].split('/')[1])
        fl = int(fl.split()[0].split('/')[0])
        rooms.append(room)
        area.append(ar)
        floor.append(fl)
        max_floor.append(mx_fl)

    offers['rooms'] = rooms
    offers['area'] = area
    offers['floor'] = floor
    offers['max_floor'] = max_floor
    offers = offers.dropna(subset=['max_floor'])
    offers['max_floor'] = offers['max_floor'].astype(int)
    offers['price_per_sqm'] = offers['price'] / offers['area']
    offers.to_csv(output_file, index=False)

    return None



def add_centre_distance(offers_file: str, output_file: str) -> None:
    """
    функция добавляет к каждому объявлению расстояние от
    квартиры до метро в координатах
    :param stations_file: json файл с информацией о станциях метро
    :param offers_file: csv файл с объявлениями
    :return: None
    """
    offers = pd.read_csv(offers_file)
    centre_distance = []
    for i in range(len(offers)):
        offer = offers.iloc[i]
        flat_cords = (float(offer.latitude), float(offer.longitude))
        centre_coords = (59.93, 30.32)
        centre_distance.append(geodesic((offer.latitude, offer.longitude), centre_coords).meters)

    offers['centre_distance'] = centre_distance
    offers.to_csv(output_file, index=False)
    return None



def filter_only_for_training(input_file: str, output_file: str) -> None:
    """
    избавимся от ненужных столбцов и обезличим данные
    :param input_file: название входного файла
    :param output_file: название файла вывода
    :return: None
    """
    offers = pd.read_csv(input_file)

    offers.drop('title', axis=1, inplace=True)
    offers.drop('url', axis=1, inplace=True)
    offers.drop('metro_distance', axis=1, inplace=True)
    offers.drop('distanceType', axis=1, inplace=True)
    offers.drop('update_time', axis=1, inplace=True)
    offers.drop('metro_name', axis=1, inplace=True)

    offers.to_csv(output_file, index=False)
    return None



def delete_duplicate(offers: pd.DataFrame, output_file: str) -> None:
    """
    Сбор данных происходил со случайных страниц, поэтому не исключены дубликаты строк. Найдем и очистим их.
    :param offers: dataframe с входными данными из таблицы
    :param output_file: название файла для вывода
    :return: None
    """
    print(offers.duplicated().sum())
    offers = offers.drop_duplicates()
    print(offers.duplicated().sum())
    print(len(offers))
    offers.to_csv(output_file, index=False)



def display_statistics(offers: pd.DataFrame) -> None:
    """
    выводим в консоль статистику по данным
    :param offers: dataframe с входными параметрами
    :return: None
    """
    pd.set_option('display.float_format', lambda x: f'{x:.6f}')
    offers.describe(percentiles=[.01, .25, .5, .75, .99]).T



def del_anomalies(offers: pd.DataFrame) -> pd.DataFrame:
    """
    функция для удаления аномальных значений
    :param offers: dataframe с входными данными
    :return: dataframe без аномалий
    """
    price_lower = offers['price'].quantile(0.01)
    price_upper = offers['price'].quantile(0.99)
    centre_max = offers['centre_distance'].quantile(0.96)
    max_area = offers['area'].quantile(0.995)

    offers_filtered = offers[
        (offers['price'] >= price_lower) &
        (offers['price'] <= price_upper) &
        (offers['centre_distance'] <= centre_max) &
        (offers['area'] <= max_area)
    ].copy()
    return offers_filtered


if __name__ == '__main__':
    handle('../csv_files/main_data10000.csv')

    filter_parse_strings('../csv_files/main_data10000.csv', '../csv_files/data_filter2.csv')
    offers = handle('../csv_files/data_filter2.csv')

    add_centre_distance("../csv_files/data_filter2.csv", '../csv_files/data_filter4.csv')
    offers = handle('../csv_files/data_filter4.csv')
    offers.info()

    filter_only_for_training('../csv_files/data_filter4.csv', '../csv_files/data_filter5.csv')
    offers = handle('../csv_files/data_filter5.csv')

    delete_duplicate(offers, '../csv_files/data_filter6.csv')

    display_statistics(offers)
    offers_filtered = del_anomalies(offers)
    print(f"Удалено {len(offers) - len(offers_filtered)} строк (выбросы по цене, площади и расстоянию до центра)")
    offers_filtered.to_csv('../csv_files/final_data.csv', index=False)

    draw_distribution(offers_filtered)

    draw_different_graph(offers_filtered)
    draw_corr(offers_filtered)
    draw_main_corr(offers_filtered)

    model_test(offers_filtered)