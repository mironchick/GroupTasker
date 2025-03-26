from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QFrame, QInputDialog, QScrollArea)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from database import save_note, get_notes


class NoteBoard(QFrame):
    def __init__(self, group_code):
        super().__init__()
        self.group_code = group_code
        self.setFixedSize(1000, 900)
        self.setStyleSheet("""
            border: 2px solid #5F7470; 
            background-color: transparent;
            border-radius: 15px;
        """)

        # Основной layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Кнопка добавления заметки
        btn_add_note = QPushButton("Добавить заметку")
        btn_add_note.setFont(QFont("Inter", 24))
        btn_add_note.setStyleSheet("""
            QPushButton {
                background-color: #E0E2DB; 
                color: #003C30; 
                border-radius: 10px; 
                padding: 10px;
            }
            QPushButton:hover { 
                background-color: #D0D2C8; 
            }
        """)
        btn_add_note.clicked.connect(self.add_note)
        self.main_layout.addWidget(btn_add_note, alignment=Qt.AlignmentFlag.AlignCenter)

        # Область с заметками с прокруткой
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")

        self.notes_container = QWidget()
        self.notes_layout = QVBoxLayout(self.notes_container)
        self.notes_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.notes_layout.setSpacing(10)

        self.scroll_area.setWidget(self.notes_container)
        self.main_layout.addWidget(self.scroll_area)

        # Загружаем существующие заметки
        self.load_notes()

    def load_notes(self):
        """Загружает заметки из базы данных."""
        notes = get_notes(self.group_code)
        for text in notes:
            self.add_note_to_board(text)

    def add_note_to_board(self, text):
        """Добавляет заметку на доску (без сохранения в БД)."""
        note_frame = QFrame()
        note_frame.setStyleSheet("""
            background-color: #E0E2DB;
            border-radius: 10px;
            padding: 10px;
        """)
        note_frame.setFixedWidth(950)

        note_layout = QVBoxLayout(note_frame)

        note_text = QLabel(text)
        note_text.setFont(QFont("Inter", 20))
        note_text.setStyleSheet("color: #003C30;")
        note_text.setWordWrap(True)
        note_text.setAlignment(Qt.AlignmentFlag.AlignLeft)

        note_layout.addWidget(note_text)
        self.notes_layout.addWidget(note_frame)

    def add_note(self):
        """Добавляет заметку на доску и сохраняет в базу данных."""
        text, ok = QInputDialog.getMultiLineText(
            self,
            "Новая заметка",
            "Введите текст заметки:",
            ""
        )

        if ok and text.strip():
            # Сохраняем в базу данных
            save_note(self.group_code, text)
            # Добавляем на доску
            self.add_note_to_board(text)