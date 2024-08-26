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
    'Calls.xlsx',
    
]

# Словарь для хранения датафреймов
dfs = {}

# Чтение каждого файла в датафрейм pandas и добавление в словарь
for file_path in file_paths:
    # Извлекаем название файла из пути
    file_name = file_path.split('/')[-1].split('.')[0]
    # Читаем файл и сохраняем в словарь
    dfs[file_name] = pd.read_excel(file_path, dtype={'CONTACTID': 'Int64'})

# Замена значений <NA> на 0
dfs['Calls']['CONTACTID'] = dfs['Calls']['CONTACTID'].fillna(0)

# Преобразование столбца в int64
dfs['Calls']['CONTACTID'] = dfs['Calls']['CONTACTID'].astype('int64')

# Преобразование столбцов в формат datetime в датафрейме 'Calls'
dfs['Calls']['Call Start Time'] = pd.to_datetime(dfs['Calls']['Call Start Time'], format='%d.%m.%Y %H:%M')

# Удаление дубликатов строк
dfs['Calls'].drop_duplicates(inplace=True)

# Удаление неактуальных столбцов  в датафрейме
columns_to_drop_calls = ['Tag', 'Dialled Number', 'Scheduled in CRM']
dfs['Calls'].drop(columns=columns_to_drop_calls, axis = 1 , inplace=True)

# Замена пропущенных значений в числовых столбцах на среднее значение
dfs['Calls']['Call Duration (in seconds)'] = dfs['Calls']['Call Duration (in seconds)'].fillna(dfs['Calls']['Call Duration (in seconds)'].mean())

columns_to_drop_calls = ['Outgoing Call Status']
dfs['Calls'].drop(columns=columns_to_drop_calls, axis = 1 , inplace=True)

calls_df = pd.DataFrame(dfs['Calls'].copy())

# Сохранение датафрейма в файл .pkl для удобной загрузки в Jupyter Notebook
calls_df.to_pickle('calls_df.pkl')

