from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QStackedWidget, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from groupcreate import GroupCreateWindow
from groupjoin import GroupJoinWindow


class GroupTaskerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("GroupTasker")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #F0F0F0;")

        self.stacked_widget = QStackedWidget(self)

        # Главная страница
        self.main_page = QWidget()
        self.main_layout = QVBoxLayout(self.main_page)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("GroupTasker")
        title.setFont(QFont("Inter", 64))
        title.setStyleSheet("color: #5F7470;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Добавляем небольшое пространство сверху
        self.main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.main_layout.addWidget(title)

        button_style = (
            "QPushButton {"
            "background-color: #D2D4C8;"
            "border-radius: 15px;"
            "font-size: 32px; font-weight: normal;"
            "color: #003C30;"
            "width: 500px;"
            "height: 175px;"
            "}"
            "QPushButton:hover { background-color: #C2C4B8; }"
        )

        btn_create = QPushButton("Создать группу")
        btn_create.setFont(QFont("Inter", 32))
        btn_create.setStyleSheet(button_style)
        btn_create.setFixedSize(500, 175)
        btn_create.clicked.connect(self.create_group_window)

        btn_join = QPushButton("Войти в группу (код группы)")
        btn_join.setFont(QFont("Inter", 32))
        btn_join.setStyleSheet(button_style)
        btn_join.setFixedSize(500, 175)
        btn_join.clicked.connect(self.join_group_window)

        # Немного уменьшаем расстояние между заголовком и кнопками
        self.main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        self.main_layout.addWidget(btn_create, alignment=Qt.AlignmentFlag.AlignCenter)

        # Оставляем увеличенный отступ между кнопками
        self.main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        self.main_layout.addWidget(btn_join, alignment=Qt.AlignmentFlag.AlignCenter)

        # Добавляем пространство снизу
        self.main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.stacked_widget.addWidget(self.main_page)

        # Устанавливаем основной layout для окна
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.stacked_widget)

    def create_group_window(self):
        """Открывает окно создания группы."""
        group_create_window = GroupCreateWindow(self.stacked_widget)
        self.stacked_widget.addWidget(group_create_window)
        self.stacked_widget.setCurrentWidget(group_create_window)

    def join_group_window(self):
        """Открывает окно входа в группу."""
        group_join_window = GroupJoinWindow(self.stacked_widget)
        self.stacked_widget.addWidget(group_join_window)
        self.stacked_widget.setCurrentWidget(group_join_window)


if __name__ == "__main__":
    app = QApplication([])
    window = GroupTaskerApp()
    window.show()
    app.exec()