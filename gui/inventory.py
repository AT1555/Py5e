from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel
from PySide6.QtCore import Qt

class inventoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.bpLayout=QVBoxLayout()
        self.setLayout(self.bpLayout)
        self.bpBody=QWidget()
        self.bpScroll=QScrollArea()
        self.bpScroll.setWidget(self.bpBody)
        self.bpScroll.setWidgetResizable(True)
        self.bpScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.bpScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.bpLayout.addWidget(self.bpScroll)
        self.itemLayout=QVBoxLayout()
        self.bpBody.setLayout(self.itemLayout)
        self.itemLayout.addWidget(QLabel('Inventory',alignment=Qt.AlignmentFlag.AlignCenter))
        self.itemLayout.addStretch()