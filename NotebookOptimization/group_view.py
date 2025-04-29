from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
                             QScrollArea, QListWidget, QListWidgetItem, QPushButton,
                             QMessageBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from database import execute_query


class GroupView(QFrame):
    def __init__(self, group_code, main_window):
        super().__init__()
        self.group_code = group_code
        self.main_window = main_window
        self.setFixedSize(800, 600)  # Уменьшенный размер
        self.setStyleSheet("""
            border: 2px solid #5F7470; 
            background-color: transparent;
            border-radius: 10px;
        """)

        # Устанавливаем стиль для QMessageBox
        self.set_message_box_style()

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Верхняя строка
        top_row = QHBoxLayout()
        top_row.setSpacing(15)

        members_label = QLabel("Участники")
        members_label.setFixedSize(150, 50)
        members_label.setStyleSheet("""
            background-color: #E0E2DB;
            border-radius: 10px;
            padding: 5px;
            color: #003C30;
        """)
        members_label.setFont(QFont("Inter", 16))
        members_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_row.addWidget(members_label)

        top_row.addStretch()

        self.group_name_label = QLabel()
        self.group_name_label.setFixedSize(250, 50)
        self.group_name_label.setStyleSheet("""
            background-color: #E0E2DB;
            border-radius: 10px;
            padding: 5px;
            color: #003C30;
        """)
        self.group_name_label.setFont(QFont("Inter", 16))
        self.group_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_row.addWidget(self.group_name_label)

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

        # Список участников
        self.members_list = QListWidget()
        self.members_list.setStyleSheet("""
            QListWidget {
                background-color: #E0E2DB;
                border-radius: 10px;
                padding: 5px;
                border: none;
                color: #003C30;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #5F7470;
            }
            QListWidget::item:selected {
                background-color: #D2D4C8;
            }
        """)
        self.members_list.setFont(QFont("Inter", 14))
        main_layout.addWidget(self.members_list)

        # Кнопки управления
        self.btn_remove_member = QPushButton("Исключить участника")
        self.btn_remove_member.setFixedHeight(40)
        self.btn_remove_member.setStyleSheet("""
            QPushButton {
                background-color: #E0E2DB;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
                color: #003C30;
                border: none;
            }
            QPushButton:hover {
                background-color: #D2D4C8;
            }
            QPushButton:disabled {
                color: #5F7470;
            }
        """)
        self.btn_remove_member.setFont(QFont("Inter", 14))
        self.btn_remove_member.clicked.connect(self.remove_member)
        main_layout.addWidget(self.btn_remove_member)

        self.btn_leave_group = QPushButton("Покинуть группу")
        self.btn_leave_group.setFixedHeight(40)
        self.btn_leave_group.setStyleSheet("""
            QPushButton {
                background-color: #FF6961;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #D9534F;
            }
            QPushButton:disabled {
                background-color: #5F7470;
            }
        """)
        self.btn_leave_group.setFont(QFont("Inter", 14))
        self.btn_leave_group.clicked.connect(self.leave_group)
        main_layout.addWidget(self.btn_leave_group)

        self.btn_delete_group = QPushButton("Удалить группу")
        self.btn_delete_group.setFixedHeight(40)
        self.btn_delete_group.setStyleSheet("""
            QPushButton {
                background-color: #FF6961;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #D9534F;
            }
            QPushButton:disabled {
                background-color: #5F7470;
            }
        """)
        self.btn_delete_group.setFont(QFont("Inter", 14))
        self.btn_delete_group.clicked.connect(self.delete_group)
        main_layout.addWidget(self.btn_delete_group)

        self.load_group_data()

    def set_message_box_style(self):
        """Устанавливает светлый стиль для всех QMessageBox"""
        style = """
            QMessageBox {
                background-color: #E0E2DB;
                color: #003C30;
            }
            QMessageBox QLabel {
                color: #003C30;
                font: 14px "Inter";
            }
            QMessageBox QPushButton {
                background-color: #5F7470;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
                min-width: 80px;
                font: 14px "Inter";
            }
            QMessageBox QPushButton:hover {
                background-color: #003C30;
            }
        """
        self.setStyleSheet(style)  # Устанавливаем стиль для текущего виджета и его дочерних элементов

    def show_note_board(self):
        self.main_window.content_stack.setCurrentIndex(1)

    def load_group_data(self):
        try:
            group_info = execute_query(
                """SELECT g.name, u.name as creator 
                   FROM groups g JOIN users u ON g.id = u.group_id
                   WHERE g.code = %s ORDER BY u.id LIMIT 1;""",
                (self.group_code,),
                fetch_one=True
            )

            if group_info:
                self.group_name_label.setText(group_info['name'])
                self.is_creator = (group_info['creator'] == self.main_window.user_name)
                self.btn_remove_member.setEnabled(self.is_creator)
                self.btn_delete_group.setEnabled(self.is_creator)
                self.btn_leave_group.setEnabled(not self.is_creator)

            members = execute_query(
                """SELECT u.name FROM users u
                   JOIN groups g ON u.group_id = g.id
                   WHERE g.code = %s ORDER BY u.name;""",
                (self.group_code,),
                fetch_all=True
            )

            self.members_list.clear()
            for member in members:
                item = QListWidgetItem(member['name'])
                self.members_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке данных группы: {e}")

    def remove_member(self):
        selected_items = self.members_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите участника для исключения")
            return

        member_name = selected_items[0].text()
        if member_name == self.main_window.user_name:
            QMessageBox.warning(self, "Ошибка", "Вы не можете исключить себя")
            return

        reply = QMessageBox.question(
            self,
            'Подтверждение',
            f'Вы уверены, что хотите исключить участника {member_name}?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                execute_query(
                    """DELETE FROM users 
                       WHERE name = %s AND group_id = (
                           SELECT id FROM groups WHERE code = %s
                       );""",
                    (member_name, self.group_code),
                    commit=True
                )
                self.load_group_data()
                QMessageBox.information(self, "Успех", f"Участник {member_name} исключен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось исключить участника: {str(e)}")

    def leave_group(self):
        reply = QMessageBox.question(
            self,
            'Подтверждение',
            'Вы уверены, что хотите покинуть группу?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                execute_query(
                    """DELETE FROM users 
                       WHERE name = %s AND group_id = (
                           SELECT id FROM groups WHERE code = %s
                       );""",
                    (self.main_window.user_name, self.group_code),
                    commit=True
                )
                QMessageBox.information(self, "Успех", "Вы покинули группу")
                self.main_window.on_back_click(None)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось покинуть группу: {str(e)}")

    def delete_group(self):
        reply = QMessageBox.question(
            self,
            'Подтверждение',
            'Вы уверены, что хотите удалить группу? Это действие нельзя отменить!',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Сначала удаляем всех пользователей группы
                execute_query(
                    "DELETE FROM users WHERE group_id = (SELECT id FROM groups WHERE code = %s);",
                    (self.group_code,),
                    commit=True
                )

                # Затем удаляем саму группу
                execute_query(
                    "DELETE FROM groups WHERE code = %s;",
                    (self.group_code,),
                    commit=True
                )

                QMessageBox.information(self, "Успех", "Группа удалена")
                self.main_window.on_back_click(None)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить группу: {str(e)}")