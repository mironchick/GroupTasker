from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QTextEdit, QWidget)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer
from database import save_message, get_messages
from datetime import datetime


class GroupChat(QFrame):
    def __init__(self, group_code, user_name, main_window):
        super().__init__()
        self.group_code = group_code
        self.user_name = user_name
        self.main_window = main_window
        self.last_message_id = 0
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

        # Надпись "Общий чат" слева
        chat_label = QLabel("Общий чат")
        chat_label.setFixedSize(200, 70)
        chat_label.setStyleSheet("""
            background-color: #E0E2DB;
            border-radius: 15px;
            padding: 10px;
            color: #003C30;
        """)
        chat_label.setFont(QFont("Inter", 24))
        chat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_row.addWidget(chat_label)

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

        # Область с сообщениями
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")

        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.messages_layout.setSpacing(10)

        self.scroll_area.setWidget(self.messages_container)
        main_layout.addWidget(self.scroll_area)

        # Панель ввода сообщения
        input_layout = QHBoxLayout()

        self.message_input = QTextEdit()
        self.message_input.setFixedHeight(80)
        self.message_input.setPlaceholderText("Введите сообщение...")
        self.message_input.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #5F7470;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
            }
        """)
        input_layout.addWidget(self.message_input)

        btn_send = QPushButton("Отправить")
        btn_send.setFixedSize(150, 80)
        btn_send.setStyleSheet("""
            QPushButton {
                background-color: #5F7470;
                color: white;
                border-radius: 10px;
                padding: 10px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #4D615E;
            }
        """)
        btn_send.clicked.connect(self.send_message)
        input_layout.addWidget(btn_send)

        main_layout.addLayout(input_layout)

        # Загружаем существующие сообщения
        self.load_messages()

        # Таймер для обновления чата
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_new_messages)
        self.timer.start(1000)  # Обновление каждую секунду

    def show_note_board(self):
        """Переключает на доску заметок"""
        self.main_window.content_stack.setCurrentIndex(1)

    def load_messages(self):
        """Загружает сообщения из базы данных."""
        messages = get_messages(self.group_code)
        if messages:
            self.last_message_id = messages[-1][0]  # Сохраняем ID последнего сообщения

        for msg_id, user, text, timestamp in messages:
            self.add_message_to_chat(user, text, timestamp)

    def add_message_to_chat(self, user, text, timestamp):
        """Добавляет сообщение в чат."""
        message_frame = QFrame()
        message_frame.setStyleSheet("""
            background-color: #E0E2DB;
            border-radius: 10px;
            padding: 15px;
        """)
        message_frame.setFixedWidth(950)

        message_layout = QVBoxLayout(message_frame)

        # Заголовок с именем пользователя и временем
        header_layout = QHBoxLayout()

        user_label = QLabel(user)
        user_label.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        user_label.setStyleSheet("color: #003C30;")
        header_layout.addWidget(user_label)

        # Форматируем время
        if isinstance(timestamp, str):
            time_str = timestamp
        else:
            time_str = timestamp.strftime("%H:%M %d.%m.%Y")

        time_label = QLabel(time_str)
        time_label.setFont(QFont("Inter", 10))
        time_label.setStyleSheet("color: #5F7470; font-style: italic;")
        header_layout.addWidget(time_label, alignment=Qt.AlignmentFlag.AlignRight)

        message_layout.addLayout(header_layout)

        # Текст сообщения
        text_label = QLabel(text)
        text_label.setFont(QFont("Inter", 16))
        text_label.setStyleSheet("color: #003C30;")
        text_label.setWordWrap(True)
        text_label.setContentsMargins(10, 5, 0, 0)
        message_layout.addWidget(text_label)

        self.messages_layout.addWidget(message_frame)

        # Прокручиваем вниз
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def send_message(self):
        """Отправляет сообщение в чат."""
        text = self.message_input.toPlainText().strip()
        if text:
            # Сохраняем сообщение в БД
            save_message(self.group_code, self.user_name, text)

            # Очищаем поле ввода
            self.message_input.clear()

            # Обновляем чат (новое сообщение подхватится при следующей проверке)
            self.check_new_messages()

    def check_new_messages(self):
        """Проверяет новые сообщения и добавляет их в чат."""
        new_messages = get_messages(self.group_code, self.last_message_id)
        if new_messages:
            self.last_message_id = new_messages[-1][0]  # Обновляем ID последнего сообщения
            for msg_id, user, text, timestamp in new_messages:
                self.add_message_to_chat(user, text, timestamp)