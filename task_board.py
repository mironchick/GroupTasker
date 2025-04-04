from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QFrame, QDialog, QScrollArea,
                             QLineEdit, QTextEdit, QDateEdit, QFormLayout)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QDate
from database import save_task, get_tasks, delete_task


class TaskBoard(QFrame):
    def __init__(self, group_code, user_name=None, main_window=None):
        super().__init__()
        self.group_code = group_code
        self.user_name = user_name
        self.main_window = main_window  # Сохраняем ссылку на главное окно
        self.setFixedSize(1000, 900)
        self.setStyleSheet("""
            border: 2px solid #5F7470; 
            background-color: transparent;
            border-radius: 15px;
        """)

        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Верхняя строка с элементами
        top_row = QHBoxLayout()
        top_row.setSpacing(20)

        # Надпись "Мои задачи" слева
        tasks_label = QLabel("Мои задачи")
        tasks_label.setFixedSize(200, 70)
        tasks_label.setStyleSheet("""
            background-color: #E0E2DB;
            border-radius: 15px;
            padding: 10px;
            color: #003C30;
        """)
        tasks_label.setFont(QFont("Inter", 24))
        tasks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_row.addWidget(tasks_label)

        # Растягивающий элемент
        top_row.addStretch()

        # Кнопка добавления задачи (по центру)
        btn_add_task = QPushButton("Добавить задачу")
        btn_add_task.setFixedSize(300, 70)
        btn_add_task.setStyleSheet("""
            QPushButton {
                background-color: #E0E2DB;
                border-radius: 15px;
                padding: 10px;
                font-size: 24px;
                color: #003C30;
                border: none;
            }
            QPushButton:hover {
                background-color: #D2D4C8;
            }
        """)
        btn_add_task.setFont(QFont("Inter", 24))
        btn_add_task.clicked.connect(self.add_task)
        top_row.addWidget(btn_add_task)

        # Растягивающий элемент
        top_row.addStretch()

        # Кнопка Home справа
        btn_home = QPushButton("Home")
        btn_home.setFixedSize(150, 70)
        btn_home.setStyleSheet("""
            QPushButton {
                background-color: #E0E2DB;
                border-radius: 15px;
                padding: 10px;
                font-size: 24px;
                color: #003C30;
                border: none;
            }
            QPushButton:hover {
                background-color: #D2D4C8;
            }
        """)
        btn_home.setFont(QFont("Inter", 24))
        btn_home.clicked.connect(self.show_note_board)
        top_row.addWidget(btn_home)

        main_layout.addLayout(top_row)

        # Область с задачами с прокруткой
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")

        self.tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tasks_layout.setSpacing(10)

        self.scroll_area.setWidget(self.tasks_container)
        main_layout.addWidget(self.scroll_area)

        # Загружаем существующие задачи
        self.load_tasks()

    def show_note_board(self):
        """Переключает на доску заметок"""
        if self.main_window and hasattr(self.main_window, 'content_stack'):
            self.main_window.content_stack.setCurrentIndex(1)

    def load_tasks(self):
        """Загружает задачи из базы данных."""
        # Очищаем существующие задачи перед загрузкой новых
        for i in reversed(range(self.tasks_layout.count())):
            widget = self.tasks_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        tasks = get_tasks(self.group_code, self.user_name)
        for task_id, title, description, deadline, user_name in tasks:
            self.add_task_to_board(task_id, title, description, deadline, user_name)

    def add_task_to_board(self, task_id, title, description, deadline, user_name):
        """Добавляет задачу на доску."""
        task_frame = QFrame()
        task_frame.setStyleSheet("""
            background-color: #E0E2DB;
            border-radius: 10px;
            padding: 15px;
        """)
        task_frame.setFixedWidth(950)

        task_layout = QVBoxLayout(task_frame)

        # Заголовок задачи
        title_label = QLabel(title)
        title_label.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #003C30;")
        title_label.setWordWrap(True)
        task_layout.addWidget(title_label)

        # Описание задачи
        description_label = QLabel(description)
        description_label.setFont(QFont("Inter", 16))
        description_label.setStyleSheet("color: #003C30;")
        description_label.setWordWrap(True)
        description_label.setContentsMargins(10, 0, 0, 0)
        task_layout.addWidget(description_label)

        # Дедлайн и автор
        footer_layout = QHBoxLayout()

        # Дедлайн
        deadline_label = QLabel(f"Дедлайн: {deadline}")
        deadline_label.setFont(QFont("Inter", 12))
        deadline_label.setStyleSheet("color: #5F7470;")
        footer_layout.addWidget(deadline_label)

        footer_layout.addStretch()

        # Автор
        user_label = QLabel(f"Автор: {user_name}")
        user_label.setFont(QFont("Inter", 12))
        user_label.setStyleSheet("color: #5F7470; font-style: italic;")
        footer_layout.addWidget(user_label)

        # Кнопка удаления
        btn_delete = QPushButton("❌")
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #FF6961;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #D9534F;
            }
        """)
        btn_delete.setFixedSize(40, 40)
        btn_delete.clicked.connect(lambda: self.remove_task(task_id))
        footer_layout.addWidget(btn_delete)

        task_layout.addLayout(footer_layout)
        self.tasks_layout.addWidget(task_frame)

    def add_task(self):
        """Открывает диалог добавления новой задачи."""
        if not self.user_name:
            print("Ошибка: имя пользователя не установлено")
            return

        dialog = TaskDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title = dialog.title_input.text().strip()
            description = dialog.description_input.toPlainText().strip()
            deadline = dialog.deadline_input.date().toString("dd.MM.yyyy")

            if title:
                # Сохраняем в базу данных и получаем ID задачи
                task_id = save_task(self.group_code, title, description, deadline, self.user_name)
                # Добавляем на доску
                self.add_task_to_board(task_id, title, description, deadline, self.user_name)

    def remove_task(self, task_id):
        """Удаляет задачу из базы данных и обновляет доску."""
        delete_task(task_id)
        self.load_tasks()


class TaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новая задача")
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #E0E2DB;
            }
            QLabel {
                color: #003C30;
                font-size: 16px;
            }
            QLineEdit, QTextEdit {
                background-color: white;
                color: #003C30;
                font-size: 16px;
                border: 1px solid #5F7470;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #5F7470;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #4D615E;
            }
        """)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        # Поле для названия задачи
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Введите название задачи")
        form_layout.addRow("Название:", self.title_input)

        # Поле для описания задачи
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Опишите задачу подробнее...")
        form_layout.addRow("Описание:", self.description_input)

        # Поле для дедлайна
        self.deadline_input = QDateEdit()
        self.deadline_input.setDate(QDate.currentDate().addDays(7))
        self.deadline_input.setCalendarPopup(True)
        form_layout.addRow("Дедлайн:", self.deadline_input)

        layout.addLayout(form_layout)

        # Кнопки
        button_layout = QHBoxLayout()

        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)

        btn_add = QPushButton("Добавить")
        btn_add.clicked.connect(self.accept)
        button_layout.addWidget(btn_add)

        layout.addLayout(button_layout)