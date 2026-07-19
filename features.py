from PySide6.QtWidgets import QVBoxLayout, QPushButton, QMessageBox, QDialog, QTextEdit, QFormLayout, QLineEdit, QDialogButtonBox
from gui.common import contextWidget, PopupDialog, QDialog5e

class feature():
    def __init__(self,featdict,c):
        self.c=c
        self.name='?'
        self.mods=[]
        self.description='(No Description)'
        self.text=''
        self.load(featdict)
        self.enable()
    def load(self,featdict):
        if 'NAME' in featdict: self.name=featdict['NAME']
        if 'MODS' in featdict: 
            if featdict['MODS']=='': pass
            else:                 
                self.mods=featdict['MODS']
                self.mods=[mod.strip().split(':') for mod in self.mods.split(',')]
                for mod in self.mods: mod[1]=int(mod[1])
        if 'TEXT' in featdict: 
            self.text=featdict['TEXT'].replace('\n','\\')
            self.description=featdict['TEXT'].replace('\\','\n')
    def show(self):
        self.gui=featureWidget(self)
    def delete(self):
        self.c.featurelist.remove(self)
        self.disable()
        self.c.update()
    def enable(self):
        for mod in self.mods: self.c.cstats[mod[0]]+=mod[1]
        self.c.update()
    def disable(self):
        for mod in self.mods: self.c.cstats[mod[0]]-=mod[1]
        self.c.update()
    def save(self):
        tempstring=f"%FEATURE\nNAME={self.name}"
        if len(self.mods)>0: 
            tempstring+="\nMODS="
            for mod in self.mods: tempstring+=f"{mod[0]}:{mod[1]:+d}, "
            tempstring=tempstring[:-2]
        return tempstring+f'\nTEXT={self.text}\n\n'

class featureWidget(contextWidget):
    def __init__(self,feat):
        self.feat=feat
        super().__init__(movable=True)
        self.button=QPushButton(text=self.feat.name,clicked=self.showinfo)
        self.layout.addWidget(self.button)
        self.feat.c.gui.mainPage.featureLayout.insertWidget(self.feat.c.gui.mainPage.featureLayout.count(),self)
    def delete(self):
        self.feat.c.gui.mainPage.featureLayout.removeWidget(self)
        self.setParent(None)
        self.deleteLater()
        self.feat.delete()
    def edit(self):
        dialog=getFeature(self.feat.save())
        if dialog.exec()==QDialog.Accepted:
            self.feat.disable()
            newdict=dialog.getData()
            self.feat.load(newdict)
            self.button.setText(self.feat.name)
            self.feat.enable()
    # def move(self,up=True,item,itemlist,layout):
    #     idx=self.feat.c.featurelist.index(self.feat)
    #     if up:
    #         if idx==0: return
    #         else: newidx=idx-1
    #     else:
    #         if idx==len(self.feat.c.featurelist): return
    #         else: newidx=idx+1
    #     self.feat.c.featurelist.insert(newidx,self.feat.c.featurelist.pop(idx))
    #     for _ in range(len(self.feat.c.featurelist)): _=self.feat.c.gui.mainPage.featureLayout.takeAt(1) #clear the layout
    #     for feati in self.feat.c.featurelist: self.feat.c.gui.mainPage.featureLayout.addWidget(feati.gui)
    def moveUp(self):
        self.move(self.feat,self.feat.c.featurelist,self.feat.c.gui.mainPage.featureLayout,up=True)
        self.feat.c.update()
    def moveDown(self):
        self.move(self.feat,self.feat.c.featurelist,self.feat.c.gui.mainPage.featureLayout,up=False)
        self.feat.c.update()
    def showinfo(self):
        self.dialog=PopupDialog(self.feat.name,self.feat.description.replace('\\','\n'))
        self.dialog.show()

class getFeature(QDialog5e):
    def __init__(self,savestring=''):
        super().__init__()
        self.setWindowTitle('New Feature')
        mainLayout=QVBoxLayout()
        self.setLayout(mainLayout)
        formLayout=QFormLayout()
        self.name=QLineEdit()
        self.bonuses=QLineEdit()
        self.description=QTextEdit()
        formLayout.addRow('Name:',self.name)
        formLayout.addRow('Bonuses (e.g. AC:3, STR:2):',self.bonuses)
        formLayout.addRow('Description',self.description)
        mainLayout.addLayout(formLayout)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.verifyData)
        buttons.rejected.connect(self.reject)
        mainLayout.addWidget(buttons)
        if savestring!='':
            indict={i[0]:i[1] for i in [j.strip().split('=') for j in savestring.strip().split('\n')[1:]]}
            self.name.setText(indict['NAME'])
            if 'MODS' in indict: self.bonuses.setText(indict['MODS'])
            if 'TEXT' in indict: self.description.setText(indict['TEXT'].replace('\\','\n'))
    def verifyData(self):
        if len(self.name.text())<1: 
            QMessageBox.warning(self,'Invalid Name','No name provided.')
            return 
        try:
            if len(self.bonuses.text().strip())>0:
                temp=[mod.strip().split(':') for mod in self.bonuses.text().split(',')]
                for mod in temp: mod[1]=int(mod[1])
        except:
            QMessageBox.warning(self,'Invalid Bonus Syntax','Invalid Bonus Syntax')
            return 
        self.accept()
    def getData(self):
        return {'NAME':self.name.text().strip(),'MODS':self.bonuses.text().strip(),'TEXT':self.description.toPlainText().strip()}