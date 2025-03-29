from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QFrame, QInputDialog, QScrollArea)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from database import save_note, get_notes, delete_note


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
        # Очищаем существующие заметки перед загрузкой новых
        for i in reversed(range(self.notes_layout.count())):
            widget = self.notes_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        notes = get_notes(self.group_code)
        for note_id, text, user_name in notes:
            self.add_note_to_board(note_id, text, user_name)

    def add_note_to_board(self, note_id, text, user_name):
        """Добавляет заметку на доску."""
        note_frame = QFrame()
        note_frame.setStyleSheet("""
            background-color: #E0E2DB;
            border-radius: 10px;
            padding: 10px;
        """)
        note_frame.setFixedWidth(950)

        note_layout = QVBoxLayout(note_frame)  # Изменено на вертикальный layout

        # Основной текст заметки
        note_text = QLabel(text)
        note_text.setFont(QFont("Inter", 20))
        note_text.setStyleSheet("color: #003C30;")
        note_text.setWordWrap(True)
        note_text.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Имя пользователя (мелким текстом)
        user_label = QLabel(f"Автор: {user_name}")
        user_label.setFont(QFont("Inter", 12))
        user_label.setStyleSheet("color: #5F7470; font-style: italic;")
        user_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Горизонтальный layout для текста и кнопки удаления
        text_button_layout = QHBoxLayout()
        text_button_layout.addWidget(note_text)

        btn_delete = QPushButton("❌")
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #FF6961;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #D9534F;
            }
        """)
        btn_delete.setFixedSize(40, 40)
        btn_delete.clicked.connect(lambda: self.remove_note(note_id))

        text_button_layout.addWidget(btn_delete)

        note_layout.addLayout(text_button_layout)
        note_layout.addWidget(user_label)
        self.notes_layout.addWidget(note_frame)

    def add_note(self):
        """Добавляет заметку на доску и сохраняет в базу данных."""
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Новая заметка")
        dialog.setLabelText("Введите текст заметки:")
        dialog.setStyleSheet("""
            QInputDialog {
                background-color: #E0E2DB;
            }
            QLabel {
                color: #003C30;
                font-size: 20px;
            }
            QTextEdit {
                background-color: white;
                color: #003C30;
                font-size: 18px;
                border: 1px solid #5F7470;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #5F7470;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #4D615E;
            }
        """)
        dialog.setInputMode(QInputDialog.InputMode.TextInput)
        dialog.setOption(QInputDialog.InputDialogOption.UsePlainTextEditForTextInput)

        if dialog.exec() == QInputDialog.DialogCode.Accepted:
            text = dialog.textValue()
            if text.strip():
                # Сохраняем в базу данных и получаем ID заметки
                note_id = save_note(self.group_code, text,
                                    self.parent().user_name)  # Получаем имя пользователя из родительского окна
                # Добавляем на доску
                self.add_note_to_board(note_id, text, self.parent().user_name)

    def remove_note(self, note_id):
        """Удаляет заметку из базы данных и обновляет доску."""
        delete_note(note_id)
        self.load_notes()