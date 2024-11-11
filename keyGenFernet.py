from cryptography.fernet import Fernet as fer
import json
import PyQt6.QtWidgets as QtWidgets
from PyQt6.QtWidgets import QFileDialog 
import PyQt6.uic as uic
import sys
import os
import pyperclip

last_file_dir = "" # Переменная для хранения пути последнего файла
last_file_dir_no_file = "" # Переменная для хранения пути без имени файла
directory = "keyFolder" # Переменная с названием стандартной директории, в которой будут находится ключи
full_directory = f"{os.getcwd()}\\{directory}" # Переменная которая хранит текущую директорию проекта

# Проверяем, существует ли папка, чтобы избежать ошибки
if not os.path.exists(directory):
    os.makedirs(directory)  # Создаем папку

# Инициируем интерфейс QtDesigner
app = QtWidgets.QApplication([])
win = uic.loadUi("keyGenFernetUi.ui")

# Функция для генерации ключа
def generate_key(name):
    if win.leNameKey.text() == "": # Проверяем поле с именем файла с ключом
        win.laError.setText("Ошибка: не указано имя файла")
    else: # Если имя заполнено переходим к созданию ключа
        key = fer.generate_key()
        file_name = f"{name}.key" # Задаём имя файла
        # Создаём файл в выбранной пользователем директориий (либо в стандартно установленной)
        with open(f"{win.lePathDirKey.text()}/{file_name}", "wb") as key_file: 
            key_file.write(key)
        # Обращаемся к глобальным переменным
        global last_file_dir, last_file_dir_no_file
        last_file_dir_no_file = win.lePathDirKey.text()
        last_file_dir = f"{win.lePathDirKey.text()}/{file_name}"

        win.leSelectKey.setText(file_name)
        win.laError.setText(f"Ключ {file_name} создан.")
        win.bCopyPathKey.setEnabled(True)
        win.bOpenFolderKey.setEnabled(True)

# Функция для загрузки ключа из файла
def load_key(keyname):
    with open(keyname, "rb") as key_file:
        return key_file.read()
    
# Шаг 2: Зашифруйте токен и сохраните его в JSON
def encrypt_and_save(text):
    key = load_key(f"{win.lePathDirKey.text()}\\{win.leSelectKey.text()}")
    fernet = fer(key)
    encrypted_token = fernet.encrypt(text.encode())
    filename = f"{win.lePathDirKey.text()}\\encrypt.json"
    # Сохраняем зашифрованный токен в JSON-файл
    with open(filename, "w") as json_file:
        json.dump({"encrypted_" : encrypted_token.decode()}, json_file)
    return filename

def load_and_decrypt(filename):
    key = load_key(f"{win.lePathDirKey.text()}\\{win.leSelectKey.text()}")
    fernet = fer(key)
    
    # Читаем зашифрованный токен из JSON-файла
    with open(filename, "r") as json_file:
        data = json.load(json_file)
        encrypted_text = data["encrypted_"]
    
    # Расшифровываем токен
    decrypted_text = fernet.decrypt(encrypted_text.encode()).decode()
    return decrypted_text

def selectFolderKey():
    directory = QFileDialog.getExistingDirectory(win, "Выберите директорию")
    if directory:
        win.lePathDirKey.setText(directory)

def selectKey():
    file_path, _ = QFileDialog.getOpenFileName(win, "Выберите файл")
        
    if file_path:  # Если файл выбран
        win.lePathDirKey.setText(os.path.dirname(file_path))
        win.leSelectKey.setText(os.path.basename(file_path))    

def openFolderKey(path):
    os.startfile(path)

def buttEncrypt():
    if win.teText.toPlainText() == "":
        win.laErrorText.setText("Ошибка: поле для текста пустое")
    elif win.leSelectKey.text() == "":
        win.laErrorText.setText("Ошибка: не выбран ключ")
    else:
        win.laErrorText.setText(f"Текст зашифрован в файл: {encrypt_and_save(win.teText.toPlainText())}")

def selectFileForDescrypt():
    file_path, _ = QFileDialog.getOpenFileName(win, "Выберите файл")
        
    if file_path:  # Если файл выбран
        win.leSelectFile.setText(file_path)

def buttDecrypt():
    if win.leSelectFile.text() == "":
        win.laError_2.setText("Ошибка: не выбран файл для расшифровки")
    elif win.leSelectKey.text() == "":
        win.laError_2.setText("Ошибка: не выбран ключ")
    else:
        win.teText_2.setText(load_and_decrypt(win.leSelectFile.text()))


win.lePathDirKey.setText(full_directory)

win.bGenerateKey.clicked.connect(lambda: generate_key(win.leNameKey.text()))

win.bCopyPathKey.clicked.connect(lambda: pyperclip.copy(last_file_dir))

win.bOpenFolderKey.clicked.connect(lambda: openFolderKey(last_file_dir_no_file))

win.bSetPathKey.clicked.connect(selectFolderKey)

win.bDefaultPathKey.clicked.connect(lambda: win.lePathDirKey.setText(full_directory))

win.bSelectKey.clicked.connect(selectKey)

win.bEncrypt.clicked.connect(buttEncrypt)

win.bSelectFile.clicked.connect(selectFileForDescrypt)

win.bDecrypt.clicked.connect(buttDecrypt)

win.show()
sys.exit(app.exec())