import pandas as pd
import numpy as np
import gspread
from gspread_dataframe import get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials
#from google.colab import drive
import matplotlib.pyplot as plt
import seaborn as sns

# Загружаем файлы XLSX
file_paths = [
    'Contacts.xlsx'
    
]

# Словарь для хранения датафреймов
dfs = {}

# Чтение каждого файла в датафрейм pandas и добавление в словарь
for file_path in file_paths:
    # Извлекаем название файла из пути
    file_name = file_path.split('/')[-1].split('.')[0]
    # Читаем файл и сохраняем в словарь
    dfs[file_name] = pd.read_excel(file_path)

# Преобразование столбцов в формат datetime в датафрейме 'Contacts'
dfs['Contacts']['Created Time'] = pd.to_datetime(dfs['Contacts']['Created Time'], format='%d.%m.%Y %H:%M')
dfs['Contacts']['Modified Time'] = pd.to_datetime(dfs['Contacts']['Modified Time'], format='%d.%m.%Y %H:%M')

#удаляем строку, где имя = False
dfs['Contacts'] = dfs['Contacts'][dfs['Contacts']['Contact Owner Name'] != False]

contacts_df = dfs['Contacts'].copy()
# Сохранение датафрейма в файл .pkl для удобной загрузки в Jupyter Notebook
contacts_df.to_pickle('contacts_df.pkl')