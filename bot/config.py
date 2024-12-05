import os

CONFIG_STUDENTS_PATH = os.path.join(os.path.dirname(__file__), "config_students_path.txt")


# Функция для загрузки FILES_DIR из config_path.txt
def load_files_dir():
    try:
        if not os.path.exists(CONFIG_STUDENTS_PATH):
            raise FileNotFoundError(f"Файл {CONFIG_STUDENTS_PATH} не найден! Убедитесь, что он существует.")

        with open(CONFIG_STUDENTS_PATH, "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith("FILES_DIR="):
                    files_dir = line.strip().split("=", 1)[1]

                    if not os.path.exists(files_dir):
                        os.makedirs(files_dir)
                        print(f"Папка {files_dir} была создана.")

                    return files_dir

            raise ValueError("Ключ STUDENTS_FILES_DIR не найден в файле config_students_path.txt. Проверьте содержимое файла.")
    except Exception as e:
        raise RuntimeError(f"Ошибка при загрузке STUDENTS_FILES_DIR из config_students_path.txt: {e}")


STUDENTS_FILES_DIR = load_files_dir()


CONFIG_TASKS_PATH = os.path.join(os.path.dirname(__file__), "config_tasks_path.txt")


# Функция для загрузки FILES_DIR из config_path.txt
def load_files_dir():
    try:
        if not os.path.exists(CONFIG_TASKS_PATH):
            raise FileNotFoundError(f"Файл {CONFIG_TASKS_PATH} не найден! Убедитесь, что он существует.")

        with open(CONFIG_TASKS_PATH, "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith("FILES_DIR="):
                    files_dir = line.strip().split("=", 1)[1]

                    if not os.path.exists(files_dir):
                        os.makedirs(files_dir)
                        print(f"Папка {files_dir} была создана.")

                    return files_dir

            raise ValueError("Ключ TASKS_FILES_DIR не найден в файле config_tasks_path.txt. Проверьте содержимое файла.")
    except Exception as e:
        raise RuntimeError(f"Ошибка при загрузке TASKS_FILES_DIR из config_tasks_path.txt: {e}")


TASKS_FILES_DIR = load_files_dir()