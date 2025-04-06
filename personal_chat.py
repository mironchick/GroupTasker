from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QTextEdit, QWidget,
                             QMessageBox, QListWidget, QListWidgetItem)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer, QDateTime
from database import (get_group_users, get_private_messages,
                      save_private_message, delete_private_message,
                      get_private_message_count)


class PersonalChat(QFrame):
    def __init__(self, group_code, user_name, main_window):
        super().__init__()
        self.group_code = group_code
        self.user_name = user_name
        self.main_window = main_window
        self.current_chat_user = None
        self.last_update_time = QDateTime.currentDateTime()
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

        chat_label = QLabel("Личные сообщения")
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

        top_row.addStretch()

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

        # Основное содержимое
        content_layout = QHBoxLayout()

        # Список пользователей
        self.users_list = QListWidget()
        self.users_list.setFixedWidth(250)
        self.users_list.setStyleSheet("""
            QListWidget {
                background-color: #E0E2DB;
                border-radius: 15px;
                padding: 10px;
                border: none;
                color: #003C30;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #5F7470;
            }
            QListWidget::item:selected {
                background-color: #D2D4C8;
            }
        """)
        self.users_list.setFont(QFont("Inter", 18))
        self.users_list.itemClicked.connect(self.on_user_selected)
        content_layout.addWidget(self.users_list)

        # Правая часть (чат)
        chat_area = QVBoxLayout()

        # Область с сообщениями
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")

        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.messages_layout.setSpacing(10)

        self.scroll_area.setWidget(self.messages_container)
        chat_area.addWidget(self.scroll_area)

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

        chat_area.addLayout(input_layout)
        content_layout.addLayout(chat_area)
        main_layout.addLayout(content_layout)

        # Инициализация чата
        self.message_ids = set()
        self.load_group_users()

        # Таймеры для обновления
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.check_updates)
        self.update_timer.start(800)

        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.full_sync)
        self.sync_timer.start(5000)

    def show_note_board(self):
        self.main_window.content_stack.setCurrentIndex(1)

    def load_group_users(self):
        """Загружает список пользователей группы"""
        users = get_group_users(self.group_code, self.user_name)
        self.users_list.clear()
        for user in users:
            item = QListWidgetItem(user)
            self.users_list.addItem(item)

    def on_user_selected(self, item):
        """Обрабатывает выбор пользователя для чата"""
        self.current_chat_user = item.text()
        self.load_messages()

    def load_messages(self):
        """Загружает сообщения с выбранным пользователем"""
        if not self.current_chat_user:
            return

        self.clear_messages()
        messages = get_private_messages(self.group_code, self.user_name, self.current_chat_user)
        self.message_ids = {msg[0] for msg in messages}

        for msg_id, sender, receiver, text, timestamp in messages:
            self.add_message_widget(msg_id, sender, text, timestamp)

        self.scroll_to_bottom()

    def clear_messages(self):
        for i in reversed(range(self.messages_layout.count())):
            widget = self.messages_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

    def add_message_widget(self, msg_id, sender, text, timestamp):
        """Создает виджет сообщения"""
        message_frame = QFrame()
        message_frame.setStyleSheet("""
            background-color: #E0E2DB;
            border-radius: 10px;
            padding: 15px;
        """)
        message_frame.setFixedWidth(700)

        layout = QVBoxLayout(message_frame)

        # Header
        header = QHBoxLayout()
        user_label = QLabel(sender)
        user_label.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        user_label.setStyleSheet("color: #003C30;")
        header.addWidget(user_label)

        time_str = timestamp.strftime("%H:%M %d.%m.%Y") if not isinstance(timestamp, str) else timestamp
        time_label = QLabel(time_str)
        time_label.setFont(QFont("Inter", 10))
        time_label.setStyleSheet("color: #5F7470; font-style: italic;")
        header.addWidget(time_label, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(header)

        # Text
        text_label = QLabel(text)
        text_label.setFont(QFont("Inter", 16))
        text_label.setStyleSheet("color: #003C30;")
        text_label.setWordWrap(True)
        text_label.setContentsMargins(10, 5, 0, 0)
        layout.addWidget(text_label)

        # Delete button (only for user's own messages)
        if sender == self.user_name:
            footer = QHBoxLayout()
            footer.addStretch()

            btn_delete = QPushButton("Удалить")
            btn_delete.setFixedSize(100, 30)
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
            btn_delete.clicked.connect(lambda: self.delete_message(msg_id))
            footer.addWidget(btn_delete)
            layout.addLayout(footer)

        self.messages_layout.addWidget(message_frame)

    def send_message(self):
        if not self.current_chat_user or not self.message_input.toPlainText().strip():
            return

        text = self.message_input.toPlainText().strip()
        save_private_message(self.group_code, self.user_name, self.current_chat_user, text)
        self.message_input.clear()
        self.last_update_time = QDateTime.currentDateTime()
        self.check_updates(force=True)

    def delete_message(self, msg_id):
        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите удалить это сообщение?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            delete_private_message(msg_id)
            self.message_ids.discard(msg_id)
            self.last_update_time = QDateTime.currentDateTime()
            self.check_updates(force=True)

    def check_updates(self, force=False):
        """Проверяет новые и удаленные сообщения"""
        if not self.current_chat_user:
            return

        try:
            current_count = get_private_message_count(self.group_code, self.user_name, self.current_chat_user)
            current_ids = {msg[0] for msg in
                           get_private_messages(self.group_code, self.user_name, self.current_chat_user)}

            # Если количество изменилось или принудительное обновление
            if force or len(self.message_ids) != current_count:
                self.load_messages()
                return

            # Проверяем отдельные изменения
            new_ids = current_ids - self.message_ids
            removed_ids = self.message_ids - current_ids

            if new_ids or removed_ids:
                self.load_messages()

        except Exception as e:
            print(f"Ошибка при проверке обновлений: {e}")

    def full_sync(self):
        """Полная синхронизация для надежности"""
        if self.current_chat_user:
            self.check_updates(force=True)

    def scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )