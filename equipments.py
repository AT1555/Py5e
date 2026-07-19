from PySide6.QtWidgets import QVBoxLayout, QPushButton, QMessageBox, QDialog, QTextEdit, QFormLayout, QLineEdit, QDialogButtonBox, QComboBox, QCheckBox
from gui.common import contextWidget, PopupDialog, QDialog5e, NoWheelSpinBox
from utilities import statmod

class equipment():
    def __init__(self,equipdict,c):
        self.c=c
        self.mods=[]
        self.hitdamage=[0,0]
        self.scaling='no' 
        self.equipped=False
        self.prof=False
        self.maxdex=None
        self.description='(No Description)'
        self.text=''
        self.gui=None
        self.load(equipdict)
        self.update()
    def load(self,equipdict):
        if 'NAME' in equipdict: self.name=equipdict['NAME']
        else: self.name='?'
        if 'MODS' in equipdict: 
            self.mods=equipdict['MODS']
            self.mods=[mod.strip().split(':') for mod in self.mods.split(',')]
            for mod in self.mods: mod[1]=int(mod[1])
        if 'HITDAMAGE' in equipdict: self.hitdamage=[int(equipdict['HITDAMAGE'].split()[0]),equipdict['HITDAMAGE'].split()[1]]
        if 'SCALING' in equipdict: self.scaling=equipdict['SCALING']
        if 'EQUIPPED' in equipdict: 
            if equipdict['EQUIPPED'].strip().lower() in 'yes': self.equipped=True
            elif equipdict['EQUIPPED'].strip().lower() in 'no': self.equipped=False
        if 'PROF' in equipdict: 
            if equipdict['PROF'].strip().lower() in 'yes': self.prof=True
        if 'MAXDEX' in equipdict: self.maxdex=int(equipdict['MAXDEX'])
        if 'TEXT' in equipdict: 
            self.text=equipdict['TEXT'].replace('\n','\\')
            self.description=equipdict['TEXT'].replace('\\','\n')
        if self.equipped: self.enable()
    def update(self,upc=False,upe=False): #need to update again after character update if ability scores change for calculating to hit and damage, prevent infinite recursion with upc and upe
        tempstring=f"{self.name}"
        for mod in self.mods:
            if mod[1]!=0: tempstring+=f", {mod[1]:+d} {mod[0]}"
        if str(self.hitdamage[1])!='0':
            if self.prof:
                if self.scaling.lower() not in 'no': tempstring+=f", To Hit:{self.hitdamage[0]+statmod(self.c.cstats[self.scaling])+self.c.cstats['PRO']:+d}, {self.hitdamage[1]}{statmod(self.c.cstats[self.scaling]):+d}"
                else: tempstring+=f", To Hit:{self.hitdamage[0]+self.c.cstats['PRO']:+d}, {self.hitdamage[1]}"
            else: 
                if self.scaling.lower() not in 'no': tempstring+=f", To Hit:{self.hitdamage[0]+statmod(self.c.cstats[self.scaling]):+d}, {self.hitdamage[1]}{statmod(self.c.cstats[self.scaling]):+d}"
                else: tempstring+=f", To Hit:{self.hitdamage[0]:+d}, {self.hitdamage[1]}"
        if self.gui is not None:
            if self.equipped: self.gui.toggleButton.setText('\u2611')
            else: self.gui.toggleButton.setText('\u2610')
            self.gui.infoButton.setText(tempstring)
        if upc: 
            self.c.update()
            self.update()
        if upe:
            for i in self.c.equiplist: i.update()
    def enable(self):
        self.equipped=True
        for mod in self.mods:
            if mod[0]=='AC' and type(self.maxdex)==int and (self.maxdex<statmod(self.c.cstats['DEX']) or self.maxdex==0): #heavy armor, maxdex==0 and negative dex mod is not counted
                self.ACadded=mod[1]+self.maxdex-statmod(self.c.cstats['DEX']) #fix infinite AC exploit
                self.c.cstats[mod[0]]+=self.ACadded
            elif mod[0]=='AC' and type(self.maxdex)==int:
                self.ACadded=mod[1]
                self.c.cstats[mod[0]]+=self.ACadded
            else: self.c.cstats[mod[0]]+=mod[1]
        self.update(upc=True,upe=True)
    def disable(self):
        self.equipped=False
        for mod in self.mods:
            if mod[0]=='AC' and type(self.maxdex)==int and (self.maxdex<statmod(self.c.cstats['DEX']) or self.maxdex==0): #heavy armor, maxdex==0 and negative dex mod is not counted
                self.c.cstats[mod[0]]-=self.ACadded #fix infinite AC exploit
            elif mod[0]=='AC' and type(self.maxdex)==int: self.c.cstats[mod[0]]-=self.ACadded
            else: self.c.cstats[mod[0]]-=mod[1]
        self.update(upc=True,upe=True)
    def toggle(self):
        if self.equipped: self.disable()            
        else: self.enable()
    def show(self):
        self.gui=equipWidget(self)
        self.update()
    def delete(self):
        if self.equipped: self.toggle()
        self.c.equiplist.remove(self)
    def save(self):
        tempstring=f"%EQUIP\nNAME={self.name}"
        if len(self.mods)>0: 
            tempstring+="\nMODS="
            for mod in self.mods: tempstring+=f"{mod[0]}:{mod[1]:+d}, "
            tempstring=tempstring[:-2]
        if self.hitdamage[1]!=0:tempstring+=f"\nHITDAMAGE={self.hitdamage[0]} {self.hitdamage[1]}"
        if self.scaling!='no':tempstring+=f"\nSCALING={self.scaling}"
        if self.prof: tempstring+="\nPROF=YES"
        if type(self.maxdex)==int: tempstring+=f"\nMAXDEX={self.maxdex:+d}"
        if self.equipped: tempstring+='\nEQUIPPED=YES'
        return tempstring+f'\nTEXT={self.text}\n\n'

class equipWidget(contextWidget):
    def __init__(self,equip):
        super().__init__(movable=True)
        self.equip=equip
        self.toggleButton=QPushButton(text='[?]',clicked=self.equip.toggle)
        self.toggleButton.setFixedWidth(self.toggleButton.sizeHint().height())
        self.layout.addWidget(self.toggleButton)
        self.infoButton=QPushButton(text=self.equip.name,clicked=self.showinfo)
        self.layout.addWidget(self.infoButton)
        self.equip.c.gui.mainPage.cEquipLayout.insertWidget(self.equip.c.gui.mainPage.cEquipLayout.count(),self)
    def showinfo(self):
        self.dialog=PopupDialog(self.equip.name,self.equip.description.replace('\\','\n'))
        self.dialog.show()
    def edit(self):
        if self.equip.equipped: 
            self.equip.disable()
            reEnable=True
        else: reEnable=False
        dialog=getEquip(self.equip)
        if dialog.exec()==QDialog.Accepted:
            newDict=dialog.getData()
            self.equip.load(newDict)
            if reEnable: self.equip.enable()
            self.equip.update(upc=True,upe=True)
    def delete(self):
        self.equip.c.gui.mainPage.cEquipLayout.removeWidget(self)
        self.setParent(None)
        self.deleteLater()
        self.equip.delete()
    def moveUp(self):
        self.move(self.equip,self.equip.c.equiplist,self.equip.c.gui.mainPage.cEquipLayout,up=True)
        self.equip.c.update()
    def moveDown(self):
        self.move(self.equip,self.equip.c.equiplist,self.equip.c.gui.mainPage.cEquipLayout,up=False)
        self.equip.c.update()

class getEquip(QDialog5e):
    def __init__(self,oldEquip=None):
        super().__init__()
        self.setWindowTitle('New Equipment')
        mainLayout=QVBoxLayout()
        self.setLayout(mainLayout)
        formLayout=QFormLayout()
        self.name=QLineEdit()
        self.bonuses=QLineEdit()
        self.maxdex=NoWheelSpinBox()
        self.maxdexcheck=QCheckBox()
        self.tohit=QLineEdit()
        self.scaling=QComboBox()
        self.scaling.addItems(['','STR','DEX','CON','INT','WIS','CHA'])
        self.prof=QCheckBox()
        self.description=QTextEdit()
        formLayout.addRow('Name:',self.name)
        formLayout.addRow('Bonuses (e.g. AC:3, STR:2):',self.bonuses)
        formLayout.addRow('Limits Max DEX Mod?',self.maxdexcheck)
        formLayout.addRow('Maximum DEX Mod:',self.maxdex)
        formLayout.addRow('To Hit/Damage (e.g. 1/1d6+1):',self.tohit)
        formLayout.addRow('Scaling:',self.scaling)
        formLayout.addRow('Proficient?',self.prof)
        formLayout.addRow('Description:',self.description)
        mainLayout.addLayout(formLayout)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.verifyData)
        buttons.rejected.connect(self.reject)
        mainLayout.addWidget(buttons)
        if oldEquip is not None:
            self.name.setText(oldEquip.name)
            if len(oldEquip.mods)>0: self.bonuses.setText(', '.join([f'{i[0]}:{i[1]:+d}' for i in oldEquip.mods]))
            if oldEquip.maxdex is not None: 
                self.maxdexcheck.setChecked(True)
                self.maxdex.setValue(oldEquip.maxdex)
            if oldEquip.hitdamage!=[0,0]: self.tohit.setText(f'{oldEquip.hitdamage[0]} {oldEquip.hitdamage[1]}')
            if oldEquip.scaling!='no': self.scaling.setCurrentText(oldEquip.scaling)
            if oldEquip.prof: self.prof.setChecked(True)
            self.description.setText(oldEquip.description)
    def verifyData(self):
        if len(self.name.text())<1: 
            QMessageBox.warning(self,'Invalid Name','No name provided.')
            return 
        if len(self.bonuses.text().strip())>0:
            try:
                temp=[mod.strip().split(':') for mod in self.bonuses.text().split(',')]
                for mod in temp: mod[1]=int(mod[1])
            except: 
                QMessageBox.warning(self,'Invalid Bonus Syntax','Invalid Bonus Syntax')
                return
        if len(self.tohit.text().strip())>0:
            try: temp=f"{int(self.tohit.text().split('/')[0])} {self.tohit.text().split('/')[1]}"
            except: QMessageBox.warning(self,'Invalid To Hit/Damage Syntax','Invalid To Hit/Damage Syntax')
        self.accept()
    def getData(self):
        outdict={'NAME':self.name.text().strip()}
        if len(self.tohit.text().strip())>0: outdict['HITDAMAGE']=f"{int(self.tohit.text().split('/')[0])} {self.tohit.text().split('/')[1]}"
        if len(self.bonuses.text().strip())>0: outdict['MODS']=self.bonuses.text().strip()
        if self.prof.isChecked(): outdict['PROF']="YES"
        else: outdict['PROF']="NO"
        if self.maxdexcheck.isChecked(): outdict['MAXDEX']=self.maxdex.value()
        if self.scaling.currentText()!='': outdict['SCALING']=self.scaling.currentText()
        if self.description.toPlainText().strip()!='': outdict['TEXT']=self.description.toPlainText().strip()
        return outdict