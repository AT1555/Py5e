from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit

class notesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.notesLayout=QVBoxLayout()
        self.setLayout(self.notesLayout)
        self.notes=QTextEdit()
        self.notesLayout.addWidget(self.notes)