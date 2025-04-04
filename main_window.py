from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QFrame, QStackedWidget
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from note_board import NoteBoard
from group_view import GroupView
from task_board import TaskBoard  # Импорт новой вкладки задач


class MainWindow(QWidget):
    def __init__(self, stacked_widget, user_name, group_code):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.user_name = user_name
        self.group_code = group_code

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("GroupTasker - Главное окно")
        self.setGeometry(100, 100, 1440, 1080)
        self.setStyleSheet("background-color: #F0F0F0;")

        main_layout = QVBoxLayout(self)

        # Верхняя панель
        header_layout = QHBoxLayout()

        btn_back = QLabel("Back")
        btn_back.setFont(QFont("Inter", 48))
        btn_back.setStyleSheet("color: #5F7470;")
        btn_back.mousePressEvent = self.on_back_click

        lbl_username = QLabel(self.user_name)
        lbl_username.setFont(QFont("Inter", 48))
        lbl_username.setStyleSheet("color: #5F7470;")
        lbl_username.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_appname = QLabel("GroupTasker")
        lbl_appname.setFont(QFont("Inter", 48))
        lbl_appname.setStyleSheet("color: #5F7470;")
        lbl_appname.setAlignment(Qt.AlignmentFlag.AlignRight)

        header_layout.addWidget(btn_back)
        header_layout.addStretch()
        header_layout.addWidget(lbl_username, alignment=Qt.AlignmentFlag.AlignCenter)
        header_layout.addStretch()
        header_layout.addWidget(lbl_appname)

        main_layout.addLayout(header_layout)

        # Центральная часть
        content_layout = QHBoxLayout()

        # Боковое меню
        menu_frame = QFrame()
        menu_frame.setFixedSize(250, 900)
        menu_frame.setStyleSheet("""
            background-color: #E0E2DB; 
            border-radius: 15px;
        """)

        menu_layout = QVBoxLayout(menu_frame)
        menu_layout.setContentsMargins(20, 20, 20, 20)

        def create_menu_button(text):
            btn = QPushButton(text)
            btn.setFont(QFont("Inter", 24))
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

        # Создаем stacked widget для переключения между вкладками
        self.content_stack = QStackedWidget()

        # Создаем все виджеты
        self.group_view = GroupView(self.group_code, self)
        self.note_board = NoteBoard(self.group_code, self.user_name)
        self.task_board = TaskBoard(self.group_code, self.user_name, self) # Новая вкладка задач

        # Добавляем их в stacked widget
        self.content_stack.addWidget(self.group_view)    # Индекс 0 - Группа
        self.content_stack.addWidget(self.note_board)   # Индекс 1 - Доска заметок
        self.content_stack.addWidget(self.task_board)   # Индекс 2 - Мои задачи

        # По умолчанию показываем доску заметок (как было раньше)
        self.content_stack.setCurrentIndex(1)

        # Подключаем кнопки меню
        btn_group.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))  # Группа
        btn_tasks.clicked.connect(lambda: self.content_stack.setCurrentIndex(2))  # Теперь открывает задачи

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