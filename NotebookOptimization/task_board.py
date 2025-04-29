from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QFrame, QDialog, QScrollArea,
                             QLineEdit, QTextEdit, QDateEdit, QFormLayout)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QDate
from database import save_task, get_tasks, delete_task
from datetime import date


class TaskBoard(QFrame):
    def __init__(self, group_code, user_name=None, main_window=None):
        super().__init__()
        self.group_code = group_code
        self.user_name = user_name
        self.main_window = main_window
        self.setFixedSize(800, 600)  # Уменьшенный размер
        self.setStyleSheet("""
            border: 2px solid #5F7470; 
            background-color: transparent;
            border-radius: 10px;
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Верхняя строка
        top_row = QHBoxLayout()
        top_row.setSpacing(15)

        tasks_label = QLabel("Мои задачи")
        tasks_label.setFixedSize(150, 50)
        tasks_label.setStyleSheet("""
            background-color: #E0E2DB;
            border-radius: 10px;
            padding: 5px;
            color: #003C30;
        """)
        tasks_label.setFont(QFont("Inter", 16))
        tasks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_row.addWidget(tasks_label)

        top_row.addStretch()

        btn_add_task = QPushButton("Добавить задачу")
        btn_add_task.setFixedSize(200, 50)
        btn_add_task.setStyleSheet("""
            QPushButton {
                background-color: #E0E2DB;
                border-radius: 10px;
                padding: 5px;
                font-size: 16px;
                color: #003C30;
                border: none;
            }
            QPushButton:hover {
                background-color: #D2D4C8;
            }
        """)
        btn_add_task.setFont(QFont("Inter", 16))
        btn_add_task.clicked.connect(self.add_task)
        top_row.addWidget(btn_add_task)

        top_row.addStretch()

        btn_home = QPushButton("Home")
        btn_home.setFixedSize(120, 50)
        btn_home.setStyleSheet("""
            QPushButton {
                background-color: #E0E2DB;
                border-radius: 10px;
                padding: 5px;
                font-size: 16px;
                color: #003C30;
                border: none;
            }
            QPushButton:hover {
                background-color: #D2D4C8;
            }
        """)
        btn_home.setFont(QFont("Inter", 16))
        btn_home.clicked.connect(self.show_note_board)
        top_row.addWidget(btn_home)

        main_layout.addLayout(top_row)

        # Область с задачами
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")

        self.tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tasks_layout.setSpacing(8)

        self.scroll_area.setWidget(self.tasks_container)
        main_layout.addWidget(self.scroll_area)

        self.load_tasks()

    def show_note_board(self):
        if self.main_window:
            self.main_window.content_stack.setCurrentIndex(1)

    def load_tasks(self):
        for i in reversed(range(self.tasks_layout.count())):
            widget = self.tasks_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        tasks = get_tasks(self.group_code, self.user_name)
        for task_id, title, description, deadline, user_name in tasks:
            self.add_task_to_board(task_id, title, description, deadline, user_name)

    def add_task_to_board(self, task_id, title, description, deadline, user_name):
        task_frame = QFrame()
        task_frame.setStyleSheet("""
            background-color: #E0E2DB;
            border-radius: 8px;
            padding: 10px;
        """)
        task_frame.setFixedWidth(750)

        task_layout = QVBoxLayout(task_frame)

        # Заголовок задачи
        title_label = QLabel(title)
        title_label.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #003C30;")
        task_layout.addWidget(title_label)

        # Описание задачи
        if description:
            desc_label = QLabel(description)
            desc_label.setFont(QFont("Inter", 12))
            desc_label.setStyleSheet("color: #003C30;")
            desc_label.setContentsMargins(10, 0, 0, 0)
            task_layout.addWidget(desc_label)

        # Дедлайн и управление
        footer_layout = QHBoxLayout()

        # Форматируем дедлайн
        deadline_str = deadline.strftime("%d.%m.%Y") if isinstance(deadline, date) else deadline
        deadline_label = QLabel(f"Дедлайн: {deadline_str}")
        deadline_label.setFont(QFont("Inter", 10))
        deadline_label.setStyleSheet("color: #5F7470;")
        footer_layout.addWidget(deadline_label)

        footer_layout.addStretch()

        # Оставшееся время
        try:
            deadline_date = QDate.fromString(deadline_str, "dd.MM.yyyy") if isinstance(deadline_str, str) else QDate(
                deadline.year, deadline.month, deadline.day)
            current_date = QDate.currentDate()
            days_left = current_date.daysTo(deadline_date)

            if days_left > 0:
                time_left_text = f"Осталось дней: {days_left}"
                time_left_color = "#5F7470"
            elif days_left == 0:
                time_left_text = "Дедлайн сегодня!"
                time_left_color = "#FFA500"
            else:
                time_left_text = "Просрочено!"
                time_left_color = "#FF6961"
        except:
            time_left_text = "Ошибка даты"
            time_left_color = "#FF0000"

        time_left_label = QLabel(time_left_text)
        time_left_label.setFont(QFont("Inter", 10))
        time_left_label.setStyleSheet(f"color: {time_left_color}; font-style: italic;")
        footer_layout.addWidget(time_left_label)

        # Кнопка удаления
        btn_delete = QPushButton("Удалить")
        btn_delete.setFixedSize(80, 30)
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #FF6961;
                color: white;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #D9534F;
            }
        """)
        btn_delete.clicked.connect(lambda: self.remove_task(task_id))
        footer_layout.addWidget(btn_delete)

        task_layout.addLayout(footer_layout)
        self.tasks_layout.addWidget(task_frame)

    def add_task(self):
        if not self.user_name:
            return

        dialog = TaskDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title = dialog.title_input.text().strip()
            description = dialog.description_input.toPlainText().strip()
            deadline = dialog.deadline_input.date().toString("dd.MM.yyyy")

            if title:
                task_id = save_task(self.group_code, title, description, deadline, self.user_name)
                self.add_task_to_board(task_id, title, description, deadline, self.user_name)

    def remove_task(self, task_id):
        delete_task(task_id)
        self.load_tasks()


class TaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новая задача")
        self.setFixedSize(500, 350)  # Уменьшенный размер

        layout = QVBoxLayout(self)
        self.setStyleSheet("""
            QDialog {
                background-color: #E0E2DB;
            }
            QLabel {
                color: #003C30;
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
                background-color: white;
                color: #003C30;
                font-size: 14px;
                border: 1px solid #5F7470;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #5F7470;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4D615E;
            }
        """)

        form_layout = QFormLayout()

        # Название задачи
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Введите название задачи")
        form_layout.addRow("Название:", self.title_input)

        # Описание задачи
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Опишите задачу...")
        self.description_input.setFixedHeight(100)
        form_layout.addRow("Описание:", self.description_input)

        # Дедлайн
        self.deadline_input = QDateEdit()
        self.deadline_input.setDate(QDate.currentDate().addDays(7))
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setStyleSheet("""
            QDateEdit {
                background-color: white;
            }
            QCalendarWidget QWidget {
                background-color: #F0F0F0;
            }
        """)
        form_layout.addRow("Дедлайн:", self.deadline_input)

        layout.addLayout(form_layout)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)

        btn_add = QPushButton("Добавить")
        btn_add.clicked.connect(self.accept)
        button_layout.addWidget(btn_add)

        layout.addLayout(button_layout)