from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
                             QScrollArea, QListWidget, QListWidgetItem, QPushButton)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import psycopg2
from psycopg2.extras import DictCursor


class GroupView(QFrame):
    def __init__(self, group_code, main_window):
        super().__init__()
        self.group_code = group_code
        self.main_window = main_window
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

        # Надпись "Участники" слева
        members_label = QLabel("Участники")
        members_label.setFixedSize(200, 70)
        members_label.setStyleSheet("""
            background-color: #E0E2DB;
            border-radius: 15px;
            padding: 10px;
            color: #003C30;
        """)
        members_label.setFont(QFont("Inter", 24))
        members_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_row.addWidget(members_label)

        # Растягивающий элемент слева от названия группы
        top_row.addStretch()

        # Название группы (по центру)
        self.group_name_label = QLabel()
        self.group_name_label.setFixedSize(300, 70)
        self.group_name_label.setStyleSheet("""
            background-color: #E0E2DB;
            border-radius: 15px;
            padding: 10px;
            color: #003C30;
        """)
        self.group_name_label.setFont(QFont("Inter", 24))
        self.group_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_row.addWidget(self.group_name_label)

        # Растягивающий элемент справа от названия группы
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

        # Список участников
        self.members_list = QListWidget()
        self.members_list.setStyleSheet("""
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
        self.members_list.setFont(QFont("Inter", 18))
        main_layout.addWidget(self.members_list)

        # Загружаем данные группы
        self.load_group_data()

    def show_note_board(self):
        """Переключает на доску заметок"""
        self.main_window.content_stack.setCurrentIndex(1)

    def load_group_data(self):
        """Загружает название группы и список участников из базы данных."""
        try:
            conn = psycopg2.connect(
                dbname="grouptasker",
                user="postgres",
                password="123456",
                host="localhost"
            )
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                # Получаем название группы
                cursor.execute("SELECT name FROM groups WHERE code = %s;", (self.group_code,))
                group = cursor.fetchone()
                if group:
                    self.group_name_label.setText(group['name'])

                # Получаем список участников
                cursor.execute("""
                    SELECT u.name FROM users u
                    JOIN groups g ON u.group_id = g.id
                    WHERE g.code = %s
                    ORDER BY u.name;
                """, (self.group_code,))

                self.members_list.clear()
                for user in cursor.fetchall():
                    item = QListWidgetItem(user['name'])
                    self.members_list.addItem(item)

        except Exception as e:
            print(f"Ошибка при загрузке данных группы: {e}")
        finally:
            if conn:
                conn.close()