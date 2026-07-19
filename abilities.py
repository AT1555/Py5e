from PySide6.QtWidgets import QVBoxLayout, QPushButton, QMessageBox, QDialog, QTextEdit, QFormLayout, QLineEdit, QDialogButtonBox, QComboBox, QCheckBox
from gui.common import contextWidget, PopupDialog, QDialog5e
from utilities import statmod

class ability():
    def __init__(self,abilitydict,c):
        self.c=c
        self.name='(N/A)'
        self.maxnum=0
        self.maxnumraw=0
        self.numleft=0
        self.resttype=''
        self.spellslot=False
        self.description='(No Description)'
        self.text=''
        self.load(abilitydict)
    def load(self,abilitydict):
        if 'NAME' in abilitydict: self.name=abilitydict['NAME']
        if 'MAX' in abilitydict:
            self.maxnumraw=abilitydict['MAX']
            try: self.maxnum=int(abilitydict['MAX'])
            except ValueError: self.maxnum=max(1,self.c.cstats[abilitydict['MAX']+'bonus']) if abilitydict['MAX'] in [i[0] for i in self.c.allskills] else (max(1,statmod(self.c.cstats[abilitydict['MAX']])) if abilitydict['MAX'] in ['STR','DEX','CON','INT','WIS','CHA'] else (self.c.cstats[abilitydict['MAX']] if abilitydict['MAX']=='PRO' else 0))
        if 'REMAINING' in abilitydict: self.numleft=int(abilitydict['REMAINING'])
        if 'REST' in abilitydict: 
            self.resttype=abilitydict['REST']
            if self.resttype.lower()=='none': self.resttype='' #remove legacy 'none' value
        if 'SPELLSLOT' in abilitydict: 
            if 'y' in abilitydict['SPELLSLOT'].lower(): self.spellslot=True
        if 'TEXT' in abilitydict: 
            self.text=abilitydict['TEXT'].replace('\n','\\')
            self.description=abilitydict['TEXT'].replace('\\','\n')
    def update(self):
        try: self.maxnum=int(self.maxnumraw)
        except ValueError: self.maxnum=max(1,self.c.cstats[self.maxnumraw+'bonus']) if self.maxnumraw in [i[0] for i in self.c.allskills] else (max(1,statmod(self.c.cstats[self.maxnumraw])) if self.maxnumraw in ['STR','DEX','CON','INT','WIS','CHA'] else (self.c.cstats[self.maxnumraw] if self.maxnumraw=='PRO' else 0))
        if self.maxnum>0: 
            if self.spellslot: self.spellgui.useButton.setText(f"{self.numleft}/{self.maxnum}: {self.name}")
            self.gui.infoButton.setText(f"{self.numleft}/{self.maxnum}: {self.name}")
        else: 
            if self.spellslot: self.spellgui.useButton.setText(f"{self.numleft}: {self.name}")
            self.gui.infoButton.setText(f"{self.numleft}: {self.name}")
        if self.numleft==0: 
            if self.spellslot: self.spellgui.useButton.setEnabled(False)
            self.gui.useButton.setEnabled(False)
        else: 
            if self.spellslot: self.spellgui.useButton.setEnabled(True)
            self.gui.useButton.setEnabled(True)
        self.c.update()
    def use(self):
        if self.numleft>0: self.numleft-=1
        self.update()
    def unuse(self):
        self.numleft+=1
        self.update()
    def rest(self,resttype):
        if resttype==self.resttype.upper(): self.numleft=self.maxnum
        self.update()
    def show(self):
        self.gui=abilityWidget(self)
        if self.spellslot: self.spellgui=abilityWidget(self,spellslot=True)
        self.update()
    def delete(self):
        if self.spellslot: self.spellgui.selfdelete()
        self.gui.selfdelete()
        self.c.abilitylist.remove(self)
    def save(self):
        return f"%ABILITY\nNAME={self.name}\nMAX={self.maxnum}\nREMAINING={self.numleft}\nREST={self.resttype}\nSPELLSLOT={'YES' if self.spellslot else 'NO'}\nTEXT={self.text}\n\n"

class abilityWidget(contextWidget):
    def __init__(self,ability,spellslot=False):
        super().__init__(movable=not spellslot)
        self.ability=ability
        self.unuseButton=QPushButton(text='+',clicked=self.ability.unuse)
        self.unuseButton.setFixedWidth(self.unuseButton.sizeHint().height())
        self.layout.addWidget(self.unuseButton)
        if spellslot: 
            # self.useButton.setFlat(True)
            # self.uesButton.setStyleSheet("border: none;")# background: none;")
            self.useButton=QPushButton(text='?',clicked=self.ability.use)
            self.layout.addWidget(self.useButton)
            self.guiLocation=self.ability.c.gui.spellsPage.spellLVLLayouts[ability.name[0]]
            self.guiLocation.insertWidget(0,self)
        else: 
            self.useButton=QPushButton(text='-',clicked=self.ability.use)
            self.useButton.setFixedWidth(self.unuseButton.sizeHint().height())
            self.infoButton=QPushButton(text='?',clicked=self.showinfo)
            self.layout.addWidget(self.useButton)
            self.layout.addWidget(self.infoButton)
            self.guiLocation=self.ability.c.gui.mainPage.cAbilityLayout
            self.guiLocation.insertWidget(self.guiLocation.count()-1,self)
    def delete(self): #necessary to override contextWidget
        self.ability.delete()
    def edit(self):
        dialog=getAbility(self.ability.c,self.ability)
        if dialog.exec()==QDialog.Accepted:
            newDict=dialog.getData()
            self.ability.load(newDict)
            self.ability.update()
    def moveUp(self):
        self.move(self.ability,self.ability.c.abilitylist,self.guiLocation,up=True)
        self.ability.c.update()
    def moveDown(self):
        self.move(self.ability,self.ability.c.abilitylist,self.guiLocation,up=False)
        self.ability.c.update()
    def showinfo(self):
        self.dialog=PopupDialog(self.ability.name,self.ability.description.replace('\\','\n'))
        self.dialog.show()
    def selfdelete(self):
        self.guiLocation.removeWidget(self)
        self.setParent(None)
        self.deleteLater()

class getAbility(QDialog5e):
    def __init__(self,c,oldAbility=None):
        super().__init__()
        self.c=c
        self.setWindowTitle('New Ability')
        mainLayout=QVBoxLayout()
        self.setLayout(mainLayout)
        formLayout=QFormLayout()
        self.name=QLineEdit()
        self.maxuse=QLineEdit()
        self.resttype=QComboBox()
        self.resttype.addItem('','')
        self.resttype.addItem('Short Rest','SR')
        self.resttype.addItem('Long Rest','LR')
        self.resttype.addItem('Day','Day')
        self.description=QTextEdit()
        self.spellslot=QCheckBox()
        formLayout.addRow('Name:',self.name)
        formLayout.addRow('Maximum Uses (optional, enter an integer or a skill/ability score name)',self.maxuse)
        formLayout.addRow('Resets on:',self.resttype)
        if oldAbility is None: formLayout.addRow('Spellslot?',self.spellslot) #hide the spellslot toggle when editing to avoid GUI Character/Spells page desync
        formLayout.addRow('Description:',self.description)
        mainLayout.addLayout(formLayout)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.verifyData)
        buttons.rejected.connect(self.reject)
        mainLayout.addWidget(buttons)
        if oldAbility is not None:
            self.name.setText(oldAbility.name)
            self.maxuse.setText(oldAbility.maxnumraw)
            self.resttype.setCurrentIndex(self.resttype.findData(oldAbility.resttype))
            self.description.setText(oldAbility.description)
            if oldAbility.spellslot: self.spellslot.setChecked(True)
    def verifyData(self):
        if len(self.name.text())<1: 
            QMessageBox.warning(self,'Invalid Name','No name provided.')
            return 
        if self.spellslot.isChecked() and self.name.text()[0] not in [str(i) for i in range(10)]:
            QMessageBox.warning(self,'Invalid Name','The first character of a Spell Slot name must start with [0-9] to assign an appropriate level.')
            return
        if len(self.maxuse.text().strip())>0:
            try: maxnum=int(self.maxuse.text().strip())
            except ValueError: 
                if self.maxuse.text().strip() not in [i[0] for i in self.c.allskills]+['PRO','STR','DEX','CON','INT','WIS','CHA']: 
                    QMessageBox.warning(self,'Invalid Maximum Uses','Invalid Maximum Uses. Valid inputs are: an integer, '+', '.join([i[0] for i in self.c.allskills]+['PRO','STR','DEX','CON','INT','WIS','CHA'])) 
                    return 
        self.accept()
    def getData(self):
        return {'NAME':self.name.text().strip(),'MAX':self.maxuse.text().strip(),'REST':self.resttype.currentData(),'SPELLSLOT':'y' if self.spellslot.isChecked() else 'n','TEXT':self.description.toPlainText().strip()}
    
