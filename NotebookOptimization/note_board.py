from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                            QHBoxLayout, QFrame, QInputDialog, QScrollArea, QMessageBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from database import save_note, get_notes, delete_note, get_note_author

class NoteBoard(QFrame):
    def __init__(self, group_code, user_name=None):
        super().__init__()
        self.group_code = group_code
        self.user_name = user_name
        self.setFixedSize(800, 600)  # Уменьшенный размер
        self.setStyleSheet("""
            border: 2px solid #5F7470; 
            background-color: transparent;
            border-radius: 10px;
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Кнопка добавления заметки
        btn_add_note = QPushButton("Добавить заметку")
        btn_add_note.setFont(QFont("Inter", 16))
        btn_add_note.setStyleSheet("""
            QPushButton {
                background-color: #E0E2DB; 
                color: #003C30; 
                border-radius: 8px; 
                padding: 8px;
                height: 40px;
            }
            QPushButton:hover { 
                background-color: #D0D2C8; 
            }
        """)
        btn_add_note.clicked.connect(self.add_note)
        self.main_layout.addWidget(btn_add_note, alignment=Qt.AlignmentFlag.AlignCenter)

        # Область с заметками
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")

        self.notes_container = QWidget()
        self.notes_layout = QVBoxLayout(self.notes_container)
        self.notes_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.notes_layout.setSpacing(8)

        self.scroll_area.setWidget(self.notes_container)
        self.main_layout.addWidget(self.scroll_area)

        self.load_notes()

    def load_notes(self):
        for i in reversed(range(self.notes_layout.count())):
            widget = self.notes_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        notes = get_notes(self.group_code)
        for note_id, text, user_name in notes:
            self.add_note_to_board(note_id, text, user_name)

    def add_note_to_board(self, note_id, text, user_name):
        note_frame = QFrame()
        note_frame.setStyleSheet("""
            background-color: #E0E2DB;
            border-radius: 8px;
            padding: 10px;
        """)
        note_frame.setFixedWidth(750)

        note_layout = QVBoxLayout(note_frame)

        # Текст заметки
        note_text = QLabel(text)
        note_text.setFont(QFont("Inter", 14))
        note_text.setStyleSheet("color: #003C30;")
        note_text.setWordWrap(True)

        # Автор заметки
        user_label = QLabel(f"Автор: {user_name}")
        user_label.setFont(QFont("Inter", 10))
        user_label.setStyleSheet("color: #5F7470; font-style: italic;")
        user_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Кнопка удаления (только для своих заметок)
        if self.user_name == user_name:
            btn_delete = QPushButton("Удалить")
            btn_delete.setFixedSize(80, 30)
            btn_delete.setStyleSheet("""
                QPushButton {
                    background-color: #FF6961;
                    color: white;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #D9534F;
                }
            """)
            btn_delete.clicked.connect(lambda: self.remove_note(note_id))

        note_layout.addWidget(note_text)
        if self.user_name == user_name:
            note_layout.addWidget(btn_delete)
        note_layout.addWidget(user_label)

        self.notes_layout.addWidget(note_frame)

    def add_note(self):
        if not self.user_name:
            return

        dialog = QInputDialog(self)
        dialog.setWindowTitle("Новая заметка")
        dialog.setLabelText("Введите текст заметки:")
        dialog.setStyleSheet("""
            QInputDialog {
                background-color: #E0E2DB;
            }
            QLabel {
                color: #003C30;
                font-size: 16px;
            }
            QTextEdit {
                background-color: white;
                color: #003C30;
                font-size: 14px;
                border: 1px solid #5F7470;
                border-radius: 5px;
            }
        """)
        dialog.setInputMode(QInputDialog.InputMode.TextInput)
        dialog.setOption(QInputDialog.InputDialogOption.UsePlainTextEditForTextInput)

        if dialog.exec() == QInputDialog.DialogCode.Accepted:
            text = dialog.textValue()
            if text.strip():
                note_id = save_note(self.group_code, text, self.user_name)
                self.add_note_to_board(note_id, text, self.user_name)

    def remove_note(self, note_id):
        author = get_note_author(note_id)
        if author == self.user_name:
            delete_note(note_id)
            self.load_notes()
        else:
            QMessageBox.warning(self, "Ошибка", "Вы можете удалять только свои заметки!")