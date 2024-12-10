from openpyxl import load_workbook, Workbook
import os
import re

# Функция для извлечения даты из имени файла
def extract_date_from_filename(file_name):
    """
    Извлекает дату из имени файла в формате tasks_дд.мм.гггг.
    :param file_name: Имя файла (например, 'tasks_12.12.2023.txt').
    :return: Дата в формате строки (например, '12.12.2023') или None, если дата не найдена.
    """
    date_pattern = r"tasks_(\d{2}\.\d{2}\.\d{4})"
    match = re.search(date_pattern, file_name)
    if match:
        return match.group(1)
    return None
# Функция для записи даты в фыйл
def write_to_excel(date, excel_folder_path, output_file="new_wb.xlsx"):
    excel_file_path = os.path.join(excel_folder_path, output_file)

    if os.path.exists(excel_file_path):
        wb = load_workbook(excel_file_path)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws['A1'] = "Дата"  # Заголовок, если файл создаётся впервые

    next_row = ws.max_row + 1
    ws[f'A{next_row}'] = date

    wb.save(excel_file_path)
    print(f"Дата {date} добавлена в файл: {excel_file_path}")


# Основная функция для обработки файлов в указанной папке
def process_files(folder_path, excel_folder_path):
    for file_name in os.listdir(folder_path):
        if file_name.startswith("tasks_"):
            date = extract_date_from_filename(file_name)
            if date:
                print(f"Дата извлечена: {date}")
                write_to_excel(date, excel_folder_path)
            else:
                print(f"В файле {file_name} не найдена дата.")

folder_path = r"C:\Users\Инстаблогерша\OneDrive\Desktop\bot_py\hw_on_differential_equations_bot\tasks"  # Папка с вашими файлами
excel_folder_path = r"C:\Users\Инстаблогерша\OneDrive\Desktop\bot_py\hw_on_differential_equations_bot\bot\data"  # Папка для Excel-файла

process_files(folder_path, excel_folder_path)
