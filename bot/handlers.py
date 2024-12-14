import os
import re
from telebot import TeleBot, types
from bot.states import user_states, user_data
from bot.config import STUDENTS_FILES_DIR, TASKS_FILES_DIR
from bot.teachers_usernames import AUTHORIZED_TEACHERS_USERNAMES
from bot.validators import is_valid_fio, is_valid_group, is_valid_date, is_valid_task
from bot.file_manager import read_existing_tasks, append_new_tasks
from telebot import types
from telebot.types import InputFile

# Использование переменной окружения для загрузки токена
TELEGRAM_BOT_TOKEN = os.getenv("hw_on_differential_equations_bot_token")
if TELEGRAM_BOT_TOKEN is None:
    raise RuntimeError("Переменная окружения hw_on_differential_equations_bot_token не установлена!")

bot = TeleBot(TELEGRAM_BOT_TOKEN)


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    username = message.from_user.username

    if username in AUTHORIZED_TEACHERS_USERNAMES:
        full_name = AUTHORIZED_TEACHERS_USERNAMES[username]
        user_states[user_id] = None
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
        markup.add("Добавить задачи для учеников", "Посмотреть статистику", "Загрузить данные")
        bot.send_message(user_id, f"Добро пожаловать,{full_name}!\nВыберите действие:", reply_markup=markup)
    else:
        user_states[user_id] = 'enter_fio'
        user_data[user_id] = {}
        bot.send_message(user_id, "Добро пожаловать, ученик!\nВведите ваши ФИ в формате <i>Иванов Иван</i>:", parse_mode='html')


# Обработка к возвращению выбора команд для преподавателя
@bot.message_handler(func=lambda message: message.text == "Вернуться к выбору команд")
def back_to_commands(message):
    user_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    markup.add("Добавить задачи для учеников", "Посмотреть статистику", "Загрузить данные", "Завершить работу")
    bot.send_message(user_id, "Выберите команду:", reply_markup=markup)


# Преподаватель устанавливает даты
@bot.message_handler(func=lambda message: message.text == "Добавить задачи для учеников")
def teacher_request_task_date(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Введите дату для задания задач в формате ДД.ММ.ГГГГ:")
    user_states[user_id] = 'teacher_task_date'


# Преподаватель подтверждает даты
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'teacher_task_date')
def teacher_create_task_file(message):
    user_id = message.chat.id
    date_str = message.text.strip()

    if is_valid_date(date_str):
        file_path = os.path.join(TASKS_FILES_DIR, f"tasks_{date_str}.txt")

        if not os.path.exists(file_path):
            open(file_path, "w", encoding="utf-8").close()
            bot.send_message(user_id, f"Файл для задач на дату {date_str} создан.")
        else:
            bot.send_message(user_id, f"Файл для задач на дату {date_str} уже существует.")

        user_data[user_id] = {'task_file': file_path}
        user_states[user_id] = 'teacher_tasks'
        bot.send_message(user_id, "Введите задачи, разделяя их запятыми:")
    else:
        bot.send_message(user_id, "Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ.")


# Преподаватель задаёт список актуальных задач
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'teacher_tasks')
def teacher_save_tasks(message):
    user_id = message.chat.id
    tasks = [task.strip() for task in message.text.split(",") if task.strip()]

    if not tasks:
        bot.send_message(user_id, "Вы не ввели ни одной задачи. Попробуйте снова.")
        return

    file_path = user_data[user_id]['task_file']
    with open(file_path, "a", encoding="utf-8") as file:
        file.write("\n".join(tasks) + "\n")  # Записываем задачи в файл

    bot.send_message(user_id, f"Задачи успешно добавлены: {', '.join(tasks)}.")

    # Завершение работы или возврат к выбору команд
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    markup.add("Вернуться к выбору команд", "Завершить работу")
    bot.send_message(user_id, "Выберите дальнейшее действие:", reply_markup=markup)
    user_states[user_id] = 'teacher_action'


# Преподаватель загружает данные
@bot.message_handler(func=lambda message: message.text == "Загрузить данные")
def download(message):
    user_id = message.chat.id
    files = os.listdir(STUDENTS_FILES_DIR)

    if not files:
        bot.send_message(user_id, "Нет доступных данных для загрузки.")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
        markup.add("Вернуться к выбору команд", "Завершить работу")
        bot.send_message(user_id, "Выберите дальнейшее действие:", reply_markup=markup)
        user_states[user_id] = None

    else:
        bot.send_message(user_id, "Отправка данных...")

        for filename in files:
            file_path = os.path.join(STUDENTS_FILES_DIR, filename)
            with open(file_path, "rb") as file:
                bot.send_document(user_id, file)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
        markup.add("Вернуться к выбору команд", "Завершить работу")
        bot.send_message(user_id, "Выберите команду:", reply_markup=markup)
        user_states[user_id] = None


# Преподаватель просматривает статистику
@bot.message_handler(func=lambda message: message.text == "Посмотреть статистику")
def view_statistics(message):
    user_id = message.chat.id

    try:
        # Пути к необходимым файлам
        base_dir = os.path.dirname(__file__)  # Корневая папка
        excel_folder_path = os.path.join(base_dir, "path_to_excel_folder")  # Указать путь к папке с Excel-файлом
        output_file = os.path.join(excel_folder_path, "new_wb.xlsx")

        # Генерация статистики (вызываем ваши функции)
        process_files_data(folder_path_tasks, excel_folder_path)  # Путь к задачам
        process_files_surname(folder_path_students, excel_folder_path)  # Путь к студентам

        # Отправка файла преподавателю
        if os.path.exists(output_file):
            bot.send_message(user_id, "Вот ваш файл со статистикой:")
            with open(output_file, "rb") as file:
                bot.send_document(user_id, InputFile(file, "new_wb.xlsx"))
        else:
            bot.send_message(user_id, "Файл со статистикой не найден. Возможно, возникла ошибка при его создании.")

    except Exception as e:
        # Обработка ошибок
        bot.send_message(user_id, f"Произошла ошибка при создании статистики: {e}")

    # Добавление кнопок для следующего действия
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    markup.add("Вернуться к выбору команд", "Завершить работу")
    bot.send_message(user_id, "Выберите дальнейшее действие:", reply_markup=markup)



# Ученик вводит ФИ
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'enter_fio')
def student_set_fio(message):
    user_id = message.chat.id
    fio = message.text.strip()
    if not is_valid_fio(fio):
        bot.send_message(user_id, "Неверный формат ввода данных.\nВведите в формате <i>Иванов Иван</i>:", parse_mode='html')

    user_data[user_id]['fio'] = fio
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Да", "Внести изменения")
    bot.send_message(user_id, f"Добавить данные для ученика <b>{fio}</b>?", parse_mode='html', reply_markup=markup)
    user_states[user_id] = 'confirm_fio'


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'confirm_fio')
def student_confirm_fio(message):
    user_id = message.chat.id
    if message.text == "Да":
        user_states[user_id] = 'enter_group'
        bot.send_message(user_id, "Введите вашу группу в формате <i>МЕН-123456</i>:", parse_mode='html')
    elif message.text == "Внести изменения":
        user_states[user_id] = 'enter_fio'
        bot.send_message(user_id, "Введите ваши фамилию и имя в формате <i>Иванов Иван</i>:", parse_mode='html')
    else:
        bot.send_message(user_id, "Ошибка. Выберите один из возможных ниже вариантов.")


# Ученик вводит группу
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'enter_group')
def student_set_group(message):
    user_id = message.chat.id
    group = message.text.strip()

    if not is_valid_group(group):
        bot.send_message(user_id, "Неверный формат ввода данных.\nВведите в формате <i>МЕН-123456</i>.", parse_mode='html')
        return

    user_data[user_id]['group'] = group
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Да", "Внести изменения")
    bot.send_message(user_id, f"Устанавливаю для вас группу <b>{group}</b>?", parse_mode='html', reply_markup=markup)
    user_states[user_id] = 'confirm_group'


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'confirm_group')
def student_confirm_group(message):
    user_id = message.chat.id
    if message.text == "Да":
        user_states[user_id] = 'enter_date'
        bot.send_message(user_id, "Введите дату в формате <i>ДД.ММ.ГГГГ</i> и не позже текущей:", parse_mode='html')
    elif message.text == "Внести изменения":
        user_states[user_id] = 'enter_group'
        bot.send_message(user_id, "Введите вашу группу в формате <i>МЕН-123456</i>:", parse_mode='html')
    else:
        bot.send_message(user_id, "Ошибка. Выберите один из возможных ниже вариантов.")


# Ученик вводит дату сдачи задач
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'enter_date')
def student_set_date(message):
    user_id = message.chat.id
    date_str = message.text.strip()

    if is_valid_date(date_str):
        latest_file = max(
            [os.path.join(TASKS_FILES_DIR, f) for f in os.listdir(TASKS_FILES_DIR) if f.startswith("tasks_")],
            key=os.path.getctime,
            default=None
        )

        if latest_file:
            with open(latest_file, "r", encoding="utf-8") as file:
                tasks = [task.strip() for task in file.readlines() if task.strip()]
            if tasks:
                tasks_message = "Актуальные задачи:\n" + "\n".join(tasks)
            else:
                tasks_message = "Актуальных задач пока нет."
        else:
            tasks_message = "Актуальных задач пока нет."

        bot.send_message(user_id, tasks_message)

        user_data[user_id]['date'] = date_str
        user_states[user_id] = 'enter_tasks'
        bot.send_message(user_id, "Введите номера сданных задач, разделяя их пробелами или запятыми:")
    else:
        bot.send_message(user_id, "Неверный формат ввода данных. Введите дату в формате <i>ДД.ММ.ГГГГ</i> и не позже текущей:", parse_mode='html')


# Ученик вводит задачи
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'enter_tasks')
def student_set_tasks(message):
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
    file_path = os.path.join(STUDENTS_FILES_DIR, f"{fio}.txt")

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

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    markup.add("Сдать ещё задачи", "Завершить работу")
    bot.send_message(user_id, "Выберите дальнейшее действие:", reply_markup=markup)
    user_states[user_id] = 'student_action'


# Ученик выбирает действие после сдачи задач
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'student_action')
def student_action(message):
    user_id = message.chat.id
    if message.text == "Сдать ещё задачи":
        user_states[user_id] = 'enter_date'
        bot.send_message(user_id, "Введите дату в формате <i>ДД.ММ.ГГГГ</i>.", parse_mode='html')
    elif message.text == "Завершить работу":
        user_states[user_id] = None
        finish_work(message)
    else:
        bot.send_message(user_id, "Пожалуйста, выберите один из вариантов.")


# Завершение работы
@bot.message_handler(func=lambda message: message.text == "Завершить работу")
def finish_work(message):
    user_id = message.chat.id
    user_states[user_id] = None
    bot.send_message(user_id, "Спасибо за работу! Вы можете вернуться в любой момент.")
    start(message)