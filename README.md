Запросы для настройки базы данных в PostgreSQL:
```sql
CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    group_id INTEGER REFERENCES groups(id) ON DELETE CASCADE,
    UNIQUE(name, group_id)
);

CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES groups(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES groups(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    deadline TIMESTAMP,
    user_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE group_messages (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES groups(id) ON DELETE CASCADE,
    user_name VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE private_messages (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES groups(id) ON DELETE CASCADE,
    sender VARCHAR(255) NOT NULL,
    receiver VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```


```
from PyQt6.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QHBoxLayout, QMessageBox, QApplication)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import random
from database import create_group
from main_window import MainWindow


class GroupCreateWindow(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Создание группы")
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

        field_layout1, self.group_name_input = create_input_field("Название группы")
        field_layout2, self.user_name_input = create_input_field("Ваше имя")
        field_layout3, self.password_input = create_input_field("Пароль")

        main_layout.addLayout(field_layout1)
        main_layout.addSpacing(24)
        main_layout.addLayout(field_layout2)
        main_layout.addSpacing(24)
        main_layout.addLayout(field_layout3)

        btn_create = QPushButton("Создать группу")
        btn_create.setFont(QFont("Inter", 30))
        btn_create.setFixedSize(500, 60)
        btn_create.setStyleSheet(
            "QPushButton { background-color: #D2D4C8; color: #003C30; border-radius: 15px; font-size: 28px; }"
            "QPushButton:hover { background-color: #C2C4B8; }"
        )
        btn_create.clicked.connect(self.create_group)

        main_layout.addSpacing(30)
        main_layout.addWidget(btn_create, alignment=Qt.AlignmentFlag.AlignCenter)

    def on_back_click(self, event):
        self.stacked_widget.setCurrentIndex(0)
        self.close()

    def create_group(self):
        group_name = self.group_name_input.text().strip()
        user_name = self.user_name_input.text().strip()
        password = self.password_input.text().strip()

        if not group_name or not user_name or not password:
            QMessageBox.warning(self, "Ошибка", "Необходимо заполнить все поля!")
            return

        group_code = str(random.randint(100000, 999999))

        try:
            group_id = create_group(group_name, group_code, user_name, password)

            if group_id:
                # Используем буфер обмена Qt вместо pyperclip
                clipboard = QApplication.clipboard()
                clipboard.setText(group_code)

                QMessageBox.information(
                    self,
                    "Группа создана",
                    f"Код группы: {group_code} (скопирован в буфер обмена)"
                )

                # Открываем главное окно с передачей кода группы
                main_window = MainWindow(self.stacked_widget, user_name, group_code)
                self.stacked_widget.addWidget(main_window)
                self.stacked_widget.setCurrentWidget(main_window)

            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось создать группу. Попробуйте снова.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при создании группы:\n{str(e)}")
```
