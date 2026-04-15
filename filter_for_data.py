import math

import pandas as pd


def filter_drop_metroname(offers_file: str, output_file: str) -> None:
    """
    функция чистит данные от ненужной информации и строк с пропусками
    :param stations_file: json файл с информацией о станциях метро
    :param offers_file: csv файл с объявлениями
    :param output_file: csv файл вывода данных
    :return: None
    """

    offers = pd.read_csv(offers_file)
    offers = offers.dropna(subset=['metro_name'])

    offers.to_csv(output_file, index=False)
    return None


def filter_parse_strings(offers_file: str, output_file: str):
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
        mx_fl = int(fl.split()[0].split('/')[1])
        fl = int(fl.split()[0].split('/')[0])
        rooms.append(room)
        area.append(ar)
        floor.append(fl)
        max_floor.append(mx_fl)

    offers.drop('title', axis=1, inplace=True)
    offers.drop('url', axis=1, inplace=True)
    offers['rooms'] = rooms
    offers['area'] = area
    offers['floor'] = floor
    offers['max_floor'] = max_floor
    offers.to_csv(output_file, index=False)
    return None


def filter_only_for_training(input_file, output_file):
    offers = pd.read_csv(input_file)
    print(offers.info())


if __name__ == "__main__":
    #filter_drop_metroname("main_data10000.csv", 'main_data_filter_metro.csv')
    #filter_parse_strings('main_data_filter_metro.csv', 'output_file.csv')
    pass
