import sys
import sqlite3
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox, 
                             QTableWidget, QTableWidgetItem, QTabWidget, QHeaderView)
from PyQt5.QtCore import Qt

def init_db():
    if os.path.exists('university.db'):
        return

    conn = sqlite3.connect('university.db')
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE Categories (id INTEGER PRIMARY KEY, name TEXT, salary REAL);
        CREATE TABLE Cycles (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE Teachers (id INTEGER PRIMARY KEY, last_name TEXT, first_name TEXT, patronymic TEXT, category_id INTEGER, address TEXT);
        CREATE TABLE Subjects (id INTEGER PRIMARY KEY, name TEXT, cycle_id INTEGER);
        CREATE TABLE Workload (id INTEGER PRIMARY KEY, teacher_id INTEGER, subject_id INTEGER, cycle_id INTEGER, hours INTEGER);
        CREATE TABLE Users (id INTEGER PRIMARY KEY, login TEXT, password TEXT, teacher_id INTEGER);
    ''')
  
    cursor.executescript('''
        INSERT INTO Categories VALUES (1, 'Высшая', 4140), (2, 'Первая', 3960), (3, 'Вторая', 3780);
        INSERT INTO Cycles VALUES (1, 'ОП'), (2, 'ОГСЭ'), (3, 'СД');
        
        INSERT INTO Teachers VALUES 
        (1, 'Гракова', 'У.', 'В.', 1, 'ул. Мопра, 123-3'), (2, 'Костина', 'В.', 'В.', 2, 'ул. Хлыновская, 51-20'),
        (3, 'Орлова', 'Н.', 'Н.', 3, 'ул. Озерная, 11-65'), (4, 'Романова', 'П.', 'Т.', 2, 'ул. Володарского, 5-183'),
        (5, 'Хорошавина', 'О.', 'Ю.', 3, 'ул. Богородская, 59-2'), (6, 'Перминова', 'Ж.', 'А.', 2, 'ул. Некрасова, 10-33'),
        (7, 'Комарова', 'С.', 'В.', 3, 'ул. Вятская, 18/1-11'), (8, 'Пушкова', 'Р.', 'О.', 3, 'ул. Воровского, 3-71'),
        (9, 'Семанов', 'Ф.', 'О.', 1, 'ул. Свободы, 128-19');
        
        INSERT INTO Subjects VALUES 
        (1, 'Практикум по решению задач на ЭВМ', 1), (2, 'Иностранный язык', 2), 
        (3, 'ИКТ в образовании', 3), (4, 'Компьютерное моделирование', 3), 
        (5, 'Методика обучения информатики', 3), (6, 'Основы теории информации', 3);
        
        INSERT INTO Workload VALUES 
        (1, 1, 1, 1, 200), (2, 2, 2, 2, 200), (3, 3, 2, 2, 200), (4, 4, 2, 2, 200), (5, 5, 2, 2, 200), 
        (6, 6, 3, 3, 100), (7, 7, 3, 3, 100), (8, 8, 4, 3, 100), (9, 1, 5, 3, 100), (10, 9, 5, 3, 100), 
        (11, 7, 1, 3, 200), (12, 8, 6, 3, 90);
        
        INSERT INTO Users VALUES (1, 'admin', 'admin', 1);
    ''')
    
    conn.commit()
    conn.close()

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.resize(300, 150)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Логин:"))
        self.txt_login = QLineEdit()
        self.txt_login.setText("admin")
        layout.addWidget(self.txt_login)
        
        layout.addWidget(QLabel("Пароль:"))
        self.txt_pass = QLineEdit()
        self.txt_pass.setEchoMode(QLineEdit.Password)
        self.txt_pass.setText("admin")
        layout.addWidget(self.txt_pass)
        
        self.btn_enter = QPushButton("Войти")
        self.btn_enter.clicked.connect(self.check_login)
        layout.addWidget(self.btn_enter)
        
        self.setLayout(layout)
        self.main_window = None

    def check_login(self):
        login = self.txt_login.text()
        password = self.txt_pass.text()
        
        conn = sqlite3.connect('university.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE login=? AND password=?", (login, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            self.main_window = MainWindow()
            self.main_window.show()
            self.hide()
        else:
            QMessageBox.critical(self, "Ошибка", "Неверный логин или пароль!")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Информационная система кафедры")
        self.resize(800, 500)
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab_teachers = QWidget()
        self.tabs.addTab(self.tab_teachers, "Преподаватели")
        self.setup_teachers_tab()

        self.tab_workload = QWidget()
        self.tabs.addTab(self.tab_workload, "Нагрузка")
        self.setup_workload_tab()

    def setup_teachers_tab(self):
        layout = QVBoxLayout()
        self.table_teachers = QTableWidget()
        self.table_teachers.setColumnCount(5)
        self.table_teachers.setHorizontalHeaderLabels(["Фамилия", "Имя", "Отчество", "Категория", "Оклад"])
        self.table_teachers.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        conn = sqlite3.connect('university.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.last_name, t.first_name, t.patronymic, c.name, c.salary 
            FROM Teachers t JOIN Categories c ON t.category_id = c.id
        ''')
        data = cursor.fetchall()
        conn.close()
        
        self.table_teachers.setRowCount(len(data))
        for row, record in enumerate(data):
            for col, value in enumerate(record):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table_teachers.setItem(row, col, item)
                
        layout.addWidget(self.table_teachers)
        self.tab_teachers.setLayout(layout)

    def setup_workload_tab(self):
        layout = QVBoxLayout()
        self.table_workload = QTableWidget()
        self.table_workload.setColumnCount(3)
        self.table_workload.setHorizontalHeaderLabels(["ФИО Преподавателя", "Предмет", "Объем часов"])
        self.table_workload.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        conn = sqlite3.connect('university.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.last_name || ' ' || t.first_name || ' ' || t.patronymic, s.name, w.hours 
            FROM Workload w 
            JOIN Teachers t ON w.teacher_id = t.id 
            JOIN Subjects s ON w.subject_id = s.id
        ''')
        data = cursor.fetchall()
        conn.close()
        
        self.table_workload.setRowCount(len(data))
        for row, record in enumerate(data):
            for col, value in enumerate(record):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table_workload.setItem(row, col, item)
                
        layout.addWidget(self.table_workload)
        self.tab_workload.setLayout(layout)

if __name__ == "__main__":
    init_db() 
    app = QApplication(sys.argv)
    login_win = LoginWindow()
    login_win.show()
    sys.exit(app.exec_())
