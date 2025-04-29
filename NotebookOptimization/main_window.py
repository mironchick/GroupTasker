from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
                            QListWidget, QFrame, QStackedWidget)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from note_board import NoteBoard
from group_view import GroupView
from task_board import TaskBoard
from group_chat import GroupChat
from personal_chat import PersonalChat

class MainWindow(QWidget):
    def __init__(self, stacked_widget, user_name, group_code):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.user_name = user_name
        self.group_code = group_code
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("GroupTasker - Главное окно")
        self.setFixedSize(1200, 700)
        self.setStyleSheet("background-color: #F0F0F0;")

        main_layout = QVBoxLayout(self)

        # Верхняя панель
        header_layout = QHBoxLayout()
        back_label = QLabel("Back")
        back_label.setFont(QFont("Inter", 24))
        back_label.setStyleSheet("color: #5F7470;")
        back_label.mousePressEvent = self.on_back_click

        lbl_username = QLabel(self.user_name)
        lbl_username.setFont(QFont("Inter", 24))
        lbl_username.setStyleSheet("color: #5F7470;")
        lbl_username.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_appname = QLabel("GroupTasker")
        lbl_appname.setFont(QFont("Inter", 24))
        lbl_appname.setStyleSheet("color: #5F7470;")
        lbl_appname.setAlignment(Qt.AlignmentFlag.AlignRight)

        header_layout.addWidget(back_label)
        header_layout.addStretch()
        header_layout.addWidget(lbl_username, alignment=Qt.AlignmentFlag.AlignCenter)
        header_layout.addStretch()
        header_layout.addWidget(lbl_appname)

        main_layout.addLayout(header_layout)

        # Центральная часть
        content_layout = QHBoxLayout()

        # Боковое меню (как было изначально)
        menu_frame = QFrame()
        menu_frame.setFixedSize(250, 700)
        menu_frame.setStyleSheet("""
            background-color: #E0E2DB; 
            border-radius: 15px;
        """)

        menu_layout = QVBoxLayout(menu_frame)
        menu_layout.setContentsMargins(20, 20, 20, 20)

        def create_menu_button(text):
            btn = QPushButton(text)
            btn.setFont(QFont("Inter", 20))
            btn.setStyleSheet("""
                QPushButton { 
                    color: #003C30; 
                    background-color: transparent; 
                    border: none; 
                    text-align: left;
                    padding: 10px;
                }
                QPushButton:hover { 
                    font-weight: bold; 
                    background-color: #D2D4C8;
                    border-radius: 10px;
                }
            """)
            return btn

        btn_group = create_menu_button("Группа")
        btn_tasks = create_menu_button("Мои задачи")
        btn_chat = create_menu_button("Общий чат")
        btn_messages = create_menu_button("Личные сообщения")

        # StackedWidget для переключения вкладок
        self.content_stack = QStackedWidget()

        # Создаем все виджеты вкладок
        self.group_view = GroupView(self.group_code, self)
        self.note_board = NoteBoard(self.group_code, self.user_name)
        self.task_board = TaskBoard(self.group_code, self.user_name, self)
        self.group_chat = GroupChat(self.group_code, self.user_name, self)
        self.personal_chat = PersonalChat(self.group_code, self.user_name, self)

        # Добавляем вкладки (индексы как были)
        self.content_stack.addWidget(self.group_view)    # 0 - Группа
        self.content_stack.addWidget(self.note_board)    # 1 - Доска заметок
        self.content_stack.addWidget(self.task_board)    # 2 - Мои задачи
        self.content_stack.addWidget(self.group_chat)    # 3 - Общий чат
        self.content_stack.addWidget(self.personal_chat) # 4 - Личные сообщения

        # По умолчанию показываем доску заметок
        self.content_stack.setCurrentIndex(1)

        # Подключаем кнопки меню
        btn_group.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))
        btn_tasks.clicked.connect(lambda: self.content_stack.setCurrentIndex(2))  # Задачи
        btn_chat.clicked.connect(lambda: self.content_stack.setCurrentIndex(3))   # Чат
        btn_messages.clicked.connect(lambda: self.content_stack.setCurrentIndex(4))  # Сообщения

        menu_layout.addWidget(btn_group)
        menu_layout.addWidget(btn_tasks)
        menu_layout.addWidget(btn_chat)
        menu_layout.addWidget(btn_messages)
        menu_layout.addStretch()

        content_layout.addWidget(menu_frame)
        content_layout.addWidget(self.content_stack)

        main_layout.addLayout(content_layout)

    def on_back_click(self, event):
        """Возвращает в главное меню."""
        self.stacked_widget.setCurrentIndex(0)
        self.close()