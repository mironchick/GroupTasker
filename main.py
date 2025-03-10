from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QStackedWidget
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from groupcreate import GroupCreateWindow
from groupjoin import GroupJoinWindow
from groupslist import GroupsListWindow  # Импортируем новое окно для списка групп

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
        self.main_layout.setSpacing(40)

        title = QLabel("GroupTasker")
        title.setFont(QFont("Inter", 64))
        title.setStyleSheet("color: #5F7470;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(title)

        button_style = (
            "QPushButton {"
            "background-color: #D2D4C8;"
            "border-radius: 15px;"
            "font-size: 32px; font-weight: normal;"
            "color: #003C30;"
            "width: 500px;"
            "height: 100px;"
            "}"
            "QPushButton:hover { background-color: #C2C4B8; }"
        )

        btn_create = QPushButton("Создать группу")
        btn_create.setFont(QFont("Inter", 32))
        btn_create.setStyleSheet(button_style)
        btn_create.clicked.connect(self.create_group_window)
        self.main_layout.addWidget(btn_create)

        btn_join = QPushButton("Войти в группу (код группы)")
        btn_join.setFont(QFont("Inter", 32))
        btn_join.setStyleSheet(button_style)
        btn_join.clicked.connect(self.join_group_window)
        self.main_layout.addWidget(btn_join)

        btn_my_groups = QPushButton("Мои группы")
        btn_my_groups.setFont(QFont("Inter", 32))
        btn_my_groups.setStyleSheet(button_style)
        btn_my_groups.clicked.connect(self.my_groups_window)  # Открытие окна с группами
        self.main_layout.addWidget(btn_my_groups)

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

    def my_groups_window(self):
        """Открывает окно с группами пользователя."""
        groups_list_window = GroupsListWindow(self.stacked_widget)
        self.stacked_widget.addWidget(groups_list_window)
        self.stacked_widget.setCurrentWidget(groups_list_window)
if __name__ == "__main__":
    app = QApplication([])
    window = GroupTaskerApp()
    window.show()
    app.exec()
