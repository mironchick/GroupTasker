from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
                             QScrollArea, QListWidget, QListWidgetItem, QPushButton,
                             QMessageBox)
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

        # Кнопка удаления участника
        self.btn_remove_member = QPushButton("Исключить участника")
        self.btn_remove_member.setFixedHeight(60)
        self.btn_remove_member.setStyleSheet("""
            QPushButton {
                background-color: #E0E2DB;
                border-radius: 15px;
                padding: 10px;
                font-size: 20px;
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
        self.btn_remove_member.setFont(QFont("Inter", 20))
        self.btn_remove_member.clicked.connect(self.remove_member)
        main_layout.addWidget(self.btn_remove_member)

        # Кнопка выхода из группы
        self.btn_leave_group = QPushButton("Покинуть группу")
        self.btn_leave_group.setFixedHeight(60)
        self.btn_leave_group.setStyleSheet("""
            QPushButton {
                background-color: #FF6961;
                border-radius: 15px;
                padding: 10px;
                font-size: 20px;
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
        self.btn_leave_group.setFont(QFont("Inter", 20))
        self.btn_leave_group.clicked.connect(self.leave_group)
        main_layout.addWidget(self.btn_leave_group)

        # Кнопка удаления группы
        self.btn_delete_group = QPushButton("Удалить группу")
        self.btn_delete_group.setFixedHeight(60)
        self.btn_delete_group.setStyleSheet("""
            QPushButton {
                background-color: #FF6961;
                border-radius: 15px;
                padding: 10px;
                font-size: 20px;
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
        self.btn_delete_group.setFont(QFont("Inter", 20))
        self.btn_delete_group.clicked.connect(self.delete_group)
        main_layout.addWidget(self.btn_delete_group)

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
                # Получаем название группы и создателя
                cursor.execute("""
                    SELECT g.name, u.name as creator 
                    FROM groups g
                    JOIN users u ON g.id = u.group_id
                    WHERE g.code = %s
                    ORDER BY u.id LIMIT 1;
                """, (self.group_code,))
                group_info = cursor.fetchone()

                if group_info:
                    self.group_name_label.setText(group_info['name'])
                    self.is_creator = (group_info['creator'] == self.main_window.user_name)

                    # Активируем кнопки в зависимости от роли пользователя
                    self.btn_remove_member.setEnabled(self.is_creator)
                    self.btn_delete_group.setEnabled(self.is_creator)
                    self.btn_leave_group.setEnabled(not self.is_creator)

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
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Ошибка")
            msg.setText(f"Ошибка при загрузке данных группы: {e}")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #F0F0F0;
                }
                QLabel {
                    color: #003C30;
                }
            """)
            msg.exec()
        finally:
            if conn:
                conn.close()

    def remove_member(self):
        """Удаляет выбранного участника из группы."""
        selected_items = self.members_list.selectedItems()
        if not selected_items:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Ошибка")
            msg.setText("Выберите участника для исключения")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #F0F0F0;
                }
                QLabel {
                    color: #003C30;
                }
            """)
            msg.exec()
            return

        member_name = selected_items[0].text()
        if member_name == self.main_window.user_name:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Ошибка")
            msg.setText("Вы не можете исключить себя")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #F0F0F0;
                }
                QLabel {
                    color: #003C30;
                }
            """)
            msg.exec()
            return

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle('Подтверждение')
        msg.setText(f'Вы уверены, что хотите исключить участника {member_name}?')
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #F0F0F0;
            }
            QLabel {
                color: #003C30;
            }
        """)

        if msg.exec() == QMessageBox.StandardButton.Yes:
            try:
                conn = psycopg2.connect(
                    dbname="grouptasker",
                    user="postgres",
                    password="123456",
                    host="localhost"
                )
                with conn.cursor() as cursor:
                    cursor.execute("""
                        DELETE FROM users 
                        WHERE name = %s AND group_id = (
                            SELECT id FROM groups WHERE code = %s
                        );
                    """, (member_name, self.group_code))
                    conn.commit()

                    self.load_group_data()

                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setWindowTitle("Успех")
                    msg.setText(f"Участник {member_name} исключен")
                    msg.setStyleSheet("""
                        QMessageBox {
                            background-color: #F0F0F0;
                        }
                        QLabel {
                            color: #003C30;
                        }
                    """)
                    msg.exec()

            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowTitle("Ошибка")
                msg.setText(f"Не удалось исключить участника: {str(e)}")
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #F0F0F0;
                    }
                    QLabel {
                        color: #003C30;
                    }
                """)
                msg.exec()
            finally:
                if conn:
                    conn.close()

    def leave_group(self):
        """Позволяет пользователю покинуть группу."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle('Подтверждение')
        msg.setText('Вы уверены, что хотите покинуть группу?')
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #F0F0F0;
            }
            QLabel {
                color: #003C30;
            }
        """)

        if msg.exec() == QMessageBox.StandardButton.Yes:
            try:
                conn = psycopg2.connect(
                    dbname="grouptasker",
                    user="postgres",
                    password="123456",
                    host="localhost"
                )
                with conn.cursor() as cursor:
                    cursor.execute("""
                        DELETE FROM users 
                        WHERE name = %s AND group_id = (
                            SELECT id FROM groups WHERE code = %s
                        );
                    """, (self.main_window.user_name, self.group_code))
                    conn.commit()

                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setWindowTitle("Успех")
                    msg.setText("Вы покинули группу")
                    msg.setStyleSheet("""
                        QMessageBox {
                            background-color: #F0F0F0;
                        }
                        QLabel {
                            color: #003C30;
                        }
                    """)
                    msg.exec()

                    self.main_window.on_back_click(None)

            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowTitle("Ошибка")
                msg.setText(f"Не удалось покинуть группу: {str(e)}")
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #F0F0F0;
                    }
                    QLabel {
                        color: #003C30;
                    }
                """)
                msg.exec()
            finally:
                if conn:
                    conn.close()

    def delete_group(self):
        """Удаляет группу полностью."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle('Подтверждение')
        msg.setText('Вы уверены, что хотите удалить группу? Это действие нельзя отменить!')
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #F0F0F0;
            }
            QLabel {
                color: #003C30;
            }
        """)

        if msg.exec() == QMessageBox.StandardButton.Yes:
            try:
                conn = psycopg2.connect(
                    dbname="grouptasker",
                    user="postgres",
                    password="123456",
                    host="localhost"
                )
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM groups WHERE code = %s;", (self.group_code,))
                    conn.commit()

                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setWindowTitle("Успех")
                    msg.setText("Группа удалена")
                    msg.setStyleSheet("""
                        QMessageBox {
                            background-color: #F0F0F0;
                        }
                        QLabel {
                            color: #003C30;
                        }
                    """)
                    msg.exec()

                    self.main_window.on_back_click(None)

            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowTitle("Ошибка")
                msg.setText(f"Не удалось удалить группу: {str(e)}")
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #F0F0F0;
                    }
                    QLabel {
                        color: #003C30;
                    }
                """)
                msg.exec()
            finally:
                if conn:
                    conn.close()