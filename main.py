import sys
import pyodbc
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox, 
                             QTableWidget, QTableWidgetItem, QTabWidget, QHeaderView)
from PyQt5.QtCore import Qt

CONN_STR = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=localhost;"         # Или имя вашего сервера, например .\SQLEXPRESS
    r"DATABASE=UniversityDB;"
    r"Trusted_Connection=yes;"
)


def get_connection():
    """Функция для получения подключения к БД"""
    try:
        conn = pyodbc.connect(CONN_STR)
        return conn
    except Exception as e:
        QMessageBox.critical(None, "Ошибка подключения", f"Не удалось подключиться к SQL Server:\n{e}")
        sys.exit(1)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация в ИС Кафедры")
        self.resize(300, 180)
        
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
        
        try:
            conn = get_connection()
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
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Информационная система кафедры")
        self.resize(850, 500)
        
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
        
        try:
            conn = get_connection()
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
                    item = QTableWidgetItem(str(value).strip()) 
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.table_teachers.setItem(row, col, item)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
                
        layout.addWidget(self.table_teachers)
        self.tab_teachers.setLayout(layout)

    def setup_workload_tab(self):
        layout = QVBoxLayout()
        self.table_workload = QTableWidget()
        self.table_workload.setColumnCount(3)
        self.table_workload.setHorizontalHeaderLabels(["ФИО Преподавателя", "Предмет", "Объем часов"])
        self.table_workload.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.last_name + ' ' + t.first_name + ' ' + t.patronymic, s.name, w.hours 
                FROM Workload w 
                JOIN Teachers t ON w.teacher_id = t.id 
                JOIN Subjects s ON w.subject_id = s.id
            ''')
            data = cursor.fetchall()
            conn.close()
            
            self.table_workload.setRowCount(len(data))
            for row, record in enumerate(data):
                for col, value in enumerate(record):
                    item = QTableWidgetItem(str(value).strip())
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.table_workload.setItem(row, col, item)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
                
        layout.addWidget(self.table_workload)
        self.tab_workload.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    get_connection() 
    
    login_win = LoginWindow()
    login_win.show()
    sys.exit(app.exec_())
