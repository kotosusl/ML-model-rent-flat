import csv
import os


def test_csv_file():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(test_dir, '..', 'csv_files', 'main_data10000.csv')

    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

        assert len(rows) > 0, "Файл пустой"
        assert len(rows[0]) > 0, "Нет заголовков"
