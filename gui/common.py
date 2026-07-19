from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QWidget, QDialog, QSpinBox, QMenu, QHBoxLayout
from PySide6.QtCore import Qt
import sys
from pathlib import Path

def getLogo():
    if getattr(sys, 'frozen', False): base_path = Path(sys._MEIPASS)
    else: base_path = Path(__file__).parent
    return str(base_path / 'data/Logo.png')

class contextWidget(QWidget):
    def __init__(self,movable=False):
        super().__init__()
        self.layout=QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self.movable=movable
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
    def showContextMenu(self,pos):
        context_menu=QMenu(self)
        actionEdit=QAction("Edit",self)
        actionEdit.triggered.connect(self.edit)
        context_menu.addAction(actionEdit)
        actionDelete=QAction("Delete",self)
        actionDelete.triggered.connect(self.delete)
        context_menu.addAction(actionDelete)
        if self.movable:
            actionMoveUp=QAction("Move Up",self)
            actionMoveUp.triggered.connect(self.moveUp)
            context_menu.addAction(actionMoveUp)
            actionMoveDown=QAction("Move Down",self)
            actionMoveDown.triggered.connect(self.moveDown)
            context_menu.addAction(actionMoveDown)
        context_menu.exec(self.mapToGlobal(pos))
    def delete(self):
        pass
    def edit(self):
        pass
    def moveUp(self):
        self.move(up=True)
    def moveDown(self):
        self.move(up=False)
    def move(self,item,itemlist,layout,up=True):
        idx=itemlist.index(item)
        if up:
            if idx==0: return
            else: newidx=idx-1
        else:
            if idx==len(itemlist): return
            else: newidx=idx+1
        itemlist.insert(newidx,itemlist.pop(idx))
        clearStretches(layout)
        for _ in range(len(itemlist)): _=layout.takeAt(1) #clear the layout except the label on top
        for itemi in itemlist: layout.addWidget(itemi.gui)

def clearStretches(layout):
    for idx in reversed(range(layout.count())):
        item=layout.itemAt(idx)
        if item.spacerItem() is not None: layout.takeAt(idx)

class NoWheelSpinBox(QSpinBox):
    def wheelEvent(self, event): event.ignore()

class QDialog5e(QDialog):
    def __init__(self):
        super().__init__()
        icon=QIcon(getLogo())
        self.setWindowIcon(icon)

class QMainWindow5e(QMainWindow):
    def __init__(self):
        super().__init__()
        icon=QIcon(getLogo())
        self.setWindowIcon(icon)

class PopupDialog(QDialog5e):
    def __init__(self,title,text):
        super().__init__()
        self.setWindowTitle(title)
        layout=QVBoxLayout(self)
        label=QLabel(text,alignment=Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)