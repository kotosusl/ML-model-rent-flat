import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


def draw_distribution(offers_filtered: pd.DataFrame) -> None:
    """
    функция для рисования графиков нормального распределения и boxplot
    :param offers_filtered: dataframe с входными данными
    :return: None
    """
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    sns.histplot(offers_filtered['price'], bins=30, kde=True, color='skyblue')
    plt.title("Распределение цен")
    plt.xlabel("Цена, руб")

    plt.subplot(1, 2, 2)
    sns.boxplot(x=offers_filtered['price'], color='lightgreen')
    plt.title("Boxplot цен")
    plt.xlabel("Цена, руб")
    plt.tight_layout()
    plt.show()



def draw_different_graph(offers_filtered: pd.DataFrame) -> None:
    """
    функция для рисования графиков зависимостей цены от площади,
    :param offered_filtered: dataframe с входными данными
    :return: None
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    sns.regplot(x='area', y='price', data=offers_filtered,
                scatter_kws={'alpha':0.3}, line_kws={'color':'red'},
                ax=axes[0, 0])
    axes[0, 0].set_title("Зависимость цены от площади\nс линией регрессии", pad=10)

    room_price = offers_filtered.groupby('rooms')['price'].median().reset_index()
    sns.barplot(x='rooms', y='price', data=room_price, ax=axes[0, 1], palette='Blues_d')
    axes[0, 1].set_title("Медианная цена по количеству комнат", pad=10)
    axes[0, 1].set_ylabel("Медианная цена, руб")

    sns.scatterplot(x='centre_distance', y='price', data=offers_filtered,
                    alpha=0.3, ax=axes[1, 0])
    sns.kdeplot(x='centre_distance', y='price', data=offers_filtered,
                levels=5, color='red', ax=axes[1, 0])
    axes[1, 0].set_title("Цена vs Расстояние до центра\nс ядерной оценкой", pad=10)
    axes[1, 0].set_xlabel("Расстояние до центра, м")
    floor_price = offers_filtered.groupby('floor')['price_per_sqm'].mean().reset_index()
    sns.lineplot(x='floor', y='price_per_sqm', data=floor_price,
                 marker='o', ax=axes[1, 1], color='green')
    axes[1, 1].set_title("Средняя цена за кв.м по этажу", pad=10)
    axes[1, 1].set_ylabel("Средняя цена за кв.м, руб")
    plt.tight_layout()
    plt.show()


def draw_corr(offers_filtered: pd.DataFrame) -> None:
    """
    функция строит матрицу корреляций
    :param offers_filtered: dataframe с входными данными
    :return: None
    """
    numeric_cols = offers_filtered.select_dtypes(include=[np.number]).columns.tolist()

    numeric_cols = [col for col in numeric_cols if col not in ['id']]

    plt.figure(figsize=(12, 10))
    corr = offers_filtered[numeric_cols].corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap='coolwarm', center=0,
                annot_kws={"size": 10}, cbar_kws={"shrink": .8})
    plt.title("Матрица корреляций", pad=20)
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()



def draw_main_corr(offers_filtered: pd.DataFrame) -> None:
    """
    функция строит графики зависимости трех самых коррелирующих с ценой признаков
    :param offers_filtered: dataframe с входными данными
    :return: None
    """
    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(7, 14))
    features = ['rooms', 'area', 'centre_distance']
    for i, col in enumerate(features):
        sns.scatterplot(x=offers_filtered[col], y=offers_filtered['price'], ax=axes[i], alpha=0.6)
        axes[i].set_title(f'Зависимость цены от {col}')
    plt.tight_layout()
    plt.show()
