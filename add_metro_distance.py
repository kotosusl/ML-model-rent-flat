import math

import pandas as pd


def add_metro_distance(stations_file: str, offers_file: str, output_file: str) -> None:
    """
    функция добавляет к каждому объявлению расстояние от
    квартиры до метро в координатах
    :param stations_file: json файл с информацией о станциях метро
    :param offers_file: csv файл с объявлениями
    :return: None
    """
    stations = pd.read_json(stations_file)
    offers = pd.read_csv(offers_file)
    metro_distance = []
    for i in range(len(offers)):
        offer = offers.iloc[i]
        if type(offer.metro_name) != float:
            flat_cords = (float(offer.latitude), float(offer.longitude))
            st = stations.loc[stations.Name == offer.metro_name]
            if len(st) == 0:
                metro_distance.append(-1)
                continue
            st = st.iloc[0]
            metro_cords = (float(st.Lat), float(st.Lon))

            metro_distance.append(math.dist(flat_cords, metro_cords))
        else:
            metro_distance.append(-1)

    offers["metro_distance_coords"] = metro_distance
    offers.to_csv(output_file, index=False)
    return None


if __name__ == "__main__":
    add_metro_distance("stations.json", "main_data_filter_metro.csv", 'main_data_filter_metro.csv')
