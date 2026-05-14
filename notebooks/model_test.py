from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import PolynomialFeatures
import typing as tp
import pandas as pd


def model_test(offers_filtered: pd.DataFrame) -> None:
    """
    Приведем переменные к единому масштабу и разделим на выборки.
    Создадим модель линейной регрессии и обучим ее. Выведем показатели коэффициента детерминации и среднеквадратической ошибки.
    Создадим модель полиномиальной регрессии и проделаем те же действия. Сразвним точности моделей.
    :param offers_filtered: dataframe с входными данными
    :return: None
    """
    X = offers_filtered[['area', 'centre_distance']]
    y = offers_filtered['price']

    # Разделение на обучающую (80%) и тестовую (20%) выборки
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=45)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    def linear_regres(X_train_scaled, X_test_scaled, y_train, y_test) -> tp.Tuple[float, float]:
        """
        модель линейной регрессии
        :param X_train_scaled: масштабированная обучающая выборка признаков
        :param X_test_scaled: масштабированная тестовая выборка признаков
        :param y_train: масштабированная обучающая выборка целевой переменной
        :param y_test: масштабированная тестовая выборка целевой переменной
        :return: кортеж из двух чисел - оценки модели
        """
        lin_reg = LinearRegression()
        lin_reg.fit(X_train_scaled, y_train)

        # Прогнозирование
        y_pred_lin = lin_reg.predict(X_test_scaled)

        # Оценка качества
        mse_lin = mean_squared_error(y_test, y_pred_lin)
        r2_lin = r2_score(y_test, y_pred_lin)

        print(f'Линейная модель -> MSE: {mse_lin:.2f}, R2: {r2_lin:.4f}')
        print('Коэффициенты модели:', dict(zip(X.columns, lin_reg.coef_)))
        return (r2_lin, mse_lin)

    r2_lin, mse_lin = linear_regres(X_train_scaled, X_test_scaled, y_train, y_test)

    def poly_regres(X_train_scaled, X_test_scaled, y_train, y_test) -> tp.Tuple[float, float]:
        """
        модель полиномиальной регрессии
        :param X_train_scaled: масштабированная обучающая выборка признаков
        :param X_test_scaled: масштабированная тестовая выборка признаков
        :param y_train: масштабированная обучающая выборка целевой переменной
        :param y_test: масштабированная тестовая выборка целевой переменной
        :return: кортеж из двух чисел - оценки модели
        """
        poly = PolynomialFeatures(degree=2, include_bias=False)
        X_train_poly = poly.fit_transform(X_train_scaled)
        X_test_poly = poly.transform(X_test_scaled)

        # Получаем имена новых признаков
        poly_features = poly.get_feature_names_out(X.columns)
        print("Примеры полиномиальных признаков:", poly_features[:10])

        poly_reg = LinearRegression()
        poly_reg.fit(X_train_poly, y_train)

        # Прогнозирование
        y_pred_poly = poly_reg.predict(X_test_poly)

        # Оценка качества
        mse_poly = mean_squared_error(y_test, y_pred_poly)
        r2_poly = r2_score(y_test, y_pred_poly)

        print(f'Полиномиальная модель -> MSE: {mse_poly:.2f}, R2: {r2_poly:.4f}')
        return (r2_poly, mse_poly)

    r2_poly, mse_poly = poly_regres(X_train_scaled, X_test_scaled, y_train, y_test)

    print("--- Сравнение моделей ---")
    print(f"Линейная модель:      R2 = {r2_lin:.4f}, MSE = {mse_lin:.2f}")
    print(f"{round(r2_lin * 100)}% предсказаний в пределах {round(mse_lin ** 0.5)} руб")
    print(f"Полиномиальная модель: R2 = {r2_poly:.4f}, MSE = {mse_poly:.2f}")
    print(f"{round(r2_poly * 100)}% предсказаний в пределах {round(mse_poly ** 0.5)} руб")
    return None