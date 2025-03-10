from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QScrollArea, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QEvent
from database import get_groups_with_users, db_cursor  # Импортируем функции для работы с БД

class HoverLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMouseTracking(True)  # Включаем отслеживание мыши

    def enterEvent(self, event):
        """Событие при наведении на label"""
        self.setStyleSheet("background-color: #00AF8E; color: white;")
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Событие при уходе с label"""
        self.setStyleSheet("background-color: transparent; color: #5F7470;")
        super().leaveEvent(event)

class GroupsListWindow(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget  # Указатель на основное окно
        self.groups = []  # Список групп
        self.selected_group_label = None  # Лейбл выбранной группы
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Мои группы")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #F0F0F0;")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Устанавливаем фокус на виджет

        main_layout = QVBoxLayout(self)

        # Верхний заголовок
        header_layout = QHBoxLayout()
        back_label = QLabel("Back")
        back_label.setFont(QFont("Inter", 44))
        back_label.setStyleSheet("color: #5F7470;")
        back_label.mousePressEvent = self.on_back_click  # Привязка к событию

        title_label = QLabel("GroupTasker")
        title_label.setFont(QFont("Inter", 44))
        title_label.setStyleSheet("color: #5F7470;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        header_layout.addWidget(back_label)
        header_layout.addStretch()
        header_layout.addWidget(title_label)

        main_layout.addLayout(header_layout)

        # Поле с группами
        self.groups_list_widget = QWidget()
        self.groups_list_layout = QVBoxLayout(self.groups_list_widget)
        self.groups_list_layout.setSpacing(15)
        self.groups_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Создаём скролл для списка групп
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.groups_list_widget)

        # Устанавливаем стиль для скролла и закругление углов
        scroll_area.setStyleSheet("""
            background-color: #E4E4E4;
            border: none;
            border-radius: 15px;
        """)

        self.groups_list_widget.setStyleSheet("border-radius: 15px;")

        main_layout.addSpacing(50)
        main_layout.addWidget(scroll_area)
        main_layout.addSpacing(50)

        # Получаем группы из базы данных
        self.groups = get_groups_with_users()  # Получаем данные из базы данных
        for group in self.groups:
            group_label = HoverLabel(f"{group['id']}. {group['name']}, пользователь: {group['user_name']}")
            group_label.setFont(QFont("Inter", 24))
            group_label.setStyleSheet("color: #5F7470;")
            group_label.setProperty("group_id", group['id'])  # Сохраняем id группы
            group_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            group_label.mousePressEvent = lambda event, gl=group_label: self.on_group_click(gl)  # Обработка клика
            self.groups_list_layout.addWidget(group_label)

        self.setLayout(main_layout)

    def on_group_click(self, group_label):
        """Обработка клика на группу"""
        if self.selected_group_label:
            self.selected_group_label.setStyleSheet("background-color: transparent; color: #5F7470;")  # Сбрасываем стиль предыдущей группы
        self.selected_group_label = group_label
        self.selected_group_label.setStyleSheet("background-color: #00AF8E; color: white;")  # Подсвечиваем выбранную группу

    def on_back_click(self, event):
        self.stacked_widget.setCurrentIndex(0)
        self.close()

    def keyPressEvent(self, event):
        """Удаление группы при нажатии клавиши Delete"""
        if event.key() == Qt.Key.Key_Delete and self.selected_group_label:
            group_id = self.selected_group_label.property("group_id")
            self.delete_group(group_id)
        else:
            super().keyPressEvent(event)  # Передаем событие дальше, если не обработали

    def delete_group(self, group_id):
        """Удаляем группу из базы данных"""
        try:
            cursor, conn = db_cursor()  # Получаем курсор и соединение
            cursor.execute("DELETE FROM Groups WHERE id = %s", (group_id,))
            conn.commit()  # Фиксируем изменения
            self.groups = [group for group in self.groups if group['id'] != group_id]  # Обновляем список групп

            # Закрываем курсор и соединение
            cursor.close()
            conn.close()

            # Обновляем отображение
            self.update_group_list()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении группы:\n{str(e)}")

    def update_group_list(self):
        """Обновляем список групп после удаления"""
        try:
            # Очищаем текущий список
            for i in reversed(range(self.groups_list_layout.count())):
                widget = self.groups_list_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            # Добавляем обновлённый список групп
            for group in self.groups:
                group_label = HoverLabel(f"{group['id']}. {group['name']}, пользователь: {group['user_name']}")
                group_label.setFont(QFont("Inter", 24))
                group_label.setStyleSheet("color: #5F7470;")
                group_label.setProperty("group_id", group['id'])
                group_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                group_label.mousePressEvent = lambda event, gl=group_label: self.on_group_click(gl)  # Обработка клика
                self.groups_list_layout.addWidget(group_label)

            self.groups_list_widget.update()
        except Exception as e:
            print(f"Ошибка при обновлении списка групп: {e}")