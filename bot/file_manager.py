import os
from bot.config import TELEGRAM_BOT_TOKEN, TEACHER_PASSWORD, FILES_DIR

def ensure_files_dir_exists(files_dir):
    if not os.path.exists(files_dir):
        os.makedirs(files_dir)

def read_existing_tasks(file_path):
    existing_tasks = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                if " :" in line:
                    _, tasks = line.split(" : ", 1)
                    existing_tasks.extend(task.strip() for task in tasks.split(","))
    return existing_tasks

def append_new_tasks(file_path, fio, group, date, new_tasks):
    with open(file_path, "a", encoding="utf-8") as file:
        if os.path.getsize(file_path) == 0:
            file.write(f"{fio}, {group}\n\n")
        file.write(f"{date} : {', '.join(new_tasks)}\n")
