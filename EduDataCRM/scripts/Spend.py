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
    'Spend.xlsx'
]

# Словарь для хранения датафреймов
dfs = {}

# Чтение каждого файла в датафрейм pandas и добавление в словарь
for file_path in file_paths:
    # Извлекаем название файла из пути
    file_name = file_path.split('/')[-1].split('.')[0]
    # Читаем файл и сохраняем в словарь
    dfs[file_name] = pd.read_excel(file_path, dtype={'Id': 'Int64'})

spend_df = pd.DataFrame(dfs['Spend'].copy())

# Сохранение датафрейма в файл .pkl для удобной загрузки в Jupyter Notebook
spend_df.to_pickle('spend_df.pkl')
