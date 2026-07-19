from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QMessageBox, QDialog, QTextEdit, QFormLayout, QLineEdit, QDialogButtonBox
from gui.common import contextWidget, NoWheelSpinBox, PopupDialog, QDialog5e

class item():
    def __init__(self,bpline,c):
        self.c=c
        self.quantity=0
        self.name=''
        self.text=''
        self.description=''
        self.load(bpline)
    def load(self,bpline):
        self.quantity=int(bpline.split(':')[1])
        self.name=bpline.split(':')[0].strip()
        if len(bpline.split(':'))>2: 
            self.text=':'.join(bpline.split(':')[2:]).strip().replace('\n','\\')
            self.description=self.text.replace('\\','\n').strip()
            if len(self.description)==0: self.description='(No Description)'
        else: self.description='(No Description)'
    def show(self):
        self.gui=itemWidget(self)
    def delete(self):
        self.c.backpacklist.remove(self)
    def save(self):
        return f"{self.name}:{self.quantity}:{self.text}\n"
    
class itemWidget(contextWidget):
    def __init__(self,item):
        super().__init__(movable=True)
        self.item=item
        self.quantity=NoWheelSpinBox(minimum=-2147483648,maximum=2147483647,value=self.item.quantity)
        self.quantity.valueChanged.connect(self.changeValue)
        self.quantity.setFixedWidth(self.quantity.sizeHint().height()*5)
        self.layout.addWidget(self.quantity)
        self.button=QPushButton(self.item.name,clicked=self.showinfo)
        self.layout.addWidget(self.button)
        self.item.c.gui.bpPage.itemLayout.insertWidget(self.item.c.gui.bpPage.itemLayout.count()-1,self)
    def changeValue(self,value):
        self.item.quantity=value
    def showinfo(self):
        self.dialog=PopupDialog(self.item.name,self.item.description.replace('\\','\n'))
        self.dialog.show()
    def edit(self):
        dialog=getItem(self.item)
        if dialog.exec()==QDialog.Accepted:
            newstring=dialog.getData()
            self.item.load(newstring)
            self.quantity.setValue(self.item.quantity)
            self.button.setText(self.item.name)
    def delete(self):
        self.item.c.gui.bpPage.itemLayout.removeWidget(self)
        self.setParent(None)
        self.deleteLater()
        self.item.delete()
    def moveUp(self):
        self.move(self.item,self.item.c.backpacklist,self.item.c.gui.bpPage.itemLayout,up=True)
        self.item.c.gui.bpPage.itemLayout.addStretch()
        self.item.c.update()
    def moveDown(self):
        self.move(self.item,self.item.c.backpacklist,self.item.c.gui.bpPage.itemLayout,up=False)
        self.item.c.gui.bpPage.itemLayout.addStretch()
        self.item.c.update()

class getItem(QDialog5e):
    def __init__(self,oldItem=None):
        super().__init__()
        self.setWindowTitle('New Item')
        mainLayout=QVBoxLayout()
        self.setLayout(mainLayout)
        formLayout=QFormLayout()
        self.name=QLineEdit()
        self.number=NoWheelSpinBox(minimum=-2147483648,maximum=2147483647,value=0)
        self.text=QTextEdit()
        formLayout.addRow('Name:',self.name)
        formLayout.addRow('Quantity:',self.number)
        formLayout.addRow('Description:',self.text)
        mainLayout.addLayout(formLayout)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.verifyData)
        buttons.rejected.connect(self.reject)
        mainLayout.addWidget(buttons)
        if oldItem is not None:
            self.name.setText(oldItem.name)
            self.number.setValue(oldItem.quantity)
            self.text.setText(oldItem.description)
    def verifyData(self):
        if len(self.name.text())<1: 
            QMessageBox.warning(self,'Invalid Name','No name provided.')
            return 
        if ':' in self.name.text(): 
            QMessageBox.warning(self,'Invalid Name','Name cannot contain ":".')
            return 
        self.accept()
    def getData(self):
        return f"{self.name.text()}:{self.number.value()}:{self.text.toPlainText().strip().replace('\n','\\')}"