from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext, InlineQueryHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram import InlineQueryResultPhoto
import sqlite3
from telegram import Update
import telebot
from telebot import types
from telegram import ReplyKeyboardMarkup

#import secret
#import config
import mysql.connector

# это можно перенести в файл config.py и потом импортировать, чтобы скрыть данные о пароле и пути к базе данных.
#функция connect_to_db() используется для подключения к базе данных MySQL. 
def connect_to_db():
    dbconfig = {'host': 'localhost',
                'user': 'root',
                'password': 'password',
                'database': 'movies'}
    try:
        connection = mysql.connector.connect(**dbconfig)
        cursor = connection.cursor()
        print("Подключение к базе данных успешно.")
        return connection, cursor
    except mysql.connector.Error as err:
        print(f"Ошибка при подключении к базе данных: {err}")
        return None, None
        
connection, cursor = connect_to_db()  # Используем возвращаемые значения

#функция для создания таблицы запросов
def create_queries_table(cursor):
    query = """CREATE TABLE IF NOT EXISTS movie_query
            (id INT AUTO_INCREMENT PRIMARY KEY,
            query VARCHAR(255) NOT NULL);"""
    cursor.execute(query)
create_queries_table(cursor)

# Функция сохранения запроса пользователя в MySQL
def log_user_query(cursor, query):
    # Сохранение запроса пользователя в MySQL
    try:
        
        insert_query = "INSERT INTO movie_query (query) VALUES (%s)"
        cursor.execute(insert_query, (query,))
        connection.commit()
        print("Запрос пользователя успешно сохранен.")
    except mysql.connector.Error as err:
        print(f"Ошибка при сохранении запроса пользователя: {err}")


# это можно перенести в файл secret.py и потом его экспортировать, чтобы скрыть информацию по токену
token = ('your_token_api') #первый бот
bot = telebot.TeleBot(token)

# хендлер и функция для обработки команды /start
#обработчик сообщений запускается, когда пользователь отправляет команду /start боту. 
#Когда бот получает эту команду, он отправляет пользователю приветственное сообщение с именем пользователя и вопросом, а также двумя кнопками "Да" и "Нет".

@bot.message_handler(commands=['start'])
def startBot(message):
    first_mess = f"{message.from_user.first_name}, привет!\nХочешь расскажу немного о себе и что я умею?"
    markup = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    button_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    markup.add(button_yes, button_no)
    bot.send_message(message.chat.id, first_mess, reply_markup=markup)

# код обрабатывает колбэки, которые возникают при нажатии пользователем на кнопки.
#пользователь нажимает на кнопку "Да", срабатывает условие if call.data == "yes". В этом случае бот отправляет сообщение и меняет callback_data для кнопки "Да" на "yes_second", чтобы обработать следующий этап в диалоге. Затем бот отправляет новое сообщение с обновленной клавиатурой, где есть только кнопка "Да" с новым callback_data и кнопка "Нет".
#Когда пользователь нажимает на кнопку "Да" во второй раз (уже с новым callback_data "yes_second"), срабатывает условие elif call.data == "yes_second". Теперь бот перенаправляет пользователя непосредственно к функции выбора критериев поиска фильмов, которая называется process_search_movies.
#Когда пользователь нажимает на кнопку "Нет", срабатывает условие elif call.data == "no", и бот отправляет сообщение.

@bot.callback_query_handler(func=lambda call: True)
def response(call):
    bot.answer_callback_query(call.id)  
    if call.data == "yes":
        second_mess = "Отлично! Я могу помочь тебе найти интересные фильмы. Продолжим?"
        markup = types.InlineKeyboardMarkup()
        # Изменение callback_data для кнопки "Да" на "yes_second"
        button_yes = types.InlineKeyboardButton(text='Да', callback_data='yes_second')
        button_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
        markup.add(button_yes, button_no)
        bot.send_message(call.message.chat.id, second_mess, reply_markup=markup)
    elif call.data == "yes_second":
        # Перенаправление непосредственно к функции выбора критериев поиска
        process_search_movies(call.message)
    elif call.data == "no":
        bot.send_message(call.message.chat.id, "Жаль! Если передумаешь, просто напиши мне. До свидания!")

#функция обрабатывает сообщение от пользователя с текстом "Поиск фильмов" и предоставляет пользователю меню с вариантами поиска фильмов.
#Создается клавиатура с вариантами поиска: "Поиск по жанру", "Поиск по слову", "Поиск по году", "Статистика запросов", "Выход".
#Отправляется сообщение пользователю с текстом "Выберите один из вариантов поиска фильмов:" и прикрепленной клавиатурой.
#Затем регистрируется обработчик следующего шага (bot.register_next_step_handler), который будет ждать ответа пользователя и вызывать функцию process_main_menu для обработки выбора пользователя из предоставленного меню.

@bot.message_handler(func=lambda message: message.text == "Поиск фильмов")
def process_search_movies(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Поиск по жанру", "Поиск по слову", "Поиск по году", "Статистика запросов", "Выход")
    text_message = "Выберите один из вариантов поиска фильмов:"
    bot.send_message(message.chat.id, text_message, reply_markup=markup)
    bot.register_next_step_handler(message, process_main_menu)

#Функция обрабатывает выбор пользователя из меню главного меню поиска фильмов. 
#Она принимает сообщение от пользователя, содержащее выбранный им вариант поиска фильмов, и осуществляет соответствующие действия.

def process_main_menu(message):
    choose = message.text
    if choose == "Поиск по жанру":
        # Сразу вызываем функцию input_genres для загрузки и вывода жанров
        input_genres(message)  # Убираем register_next_step_handler и вызываем напрямую
        #process_search_movies(message)
        
    elif choose == "Поиск по слову":
        bot.send_message(message.chat.id, "Введите слово из названия фильма:")
        bot.register_next_step_handler(message, process_keyword)
        #добавлена функция обратно в меню
        #process_search_movies(message)
        
    elif choose == "Поиск по году":
        bot.send_message(message.chat.id, "Введите год выпуска фильма c 2007 до 2015 года:")
        bot.register_next_step_handler(message, process_year_input)  # Изменено на process_year_input
                
    elif choose == "Статистика запросов":
        display_popular_queries(message) #вызываем функцию напрямую
        process_search_movies(message)
        
    elif choose == "Выход":
        bot.send_message(message.chat.id, "Спасибо за использование нашего сервиса. До свидания!")
        return

# функция извлекает список уникальных жанров фильмов из базы данных. 
#Выполняется SQL-запрос, который выбирает все жанры фильмов из таблицы movies и объединяет их в одну строку с помощью функции GROUP_CONCAT.
#Результат запроса сохраняется в переменную genres_str.
#Строка жанров разделяется на список жанров с помощью метода split(',').
#Далее осуществляется фильтрация повторяющихся жанров с помощью цикла for. Уникальные жанры добавляются в список unique_genres.
#В конце функция возвращает список уникальных жанров.
#Если возникает ошибка при выполнении SQL-запроса, она обрабатывается блоком except, который выводит сообщение об ошибке и возвращает пустой список

def get_genres(cursor):
    try:
        
        # Выбираем все жанры фильмов и объединяем их в одну строку
        query = "SELECT GROUP_CONCAT(genres) FROM movies"
        cursor.execute(query)
        genres_str = cursor.fetchone()[0]  # Получаем строку с жанрами
        
        # Разделяем строку на список жанров
        genres = genres_str.split(',') if genres_str else []
        unique_genres = []
        for genre in genres:
            if genre not in unique_genres:
                unique_genres.append(genre)
        
        return unique_genres
        
    except mysql.connector.Error as err:
        print(f"Ошибка при выполнении запроса: {err}")
        return []
        
#Эта функция извлекает информацию о фильмах определенного жанра из базы данных. 
#Результаты запроса сохраняются в переменной movies.
#Если запрос выполняется успешно, функция возвращает список фильмов.
#Если возникает ошибка во время выполнения запроса, она обрабатывается в блоке except. Сообщение об ошибке выводится, и функция возвращает пустой список.

def get_genre_movies(cursor, genre):
    try:
        # Запрос фильмов для выбранного жанра
        query = f"SELECT title, plot, year, poster FROM movies WHERE genres LIKE '%{genre}%' LIMIT 10"
        cursor.execute(query)
        movies = cursor.fetchall()
        return movies
        
    except mysql.connector.Error as err:
        print(f"Ошибка при выполнении запроса: {err}")
        return []
    except Exception as e:
        print(f"Ошибка: {e}")
        return []
    
#функция предназначена для ввода пользователем номера жанра из списка. 
#Функция input_genres получает список всех жанров из базы данных с помощью функции get_genres.
#Если список жанров не пустой, то формируется сообщение со списком жанров, которое отправляется пользователю.
#Создается клавиатура с кнопками, каждая из которых соответствует номеру жанра.
#Клавиатура отправляется пользователю, и ожидается ответ в виде номера жанра.
#Зарегистрирован обработчик следующего шага, который будет вызван после получения ответа пользователя.       

def input_genres(message):
    global genres, cursor
    genres = get_genres(cursor)  # Получаем список всех жанров из базы данных
    
    if genres:  # Проверяем, есть ли жанры
        # Формируем и отправляем сообщение с перечнем жанров
        genres_message = "\n".join(f"{idx + 1}. {genre}" for idx, genre in enumerate(genres))
        bot.send_message(message.chat.id, genres_message)
        
        # Создаем клавиатуру с номерами жанров
        genres_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for idx, genre in enumerate(genres, start=1):
            genres_keyboard.add(types.KeyboardButton(str(idx)))
        
        # Отправляем клавиатуру пользователю
        bot.send_message(message.chat.id, "Выберите номер жанра:", reply_markup=genres_keyboard)
        # Регистрируем обработчик следующего шага
        bot.register_next_step_handler(message, process_genre_choice)
        
    else:
        bot.send_message(message.chat.id, "Извините, не удалось получить список жанров.")
    


#process_genre_choice: Эта функция обрабатывает выбранный пользователем жанр. Она пытается преобразовать текст сообщения в число, чтобы определить выбранный пользователем номер жанра. Если это число, и оно попадает в диапазон от 1 до количества жанров, она извлекает соответствующий жанр из списка genres и отправляет пользователю список фильмов этого жанра. В случае ошибки значения или ввода, она отправляет соответствующее сообщение об ошибке.

def process_genre_choice(message):
    global genres, cursor  # Делаем переменные доступными внутри функции
    try:
        choice = int(message.text)
        if 1 <= choice <= len(genres):
            selected_genre = genres[choice - 1]
            genre_movies = get_genre_movies(cursor, selected_genre)

            bot.send_message(message.chat.id, f"Фильмы в жанре '{selected_genre}':")
            for idx, movie in enumerate(genre_movies, start=1):
                movie_info = f"{idx}. Название: {movie[0]}\n   Описание: {movie[1]}\n   Год выпуска: {movie[2]}\n    Постер: {movie[3]}"
                bot.send_photo(message.chat.id, photo=movie[3], caption=movie_info)
            genre_offsets[selected_genre] = 0  # Инициализируем смещение для жанра
            ask_for_more_movies(message, selected_genre)  # Запрос на дополнительные фильмы
            log_user_query(cursor, selected_genre) #запрос на сохранение в базе данных

        else:
            bot.send_message(message.chat.id, "Пожалуйста, введите корректный номер.")

    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите число.")

#код представляет функцию, которая используется для получения дополнительных фильмов определенного жанра с учетом смещения. 

def get_additional_movies(cursor, selected_genre, offset):
    try:
        
        query = f"SELECT title, plot, year, poster FROM movies WHERE genres LIKE '%{selected_genre}%' LIMIT 10 OFFSET {offset}"
        cursor.execute(query)
        additional_movies = cursor.fetchall()
        return additional_movies
    except mysql.connector.Error as err:
        print(f"Ошибка при выполнении запроса: {err}")
        return []
   
        
#функция предназначена для запроса у пользователя о том, нужно ли ему еще 10 фильмов выбранного жанра. 
def ask_for_more_movies(message, selected_genre):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #размер кнопок исправлен
    markup.add(types.KeyboardButton("Да"), types.KeyboardButton("Нет"))
    bot.send_message(message.chat.id, "Хотите еще 10 фильмов этого жанра? (да/нет)", reply_markup=markup)
    bot.register_next_step_handler(message, handle_user_response, selected_genre)


#функция обрабатывает ответ пользователя на предыдущий вопрос о том, нужно ли ему еще 10 фильмов выбранного жанра или нет...

def handle_user_response(message, selected_genre, keyword=None): #добавлен третий аргумент - смотрим, что будет...
    user_response = message.text.lower()
    if user_response == "да":
        # Получаем текущее смещение из словаря и запрашиваем следующие 10 фильмов
        offset = genre_offsets.get(selected_genre, 0) + 10
        genre_offsets[selected_genre] = offset  # Обновляем смещение в словаре
        additional_movies = get_additional_movies(cursor, selected_genre, offset)
        if additional_movies:
            for idx, movie in enumerate(additional_movies, start=1):
                movie_info = f"{idx + offset}. Название: {movie[0]}\n   Описание: {movie[1]}\n   Год выпуска: {movie[2]}\n    Постер: {movie[3]}"
                bot.send_photo(message.chat.id, photo=movie[3], caption=movie_info)
            ask_for_more_movies(message, selected_genre)  # Предложить еще фильмы
        else:
            bot.send_message(message.chat.id, "Больше фильмов этого жанра не найдено.")
    elif user_response == "нет":
        bot.send_message(message.chat.id, "Хорошо, если вам понадобится еще фильмы - обращайтесь.")
        
    else:
        bot.send_message(message.chat.id, "Пожалуйста, ответьте 'да' или 'нет'.")
        ask_for_more_movies(message, selected_genre)  # Повторный запрос
        
         
genre_offsets = {}  # Словарь для хранения смещения для каждого жанра


#функция выполняет поиск фильмов по ключевому слову в базе данных.

def search_films_by_keyword(cursor, message, keyword):
    try:
    # Изменяем SQL-запрос для нечувствительности к регистру
        
        query = f"SELECT title, year, plot, poster FROM movies WHERE LOWER(title) LIKE '%{keyword}%' LIMIT 10"
        cursor.execute(query)
        films = cursor.fetchall()
        if not films:
            return "По вашему запросу ничего не найдено."
        else:
            result = f"Найдено фильмов: {len(films)}\n"
            for idx, movie in enumerate(films, start=1):
                movie_info = f"{idx}. Название: {movie[0]}\n   Описание: {movie[2]}\n   Год выпуска: {movie[1]}\n    Постер: {movie[3]}"
                bot.send_photo(message.chat.id, photo=movie[3], caption=movie_info)      
            return result
    except mysql.connector.Error as err:
        print(f"Ошибка при выполнении запроса: {err}")
        return "Произошла ошибка при выполнении запроса."
    
    except Exception as e:
        print(f"Ошибка: {e}")
        return "Произошла непредвиденная ошибка."

#функция обрабатывает ключевое слово, введенное пользователем для поиска фильмов по нему

def process_keyword(message):
    # Получаем текст напрямую из сообщения пользователя и переводим в нижний регистр для универсальности
    keyword = message.text.lower()
    log_user_query(cursor, keyword)  # Записываем запрос пользователя
    films_info = search_films_by_keyword(cursor, message, keyword)
    bot.send_message(message.chat.id, films_info)
    process_search_movies(message)


#функция выполняет поиск фильмов по указанному году выпуска

def search_films_by_year(cursor, year, message):
    try:
        
        cursor.execute("SELECT title, year, plot, poster FROM movies WHERE year = %s LIMIT 10", (year,))
        films = cursor.fetchall()
        if not films:
            bot.send_message(message.chat.id, "По вашему запросу ничего не найдено.")
        else:
            bot.send_message(message.chat.id, "Вот список фильмов по вашему запросу:")
            for idx, movie in enumerate(films, start=1):
                movie_info = f"{idx}. Название: {movie[0]}\n   Описание: {movie[2]}\n   Год выпуска: {movie[1]}\n    Постер: {movie[3]}"
                bot.send_photo(message.chat.id, photo=movie[3], caption=movie_info)
            return films
            
    except mysql.connector.Error as err:
        print(f"Ошибка при выполнении запроса: {err}")
        return []
    except Exception as e:
        print(f"Ошибка: {e}")
        return []
    
# функция обрабатывает ответ пользователя на вопрос о желании выполнить поиск фильмов по году выпуска или просмотреть популярные запросы.

@bot.message_handler(func=lambda message: message.text.lower() in ["да", "нет", "популярные запросы"])
def process_year_search_response(message):
    response = message.text.lower()  # Получаем ответ пользователя

    if response == 'да':
        bot.send_message(message.chat.id, "Введите год выпуска фильма c 2007 до 2015 года:")
        bot.register_next_step_handler(message, process_year_input)

    elif response == 'нет':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Да"), types.KeyboardButton("Нет"))
        bot.send_message(message.chat.id, "Хорошо, если вам понадобится еще фильмы - обращайтесь.")

# Функция для обработки ввода пользователем года выпуска фильма
def process_year_input(message):
    try:
        year = int(message.text)
        if 2007 <= year <= 2015:
            bot.send_message(message.chat.id, f"Год {year} принят. Спасибо за выбор.")
            log_user_query(cursor, year)
            movies = search_films_by_year(cursor, year, message)
            #добавлен возврат в меню, после выдачи фильмов.
            process_search_movies(message)
            
            if movies:
                movies_list = "\n".join([f"{movie[0]} - {movie[1]}" for movie in movies])
                #bot.send_message(message.chat.id, f"Фильмы {year} года:\n{movies_list}")
            else:
                bot.send_message(message.chat.id, "К сожалению, фильмов в данном году нет в базе данных.")
        else:
            bot.send_message(message.chat.id, "Год выпуска фильма должен быть в диапазоне от 2007 до 2015.")
            bot.register_next_step_handler(message, process_year_input)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный год числом.")
        bot.register_next_step_handler(message, process_year_input)

# Функция для запроса к базе данных на получение статистики самых популярных запросов
def get_popular_queries(cursor):
    try:
        
        query = """
            SELECT query, COUNT(*) AS count
            FROM movie_query
            GROUP BY query
            ORDER BY count DESC LIMIT 10;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        return results
            
    except mysql.connector.Error as err:
        print(f"Ошибка при выполнении анализа запросов: {err}")
        return []

#функция отображает самые популярные запросы пользователей.
#Сначала она получает список популярных запросов. Затем она формирует текст сообщения и отправляет ответ пользователю.
#код создаст текст в виде таблицы, который будет отправлен пользователю

def display_popular_queries(message):
    popular_queries = get_popular_queries(cursor)
    
    # Заголовок таблицы
    message_text = "{:<30} | {:<10}\n".format("Частые запросы", "Количество")
    message_text += "-" * 53 + "\n"  # Разделительная линия
    
    # Заполнение таблицы данными
    for query, count in popular_queries:
        message_text += "{:<30} | {:<10}\n".format(query, count)
    
    bot.send_message(message.chat.id, message_text)
    
    response = message.text.lower()  

#используется для запуска бота в режиме "прослушивания" входящих обновлений. 
#none_stop=True гарантирует, что бот будет перезапущен автоматически в случае возникновения какой-либо ошибки, чтобы он продолжал работать без прерываний.
#interval=0 указывает, что бот будет постоянно проверять наличие новых обновлений без каких-либо задержек между запросами к серверам Telegram.
#код обычно размещается в конце скрипта бота и запускает его, начиная прослушивание входящих обновлений от пользователей.

bot.polling(none_stop=True, interval = 0)