import os
import re
from telebot import TeleBot, types
from bot.states import user_states, user_data, authorized_teachers
from bot.config import TELEGRAM_BOT_TOKEN, TEACHER_PASSWORD, FILES_DIR
from bot.validators import is_valid_fio, is_valid_group, is_valid_date, is_valid_task
from bot.file_manager import read_existing_tasks, append_new_tasks

bot = TeleBot(TELEGRAM_BOT_TOKEN)


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    user_states[user_id] = 'choose_role'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Преподаватель", "Ученик")
    bot.send_message(user_id, "Выберите вашу роль:", reply_markup=markup)


# Выбор роли
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'choose_role')
def choose_role(message):
    user_id = message.chat.id
    if message.text == "Преподаватель":
        user_states[user_id] = 'enter_password'
        bot.send_message(user_id, "Введите пароль преподавателя:")
    elif message.text == "Ученик":
        user_states[user_id] = 'enter_fio'
        user_data[user_id] = {}
        bot.send_message(user_id, "Введите ваши ФИО в формате Иванов Иван:")
    else:
        bot.send_message(user_id, "Пожалуйста, выберите одну из ролей.")


# Проверка пароля преподавателя
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'enter_password')
def check_teacher_password(message):
    user_id = message.chat.id
    if message.text == TEACHER_PASSWORD:
        authorized_teachers.add(user_id)
        user_states[user_id] = None
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Загрузить данные", "Посмотреть статистику")
        bot.send_message(user_id, "Авторизация успешна! Выберите действие:", reply_markup=markup)
    else:
        bot.send_message(user_id, "Неверный пароль. Попробуйте снова.")


# Проверка ФИО ученика
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'enter_fio')
def get_fio(message):
    user_id = message.chat.id
    fio = message.text.strip()
    if is_valid_fio(fio):
        user_data[user_id]['fio'] = fio
        user_states[user_id] = 'enter_group'
        bot.send_message(user_id, "Введите вашу группу в формате МЕН-123456:")
    else:
        bot.send_message(user_id, "Неверный формат. Введите ФИО в формате Иванов Иван.")


# Проверка группы ученика
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'enter_group')
def get_group(message):
    user_id = message.chat.id
    group = message.text.strip()
    if is_valid_group(group):
        user_data[user_id]['group'] = group
        user_states[user_id] = 'enter_date'
        bot.send_message(user_id, "Введите дату в формате ДД.ММ.ГГГГ:")
    else:
        bot.send_message(user_id, "Неверный формат группы. Попробуйте снова.")


# Проверка даты
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'enter_date')
def get_date(message):
    user_id = message.chat.id
    date_str = message.text.strip()
    if is_valid_date(date_str):
        user_data[user_id]['date'] = date_str
        user_states[user_id] = 'enter_tasks'
        bot.send_message(user_id, "Введите номера сданных задач, разделяя их пробелами или запятыми:")
    else:
        bot.send_message(user_id, "Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ и не позже текущей.")


# Проверка и сохранение задач
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'enter_tasks')
def get_tasks(message):
    user_id = message.chat.id
    tasks = re.split(r'[ ,]+', message.text.strip())
    tasks = [task for task in tasks if task]

    invalid_tasks = [task for task in tasks if not is_valid_task(task)]
    if invalid_tasks:
        bot.send_message(user_id, f"Некорректные задачи: {', '.join(invalid_tasks)}. Введите только цифры.")
        return

    fio = user_data[user_id]['fio']
    group = user_data[user_id]['group']
    date = user_data[user_id]['date']
    file_path = os.path.join(FILES_DIR, f"{fio}.txt")

    existing_tasks = read_existing_tasks(file_path)
    new_tasks = [task for task in tasks if task not in existing_tasks]
    duplicate_tasks = [task for task in tasks if task in existing_tasks]

    if duplicate_tasks:
        bot.send_message(user_id, f"Эти задачи уже были сданы: {', '.join(duplicate_tasks)}.")

    if new_tasks:
        append_new_tasks(file_path, fio, group, date, new_tasks)
        bot.send_message(user_id, f"Добавлены новые задачи: {', '.join(new_tasks)}.")
    else:
        bot.send_message(user_id, "Все введённые задачи уже были сданы ранее.")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Сдать ещё задачи", "Завершить работу")
    bot.send_message(user_id, "Выберите дальнейшее действие:", reply_markup=markup)
    user_states[user_id] = 'student_action'


# Действия после сдачи задач
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'student_action')
def student_action(message):
    user_id = message.chat.id
    if message.text == "Сдать ещё задачи":
        user_states[user_id] = 'enter_date'
        bot.send_message(user_id, "Введите дату в формате ДД.ММ.ГГГГ:")
    elif message.text == "Завершить работу":
        user_states[user_id] = None
        bot.send_message(user_id, "Спасибо за использование бота!")
    else:
        bot.send_message(user_id, "Пожалуйста, выберите один из вариантов.")


# Загрузка данных (для преподавателей)
@bot.message_handler(func=lambda message: message.text == "Загрузить данные" and message.chat.id in authorized_teachers)
def download_data(message):
    user_id = message.chat.id
    files = os.listdir(FILES_DIR)
    if not files:
        bot.send_message(user_id, "Нет данных для загрузки.")
        return

    for filename in files:
        file_path = os.path.join(FILES_DIR, filename)
        with open(file_path, "rb") as file:
            bot.send_document(user_id, file)


# Просмотр статистики (для преподавателей)
@bot.message_handler(func=lambda message: message.text == "Посмотреть статистику" and message.chat.id in authorized_teachers)
def view_statistics(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Функция просмотра статистики пока не реализована.")
