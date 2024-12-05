import os


TU_FILE_PATH = os.path.join(os.path.dirname(__file__), "teachers_usernames_data.txt")

# Загружаем данные преподавателей из файла
def load_teachers_usernames(file_path):
    authorized_teachers = {}
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(",", 1)  # Разделяем только по первой запятой
                if len(parts) == 2:
                    username, full_name = parts
                    authorized_teachers[username] = full_name
    else:
        print(f"Файл {file_path} не найден! Убедитесь, что он существует.")
    return authorized_teachers


AUTHORIZED_TEACHERS_USERNAMES = load_teachers_usernames(TU_FILE_PATH)