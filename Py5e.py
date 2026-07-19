from PySide6.QtWidgets import QApplication, QVBoxLayout, QLabel, QPushButton, QWidget
from glob import glob

from character import character
from spells import load_spells
from gui.common import QMainWindow5e
from update import updatecheck
from utilities import rgb2hex

VERSION='2026_07_18'

class CharacterSelectWindow(QMainWindow5e):
    def __init__(self,updatestatus):
        super().__init__()
        masterspellsdict=load_spells()
        self.setWindowTitle("Py5e")
        font=QApplication.font()
        font.setPointSize(10)
        QApplication.setFont(font)
        layout=QVBoxLayout()
        layout.addWidget(QLabel(f'Select a Character'))
        layout.addWidget(QPushButton(text='New Character',clicked=lambda _, file='NEW_CHARACTER': self.pickchar(infile=file)))
        FiveEfiles=glob('*.5e')
        if len(FiveEfiles)>0:
            for file in FiveEfiles:
                bkgcolor=[236,230,220]
                fontcolor=[0,0,0]
                for encoding in ['utf-8','cp1252']:
                    try:
                        with open(file,'r',encoding=encoding) as openfile:
                            for line in openfile:
                                if line.startswith('COLOR'): bkgcolor=[int(i) for i in line.strip().split('=')[1].split(',')]
                                elif line.startswith('FONTCOLOR'): fontcolor=[int(i) for i in line.strip().split('=')[1].split(',')]
                    except UnicodeDecodeError: pass
                charbutton=QPushButton(text=file.split('/')[-1],clicked=lambda _, file=file: self.pickchar(infile=file))
                charbutton.setStyleSheet(f"background-color: {rgb2hex(bkgcolor)}; color: {rgb2hex(fontcolor)}")
                layout.addWidget(charbutton)
        layout.addWidget(QLabel(updatestatus+f"\n{len(masterspellsdict)} spells loaded."))
        widget=QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    def pickchar(self,*,infile):
        global filename
        filename=infile
        self.close()

def CharacterSelect(updatestatus):
    app=QApplication()
    window=CharacterSelectWindow(updatestatus)
    window.show()
    app.exec()
    app.shutdown()
    return

if __name__=="__main__":
    color1=[236,230,220]
    fcolor1=[0,0,0]
    updatestatus=updatecheck(VERSION)
    filename=None
    CharacterSelect(updatestatus)
    if filename is None: exit()
    else:
        app=QApplication()
        c=character(VERSION)
        if filename=='NEW_CHARACTER': 
            c.show()
            c.gui.editCharacter()
        else: c.load(filename)
        app.exec()    