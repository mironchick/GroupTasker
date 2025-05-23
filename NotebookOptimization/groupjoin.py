from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from database import check_group_exists, check_user_exists, add_user_to_group, check_user_exists_in_group, verify_user_password
from main_window import MainWindow


class GroupJoinWindow(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Вход в группу")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #F0F0F0;")

        main_layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        back_label = QLabel("Back")
        back_label.setFont(QFont("Inter", 44))
        back_label.setStyleSheet("color: #5F7470;")
        back_label.mousePressEvent = self.on_back_click

        title_label = QLabel("GroupTasker")
        title_label.setFont(QFont("Inter", 44))
        title_label.setStyleSheet("color: #5F7470;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        header_layout.addWidget(back_label)
        header_layout.addStretch()
        header_layout.addWidget(title_label)

        main_layout.addLayout(header_layout)
        main_layout.addSpacing(30)

        def create_input_field(label_text):
            label = QLabel(label_text)
            label.setFont(QFont("Inter", 30))
            label.setStyleSheet("color: #5F7470;")

            input_field = QLineEdit()
            input_field.setFixedSize(770, 60)
            input_field.setStyleSheet(
                "background-color: #D2D4C8; border-radius: 15px; font-size: 22px; padding-left: 10px;"
            )

            field_layout = QVBoxLayout()
            field_layout.addWidget(label)
            field_layout.addWidget(input_field)

            return field_layout, input_field

        field_layout1, self.group_code_input = create_input_field("Код группы")
        field_layout2, self.user_name_input = create_input_field("Ваше имя")
        field_layout3, self.password_input = create_input_field("Пароль")

        main_layout.addLayout(field_layout1)
        main_layout.addSpacing(24)
        main_layout.addLayout(field_layout2)
        main_layout.addSpacing(24)
        main_layout.addLayout(field_layout3)

        btn_join = QPushButton("Присоединиться к группе")
        btn_join.setFont(QFont("Inter", 30))
        btn_join.setFixedSize(500, 60)
        btn_join.setStyleSheet(
            "QPushButton { background-color: #D2D4C8; color: #003C30; border-radius: 15px; font-size: 28px; }"
            "QPushButton:hover { background-color: #C2C4B8; }"
        )
        btn_join.clicked.connect(self.join_group)

        main_layout.addSpacing(30)
        main_layout.addWidget(btn_join, alignment=Qt.AlignmentFlag.AlignCenter)

    def on_back_click(self, event):
        self.stacked_widget.setCurrentIndex(0)
        self.close()

    def join_group(self):
        group_code = self.group_code_input.text().strip()
        user_name = self.user_name_input.text().strip()
        password = self.password_input.text().strip()

        if not group_code or not user_name or not password:
            QMessageBox.warning(self, "Ошибка", "Необходимо заполнить все поля!")
            return

        if not check_group_exists(group_code):
            QMessageBox.warning(self, "Ошибка", "Код группы введён неверно")
            return

        # Проверяем, существует ли пользователь с таким именем в группе
        user_exists = check_user_exists_in_group(user_name, group_code)
        if user_exists:
            # Если пользователь существует, проверяем пароль
            password_correct = verify_user_password(user_name, password, group_code)
            if not password_correct:
                QMessageBox.warning(self, "Ошибка", "Неверный пароль для существующего пользователя")
                return
        else:
            # Если пользователя нет, добавляем его
            add_user_to_group(user_name, password, group_code)

        QMessageBox.information(self, "Успех", "Вы успешно вошли в группу")

        # Открываем главное окно с передачей кода группы
        main_window = MainWindow(self.stacked_widget, user_name, group_code)
        self.stacked_widget.addWidget(main_window)
        self.stacked_widget.setCurrentWidget(main_window)
        self.close()