import time
import telebot
from telebot import types
from datetime import datetime
import re

bot = telebot.TeleBot('8000790714:AAF8b-9847v_yyGcZMAp1ui9AtvUkiQH_0g')

TEACHER_PASSWORD = "securepassword"
authorized_teachers = set()  # Хранение ID авторизованных преподавателей
user_states = {}  # Состояние каждого пользователя
user_data = {}  # Постоянные данные учеников (ФИ и группа)

import os
FILES_DIR = r"C:\Users\Алина\Desktop\pyton\tg bot\students"

if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    user_states[user_id] = 'choose_role'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Преподаватель", "Ученик")
    bot.send_message(user_id, "Выберите вашу роль:", reply_markup=markup)


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'choose_role')
def choose_role(message):
    user_id = message.chat.id
    if message.text == "Преподаватель":
        user_states[user_id] = 'enter_password'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Вернуться к выбору роли")
        bot.send_message(user_id, "Вы выбрали роль «Преподаватель».\nВведите пароль:", parse_mode='html', reply_markup=markup)

    elif message.text == "Ученик":
        user_states[user_id] = 'enter_fio'
        user_data[user_id] = {}
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Вернуться к выбору роли")
        bot.send_message(user_id, "Вы выбрали роль «Ученик».\nВведите ваши фамилию и имя в формате <i>Иванов Иван</i>:", parse_mode='html', reply_markup=markup)

    elif message.text == "Вернуться к выбору роли":
        start(message)

    else:
        bot.send_message(user_id, "Ошибка. Выберите один из возможных ниже вариантов.")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'enter_password')
def check_teacher_password(message):
    user_id = message.chat.id
    if message.text == "Вернуться к выбору роли":
        start(message)
        return

    if message.text == TEACHER_PASSWORD:
        authorized_teachers.add(user_id)
        user_states[user_id] = None  # Сбрасываем состояние
        bot.send_message(user_id, "Авторизация успешна!")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
        markup.add("Загрузить данные", "Посмотреть статистику")
        bot.send_message(user_id, "Выберите команду:", reply_markup=markup)
    else:
        bot.send_message(user_id, "Неверный пароль.\nПопробуйте снова.")


@bot.message_handler(func=lambda message: message.text == "Загрузить данные" and message.chat.id in authorized_teachers)
def download(message):
    user_id = message.chat.id
    files = os.listdir(FILES_DIR)

    if not user_data:
        bot.send_message(user_id, "Нет доступных данных для загрузки.")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
        markup.add("Вернуться к выбору команд", "Завершить работу")
        bot.send_message(user_id, "Вы можете", reply_markup=markup)

        user_states[user_id] = None

    else:
        bot.send_message(user_id, "Отправка данных...")

        for filename in files:
            file_path = os.path.join(FILES_DIR, filename)
            with open(file_path, "rb") as file:
                bot.send_document(user_id, file)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
        markup.add("Вернуться к выбору команд", "Завершить работу")
        bot.send_message(user_id, "Выберите команду:", reply_markup=markup)

        user_states[user_id] = None


@bot.message_handler(func=lambda message: message.text == "Посмотреть статистику" and message.chat.id in authorized_teachers)
def view_statistics(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Статистики сданных задач ещё нет.")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    markup.add("Вернуться к выбору команд", "Завершить работу")
    bot.send_message(user_id, "Вы можете:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Вернуться к выбору команд" and message.chat.id in authorized_teachers)
def back_to_commands(message):
    user_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    markup.add("Загрузить данные", "Посмотреть статистику", "Завершить работу")
    bot.send_message(user_id, "Выберите команду:", reply_markup=markup)


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'enter_fio')
def get_fio(message):
    user_id = message.chat.id
    if message.text == "Вернуться к выбору роли":
        start(message)
        return

    user_data[user_id]['fio'] = message.text
    user_states[user_id] = 'enter_group'  # Состояние: ввод группы
    bot.send_message(user_id, "Введите вашу группу в формате <i>МЕН-123456</i>:", parse_mode='html', reply_markup=types.ReplyKeyboardRemove())


def is_valid_group(group):
    return bool(re.match(r'^МЕН-\d{6}$', group))


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'enter_group')
def get_group(message):
    user_id = message.chat.id
    group = message.text

    if not is_valid_group(group):
        bot.send_message(user_id, "Неверный формат группы.\nВведите в формате <i>МЕН-123456</i>", parse_mode='html')
        return

    user_data[user_id]['group'] = group
    user_states[user_id] = 'enter_date'  # Состояние: ввод даты
    bot.send_message(user_id, "Введите дату в формате  <i>ДД.ММ.ГГГГ</i> и не позже текущей:", parse_mode='html')


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'enter_date')
def get_date(message):
    user_id = message.chat.id
    try:
        entered_date = datetime.strptime(message.text, "%d.%m.%Y")
        if entered_date > datetime.now():
            bot.send_message(user_id, "Дата не может быть позже текущей. Попробуйте снова.")
            return
    except ValueError:
        bot.send_message(user_id, "Неверный формат даты.\nВведите в формате <i>ДД.ММ.ГГГГ</i>.", parse_mode='html')
        return

    user_data[user_id]['date'] = message.text
    user_states[user_id] = 'enter_tasks'  # Состояние: ввод задач
    bot.send_message(user_id, "Введите номера сданных задач:")


def is_valid_task(task):
    return bool(re.match(r'^\d+$', task))


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'enter_tasks')
def get_tasks(message):
    user_id = message.chat.id
    entered_tasks = re.split(r'[ ,]+', message.text.strip())
    entered_tasks = [task.strip() for task in entered_tasks if task.strip()]

    if not entered_tasks:
        bot.send_message(user_id, "Вы не ввели задачи. Пожалуйста, введите хотя бы одну задачу.")
        return

    invalid_tasks = [task for task in entered_tasks if not is_valid_task(task)]

    if invalid_tasks:
        bot.send_message(user_id, f"Некоторые из введённых задач некорректны: {', '.join(invalid_tasks)}.\nЗадачи должны содержать только цифры.")
        return

    fio = user_data[user_id]['fio']
    group = user_data[user_id]['group']
    date = user_data[user_id]['date']

    filename = os.path.join(FILES_DIR, f"{fio}.txt")

    existing_tasks = []
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                if " :" in line:
                    _, tasks = line.split(" : ", 1)
                    existing_tasks.extend(task.strip() for task in tasks.split(","))

    new_tasks = [task for task in entered_tasks if task not in existing_tasks]
    duplicate_tasks = [task for task in entered_tasks if task in existing_tasks]

    if duplicate_tasks:
        bot.send_message(user_id, f"Следующие задачи уже были сданы ранее: {', '.join(duplicate_tasks)}")

    if new_tasks:
        with open(filename, "a", encoding="utf-8") as file:
            if os.path.getsize(filename) == 0:
                file.write(f"{fio}, {group}\n\n")
            file.write(f"{date} : {', '.join(new_tasks)}\n")

        bot.send_message(user_id, f"Задачи добавлены: {', '.join(new_tasks)}")

    else:
        bot.send_message(user_id, "Все введённые задачи уже были сданы ранее.")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    markup.add("Сдать ещё задачи", "Завершить работу")
    bot.send_message(user_id, "Хотите сдать ещё задачи?", reply_markup=markup)
    user_states[user_id] = 'student_action'


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'student_action')
def student_action(message):
    user_id = message.chat.id
    if message.text == "Сдать ещё задачи":
        user_states[user_id] = 'enter_date'
        bot.send_message(user_id, "Введите дату в формате  <i>ДД.ММ.ГГГГ</i> и не позже текущей:", parse_mode='html')

    elif message.text == "Завершить работу":
        user_states[user_id] = None
        user_data[user_id] = {}
        finish_work(message)

    else:
        bot.send_message(user_id, "Ошибка. Выберите один из возможных ниже вариантов.")


@bot.message_handler(func=lambda message: message.text == "Завершить работу" and message.chat.id in authorized_teachers)
def finish_work(message):
    user_id = message.chat.id
    user_states[user_id] = None
    bot.send_message(user_id, "Спасибо за работу! Вы можете вернуться в любой момент.")
    start(message)


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка: {e}. Перезапуск через 5 секунд...")
        time.sleep(5)
