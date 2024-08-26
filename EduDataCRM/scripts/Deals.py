import pandas as pd
import numpy as np
import gspread
from gspread_dataframe import get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials
#from google.colab import drive
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report

# Загружаем файлы XLSX
file_paths = [
    'Deals.xlsx'
]

# Словарь для хранения датафреймов
dfs = {}

# Чтение каждого файла в датафрейм pandas и добавление в словарь
for file_path in file_paths:
    # Извлекаем название файла из пути
    file_name = file_path.split('/')[-1].split('.')[0]
    # Читаем файл и сохраняем в словарь
    dfs[file_name] = pd.read_excel(file_path, dtype={'Id': 'Int64', 'Contact Name': 'Int64'})

# Преобразование столбцов в формат datetime в датафрейме 'Contacts'
dfs['Deals']['Closing Date'] = pd.to_datetime(dfs['Deals']['Closing Date'], format='%d.%m.%Y')
dfs['Deals']['Created Time'] = pd.to_datetime(dfs['Deals']['Created Time'], format='%d.%m.%Y %H:%M')

#удаляем две последние строки в датафрейме Deals 
dfs['Deals'] = dfs['Deals'].iloc[:-2]

#Распределение данных в каждом столбце в таблице Deals
# Преобразование столбцов к строковому типу
dfs['Deals']['Offer Total Amount'] = dfs['Deals']['Offer Total Amount'].astype(str)
dfs['Deals']['Initial Amount Paid'] = dfs['Deals']['Initial Amount Paid'].astype(str)

# Замена символов и преобразование к типу float
dfs['Deals']['Offer Total Amount'] = dfs['Deals']['Offer Total Amount'].str.replace('€', '').str.replace('.', '').str.replace(',', '.').astype(float)
dfs['Deals']['Initial Amount Paid'] = dfs['Deals']['Initial Amount Paid'].str.replace('€', '').str.replace('.', '').str.replace(',', '.').astype(float)

#удаляем пустые строки в столбце, потому что они 0.13%
dfs['Deals'] = dfs['Deals'].dropna(subset=['Deal Owner Name'])

dfs['Deals']["City"] = dfs['Deals']['City'].replace({'Karl-Liebknecht str. 24, Hildburghausen, Thüringen': 'Hildburghausen', 'Poland , Gdansk , Al. Grunwaldzka 7, ap. 1a': 'Gdansk', 'Vor Ebersbach 1, 77761 Schiltach': 'Schiltach', '-': 'nan' })

deals_df = pd.DataFrame(dfs['Deals'].copy())

deals_df.rename(columns={'Contact Name': 'CONTACTID'}, inplace=True)

#удаляем пустые строки в столбце CONTACTID, потому что они 0.28%
deals_df = deals_df.dropna(subset=['CONTACTID'])
deals_df.rename(columns={'Content': 'Ad', 'Term': 'AdGroup'}, inplace=True)
deals_df = pd.DataFrame(deals_df.copy())

# Сохранение датафрейма в файл .pkl для удобной загрузки в Jupyter Notebook
deals_df.to_pickle('deals_df.pkl')
