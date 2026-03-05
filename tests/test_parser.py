import csv


def test_csv_file():
    filename = "data_for_ml.csv"

    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

        assert len(rows) > 0, "Файл пустой"
        assert len(rows[0]) > 0, "Нет заголовков"