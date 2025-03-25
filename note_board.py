from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QInputDialog
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class NoteBoard(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1000, 900)
        self.setStyleSheet("border: 2px solid #5F7470; background-color: transparent;")

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        btn_add_note = QPushButton("Добавить заметку")
        btn_add_note.setFont(QFont("Inter", 24))
        btn_add_note.setStyleSheet(
            "QPushButton { background-color: #E0E2DB; color: #003C30; border-radius: 10px; padding: 10px; }"
            "QPushButton:hover { background-color: #D0D2C8; }"
        )
        btn_add_note.clicked.connect(self.add_note)

        self.layout.addWidget(btn_add_note, alignment=Qt.AlignmentFlag.AlignCenter)

    def add_note(self):
        """Добавляет заметку на доску."""
        text, ok = QInputDialog.getText(self, "Новая заметка", "Введите текст заметки:")
        if ok and text:
            note = QLabel(text)
            note.setFixedSize(200, 150)
            note.setFont(QFont("Inter", 24))
            note.setStyleSheet("background-color: #E0E2DB; color: #003C30; border-radius: 10px; padding: 10px;")
            note.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.layout.addWidget(note, alignment=Qt.AlignmentFlag.AlignTop)
