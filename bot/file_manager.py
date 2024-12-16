import os
from bot.config import TASKS_FILES_DIR

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


def get_all_tasks_from_files():
    all_tasks = []
    for file_name in os.listdir(TASKS_FILES_DIR):
        if file_name.startswith("tasks_"):
            file_path = os.path.join(TASKS_FILES_DIR, file_name)
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    tasks = [task.strip() for task in file.readlines() if task.strip()]
                    all_tasks.extend(tasks)
            except Exception as e:
                print(f"Ошибка при чтении файла {file_name}: {e}")
    return all_tasks