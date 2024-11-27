import os

# Использование переменной окружения для загрузки токена
TELEGRAM_BOT_TOKEN = os.getenv("hw_on_differential_equations_bot_token")

if TELEGRAM_BOT_TOKEN is None:
    raise RuntimeError("Переменная окружения hw_on_differential_equations_bot_token не установлена!")


TEACHER_PASSWORD = "securepassword"


CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "config_path.txt")


# Функция для загрузки FILES_DIR из config_path.txt
def load_files_dir():
    try:
        if not os.path.exists(CONFIG_FILE_PATH):
            raise FileNotFoundError(f"Файл {CONFIG_FILE_PATH} не найден. Убедитесь, что он существует.")

        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith("FILES_DIR="):
                    files_dir = line.strip().split("=", 1)[1]

                    if not os.path.exists(files_dir):
                        os.makedirs(files_dir)
                        print(f"Папка {files_dir} была создана.")

                    return files_dir

            raise ValueError("Ключ FILES_DIR не найден в файле config_path.txt. Проверьте содержимое файла.")
    except Exception as e:
        raise RuntimeError(f"Ошибка при загрузке FILES_DIR из config_path.txt: {e}")


FILES_DIR = load_files_dir()
