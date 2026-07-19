from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QTabWidget, QInputDialog, QFileDialog, QMessageBox, QDialog, QTextEdit, QFormLayout, QLineEdit, QDialogButtonBox, QCheckBox, QComboBox
from PySide6.QtCore import Qt

from items import item, getItem
from features import feature, getFeature
from abilities import ability, getAbility
from equipments import equipment, getEquip
from spells import load_spells, spell, getSpell
from gui.common import QMainWindow5e, QDialog5e, PopupDialog, NoWheelSpinBox
from gui.spells_page import spellsPage
from gui.inventory import inventoryPage
from gui.notes_page import notesPage
from gui.main_page import mainPage
from utilities import statmod

class character():
    def __init__(self,currentversion): #initalize blank character
        self.filepath=None
        self.name='NAME'
        self.classes='CLASS'
        self.stats={'HP':0,'MAXHP':0,'TEMPHP':0,'SPEED':30,'STR':10,'DEX':10,'CON':10,'INT':10,'WIS':10,'CHA':10,'PRO':0}
        self.langs=[]
        self.profs=[]
        self.skills=[]
        self.experts=[]
        self.savethrows=[]
        self.caststat=''
        self.notes=''
        self.featurelist=[]
        self.spellist=[]
        self.abilitylist=[]
        self.equiplist=[]
        self.backpacklist=[]
        self.spellbookdict={str(i):[] for i in range(10)}
        self.masterspellsdict=load_spells()
        self.color=[236,230,220]
        self.fontcolor=[0,0,0]
        self.fontsize=10
        self.allskills=sorted([['Investigation (P)','INT'],['Insight (P)','WIS'],['Perception (P)','WIS'],['Initiative', 'DEX'],['Athletics','STR'],['Acrobatics','DEX'],['Sleight of Hand','DEX'],['Stealth','DEX'],['Arcana','INT'],['History','INT'],['Investigation','INT'],['Nature','INT'],['Religion','INT'],['Animal Handling','WIS'],['Insight','WIS'],['Medicine','WIS'],['Perception','WIS'],['Survival','WIS'],['Deception','CHA'],['Intimidation','CHA'],['Performance','CHA'],['Persuasion','CHA']])
        self.cstats={i:self.stats[i] for i in self.stats} #make dictionary of current stats that can be modified by items etc
        self.cstats['AC']=10#+statmod(self.cstats['DEX']) #now treated as bonus to AC to allow for AC changes when dex changes
        self.cstats['CAST'],self.cstats['DC'],self.cstats['SAB']=0,0,0 #even if a character doesn't have spells, they could still have equipment that buffs these values
        for skill in self.allskills: 
            self.cstats[skill[0]]=0 #store bonuses to skills granted by items etc. Zero to start.
            self.cstats[skill[0]+'bonus']=0 #store the actual bonus with ability scores, skills, and expertises (and Jack of All Trades) for easy lookup
        self.gui=None
        self.currentversion=currentversion
    def load(self,filepath):
        self.filepath=filepath
        with open(filepath,'r') as file:
            linesdict={}
            for line in file:
                if line.strip()=='': continue
                elif line.strip().startswith('%%'):
                    currentblock=line.strip()[2:]
                    linesdict[currentblock]=[]
                else: linesdict[currentblock].append(line)
        if 'VERSION' in linesdict: self.version=linesdict['VERSION']
        for line in linesdict['CHARACTER']:
            line=line.strip()
            if line=='': continue
            line=line.split('=')
            if line[0]=='NAME': self.name=line[1].strip()
            elif line[0]=='CLASS': self.classes=line[1].strip()
            elif line[0] in ['HP','MAXHP','TEMPHP','STR','DEX','CON','INT','WIS','CHA','PRO']: self.stats[line[0]]=int(line[1])
            elif line[0]=='SPEED': self.stats['SPEED']=int(float(line[1]))
            elif line[0]=='GOLD': self.stats['GOLD']=float(line[1]) #to be removed in future versions as character.stats['GOLD'] will be removed
            elif line[0]=='LANGUAGES': self.langs=[i.strip() for i in line[1].split(',')]
            elif line[0]=='PROFS': self.profs=[i.strip() for i in line[1].split(',')]
            elif line[0]=='SKILLS': self.skills=[i.strip() for i in line[1].strip().split(',')]
            elif line[0]=='EXPERT': self.experts=[i.strip() for i in line[1].strip().split(',')]
            elif line[0]=='SAVETHROWS': self.savethrows=[i.strip() for i in line[1].strip().split(',')]
            elif line[0]=='COLOR': self.color=[int(i) for i in line[1].strip().split(',')]
            elif line[0]=='FONTCOLOR': self.fontcolor=[int(i) for i in line[1].strip().split(',')]
            elif line[0]=='FONTSIZE': self.fontsize=int(float(line[1].strip()))
            elif line[0]=='CASTINGSTAT': self.caststat=line[1].strip()
            else: pass
        for i in self.stats: self.cstats[i]=self.stats[i]
        self.cstats['AC']=10#+statmod(self.cstats['DEX']) #now treated as bonus to AC to allow for AC changes when dex changes
        for skill in self.allskills: self.cstats[skill[0]]=0 #store bonuses to skills granted by items etc. Zero to start.
        self.attributes={}
        for line in linesdict['ATTRIBUTES']:
            line=line.strip()
            if line=='': continue
            elif line[0]=='%':
                currenttype=line[1:]
                if currenttype not in self.attributes: self.attributes[currenttype]=[]
                self.attributes[currenttype].append({})
            else: self.attributes[currenttype][-1][line.split('=')[0].strip()]=line.split('=')[1].strip()
        if 'ABILITY' in self.attributes: self.abilitylist=[ability(abilitydict,self) for abilitydict in self.attributes['ABILITY']]
        else: self.abilitylist=[]
        if 'SPELL' in self.attributes: 
            for spelldict in self.attributes['SPELL']:
                temp=spell(spelldict,self)
                self.spellbookdict[str(temp.level)].append(temp)
        self.cstats['CAST'],self.cstats['DC'],self.cstats['SAB']=0,0,0 #even if a character doesn't have spells, they could still have equipment that buffs these values
        if 'FEATURE' in self.attributes: self.featurelist=[feature(featuredict,self) for featuredict in self.attributes['FEATURE']]
        else: self.featurelist=[]
        if 'EQUIP' in self.attributes: self.equiplist=[equipment(equipdict,self) for equipdict in self.attributes['EQUIP']]
        else: self.equiplist=[]
        if 'BACKPACK' in linesdict: self.backpacklist=[item(bpline,self) for bpline in linesdict['BACKPACK'] if len(bpline)>2]
        else: self.backpacklist=[]
        if 'GOLD' in self.stats: self.backpacklist.insert(0,item(f"Gold:{int(self.stats['GOLD'])}",self)) #to be removed in future versions as character.stats['GOLD'] will be removed
        if 'NOTES' in linesdict: 
            if len(linesdict['NOTES'])>0:
                for line in linesdict['NOTES']: self.notes+=line
        else: self.notes=''
        self.show()
        self.update()
        if self.filepath is not None: self.gui.setWindowTitle(self.filepath.split('/')[-1].split('\\')[-1])
        self.gui.quitAllowed=True #override after inital load to permit quitting without saving
    def show(self):
        self.gui=MainWindow(self)
        self.gui.show()
        self.gui.showContent()
    def update(self):
        if self.stats['HP']>self.cstats['MAXHP']: self.stats['HP']=self.cstats['MAXHP']
        for stat in ['STR','DEX','CON','INT','WIS','CHA']:
            savebonus=statmod(self.cstats[stat])
            if stat in self.savethrows: savebonus+=self.cstats['PRO']
        for skill in self.allskills:
            training=''
            bonus=self.cstats[skill[0]]
            if '(P)' in skill[0]: bonus+=self.cstats[skill[0].replace(' (P)','')]
            bonus+=statmod(self.cstats[skill[1]])
            if skill[0] in self.experts or skill[0].replace(' (P)','') in self.experts: 
                bonus+=2*self.cstats['PRO']
                training+='**'
            elif skill[0] in self.skills or skill[0].replace(' (P)','') in self.skills: 
                bonus+=self.cstats['PRO']
                training+='*'
            elif 'JACK' in [feat.name[:4].upper() for feat in self.featurelist]: bonus+=self.cstats['PRO']//2
            self.cstats[skill[0]+'bonus']=bonus #save bonus for easier lookup            
        if self.gui is not None: self.gui.update()
    def rest(self,resttype):
        if resttype=='LR': resttype=['LR','SR']
        else: resttype=[resttype]
        for j in resttype:
            for i in self.abilitylist: i.rest(j.upper())
            if j=='LR': 
                self.stats['TEMPHP']=0
                self.stats['HP']=self.stats['MAXHP'] 
        self.update()
    def save(self,filepath):
        self.update()
        self.gui.setWindowTitle(filepath.split('/')[-1].split('\\')[-1])
        self.filepath=filepath
        with open(filepath,'w') as file:
            file.write(f"%%CHARACTER\nNAME={self.name}\nCLASS={self.classes}\n")
            for i in self.stats: 
                if 'GOLD' not in i: #GOLD will become a backpack item now. To be removed in a future version
                    file.write(f"{i}={self.stats[i]}\n")
            if len(self.savethrows)>0:
                savethrowstring='SAVETHROWS='
                for savethrow in self.savethrows: savethrowstring+=f'{savethrow},'
                file.write(savethrowstring[:-1]+'\n')
            if len(self.skills)>0:
                skillstring='SKILLS='
                for skill in self.skills: skillstring+=f'{skill},'
                file.write(skillstring[:-1]+'\n')
            if len(self.experts)>0:
                expertstring='EXPERT='
                for expert in self.experts: expertstring+=f'{expert},'
                file.write(expertstring[:-1]+'\n')
            if self.caststat!='': file.write('CASTINGSTAT='+self.caststat+'\n')
            langsstring='LANGUAGES='
            if len(self.langs)>0:
                for lang in self.langs: langsstring+=f'{lang},'
                file.write(langsstring[:-1]+'\n')
            else: file.write(langsstring+'\n')
            profsstring='PROFS='
            if len(self.profs)>0:
                for prof in self.profs: profsstring+=f'{prof},'
                file.write(profsstring[:-1]+'\n')
            else: file.write(profsstring+'\n')
            file.write(f"COLOR={self.color[0]},{self.color[1]},{self.color[2]}\n")
            file.write(f"FONTCOLOR={self.fontcolor[0]},{self.fontcolor[1]},{self.fontcolor[2]}\n")
            file.write(f"FONTSIZE={self.fontsize}\n")
            file.write('\n%%ATTRIBUTES\n')
            for ability in self.abilitylist: file.write(ability.save())
            for equip in self.equiplist: file.write(equip.save())
            for level in self.spellbookdict: 
                for spell in self.spellbookdict[level]: file.write(spell.save())
            for feature in self.featurelist: file.write(feature.save())
            file.write('%%BACKPACK\n')
            for item in self.backpacklist:file.write(item.save())
            file.write(f"\n%%NOTES\n{self.gui.notesPage.notes.toPlainText()}")
            file.write(f"%%VERSION\n{self.currentversion}")


class MainWindow(QMainWindow5e):
    def __init__(self,c):
        super().__init__()
        self.c=c
        self.setFont(c.fontsize)
        self.resize(int(700*(c.fontsize/9)),int(800*(c.fontsize/9))) #700 is a guess for width, 800 perfectly fits all skills
        # self.resize(700,800)
        self.setWindowTitle('Py5e')
        self.quitAllowed=True

        saveShortcut=QShortcut(QKeySequence("Ctrl+S"), self)
        saveShortcut.activated.connect(self.save)

        menu_bar=self.menuBar()
        file_menu=menu_bar.addMenu("File")
        save_action=QAction("Save",self)
        save_action.triggered.connect(self.save)
        file_menu.addAction(save_action)
        saveAs_action=QAction("Save As...",self)
        saveAs_action.triggered.connect(self.saveAs)
        file_menu.addAction(saveAs_action)
        save_and_quit_action=QAction("Save and Quit",self)
        save_and_quit_action.triggered.connect(self.save_and_quit)
        file_menu.addAction(save_and_quit_action)
        quit_action=QAction("Quit",self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        newMenu=menu_bar.addMenu("Add")
        newAbilityAction=QAction("Ability...",self)
        newAbilityAction.triggered.connect(self.newAbility)
        newMenu.addAction(newAbilityAction)
        newEquipAction=QAction("Equipment...",self)
        newEquipAction.triggered.connect(self.newEquip)
        newMenu.addAction(newEquipAction)
        newFeatureAction=QAction("Feature...",self)
        newFeatureAction.triggered.connect(self.newFeature)
        newMenu.addAction(newFeatureAction)
        newItemAction=QAction("Item...",self)
        newItemAction.triggered.connect(self.newItem)
        newMenu.addAction(newItemAction)
        newSpellAction=QAction("Spell...",self)
        newSpellAction.triggered.connect(self.newSpell)
        newMenu.addAction(newSpellAction)

        editMenu=menu_bar.addMenu("Edit")
        editCharacterAction=QAction("Character...",self)
        editCharacterAction.triggered.connect(self.editCharacter)
        editMenu.addAction(editCharacterAction)
        editFontAction=QAction("Font...",self)
        editFontAction.triggered.connect(self.editFont)
        editMenu.addAction(editFontAction)
        editRemoveAction=QAction("Remove...",self)
        editRemoveAction.triggered.connect(self.editRemove)
        editMenu.addAction(editRemoveAction)

        rest_menu=menu_bar.addMenu("Rest")
        short_rest=QAction("Short Rest",self)
        short_rest.triggered.connect(lambda: self.rest('SR'))
        rest_menu.addAction(short_rest)
        long_rest=QAction("Long Rest",self)
        long_rest.triggered.connect(lambda: self.rest('LR'))        
        rest_menu.addAction(long_rest)
        day_rest=QAction("Next Day",self)
        day_rest.triggered.connect(lambda: self.rest('DAY'))
        rest_menu.addAction(day_rest)

        self.content=QWidget()
        self.setCentralWidget(self.content)

        tabLayout=QVBoxLayout()
        self.content.setLayout(tabLayout)
        self.tabs=QTabWidget(self.content)
        tabLayout.addWidget(self.tabs)

        self.mainPage=mainPage(self.c)
        self.tabs.addTab(self.mainPage,'Character')
        self.spellsPage=spellsPage()
        self.tabs.addTab(self.spellsPage,'Spells')
        self.bpPage=inventoryPage()
        self.tabs.addTab(self.bpPage,'Inventory')
        self.notesPage=notesPage()
        self.tabs.addTab(self.notesPage,'Notes')

    def showContent(self):
        for feat in self.c.featurelist: feat.show()
        for ability in self.c.abilitylist: ability.show()
        for equip in self.c.equiplist: equip.show()
        for item in self.c.backpacklist: item.show()
        if len([self.c.spellbookdict['0']])>0: self.spellsPage.spellLVLLayouts['0'].addWidget(QLabel('Cantrips',alignment=Qt.AlignmentFlag.AlignCenter))
        for level in self.c.spellbookdict: 
            for spell in self.c.spellbookdict[level]: spell.show()
        self.notesPage.notes.setText(self.c.notes)
    def update(self):
        if self.c.filepath is not None: self.setWindowTitle('*'+self.c.filepath.split('/')[-1].split('\\')[-1])
        self.mainPage.displayNameClass.setText(f"{self.c.name}\n{self.c.classes}")
        self.mainPage.displayHP.setText(f"HP: {self.c.stats['HP']}/{self.c.stats['MAXHP']}")
        if self.c.stats['TEMPHP']>0: self.mainPage.displayTempHP.setText(f"{self.c.stats['TEMPHP']:+d}")
        else: self.mainPage.displayTempHP.setText("")
        self.mainPage.displayACSpeed.setText(f"AC: {self.c.cstats['AC']+statmod(self.c.cstats['DEX'])}, Speed: {self.c.cstats['SPEED']}ft")
        self.mainPage.displayStats['Proficiency'].setText(f"Proficiency: {self.c.cstats['PRO']}")
        for stat in ['STR','DEX','CON','INT','WIS','CHA']:
            savebonus=statmod(self.c.cstats[stat])
            if stat in self.c.savethrows: savebonus+=self.c.cstats['PRO']
            self.mainPage.displayStats[stat].setText(f"{stat}: {self.c.cstats[stat]} ({statmod(self.c.cstats[stat]):+d}) ({savebonus:+d})")
        for skill in self.c.allskills:
            training=''
            bonus=self.c.cstats[skill[0]]
            if '(P)' in skill[0]: bonus+=self.c.cstats[skill[0].replace(' (P)','')]
            bonus+=statmod(self.c.cstats[skill[1]])
            if skill[0] in self.c.experts or skill[0].replace(' (P)','') in self.c.experts: 
                bonus+=2*self.c.cstats['PRO']
                training+='**'
            elif skill[0] in self.c.skills or skill[0].replace(' (P)','') in self.c.skills: 
                bonus+=self.c.cstats['PRO']
                training+='*'
            elif 'JACK' in [feat.name[:4].upper() for feat in self.c.featurelist]: bonus+=self.c.cstats['PRO']//2
            self.c.cstats[skill[0]+'bonus']=bonus #save bonus for easier lookup        
            self.mainPage.displayStats[skill[0]].setText(f"{training}{skill[0]}: {bonus:+d}")
        if self.c.caststat!='': self.spellsPage.spellsHeader.setText(f"Casting ability: {statmod(self.c.cstats[self.c.caststat])+self.c.cstats['PRO']:+d}, Save DC: {8+statmod(self.c.cstats[self.c.caststat])+self.c.cstats['PRO']:+d}, Spell Attack Bonus: {statmod(self.c.cstats[self.c.caststat])+self.c.cstats['PRO']:+d}")
        #remove and reconstruct land and profs in case of new ones added during editing
        while self.mainPage.langLayout.count(): 
            item=self.mainPage.langLayout.takeAt(0)
            widget=item.widget()
            if widget is not None: widget.deleteLater()
        self.mainPage.langLayout.addWidget(QLabel('Languages:',alignment=Qt.AlignmentFlag.AlignCenter))
        for lang in self.c.langs: self.mainPage.langLayout.addWidget(QLabel(lang))
        while self.mainPage.profLayout.count():
            item=self.mainPage.profLayout.takeAt(0)
            widget=item.widget()
            if widget is not None: widget.deleteLater()
        self.mainPage.profLayout.addWidget(QLabel('Proficiencies:',alignment=Qt.AlignmentFlag.AlignCenter))
        for prof in self.c.profs: self.mainPage.profLayout.addWidget(QLabel(prof))
        self.mainPage.profLayout.addStretch()
        self.quitAllowed=False
    def rest(self,restType):
        self.c.rest(restType)
    def saveAs(self):
        filepath,selectedfilter=QFileDialog.getSaveFileName(self,"Save File","","Py5e Files (*.5e);;All Files (*)")
        self.c.save(filepath)
        self.quitAllowed=True
    def save(self):
        if self.c.filepath is not None: 
            self.c.save(self.c.filepath)
            self.quitAllowed=True
        else: self.saveAs()
    def save_and_quit(self):
        self.save()
        self.close()
    def askToQuit(self):
        reply=QMessageBox.question(self,"Confirm Exit","Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
        if reply==QMessageBox.Yes: return True
        else: return False
    def closeEvent(self,event): #intercept close events to prompt to exit unless save_and_quit has been called
        if self.quitAllowed: event.accept()
        else:
            if self.askToQuit(): event.accept()
            else: event.ignore()

    def newFeature(self):
        dialog=getFeature()
        if dialog.exec()==QDialog.Accepted:
            self.c.featurelist.append(feature(dialog.getData(),self.c))
            self.c.featurelist[-1].show()
            self.c.update()
    def newAbility(self):
        dialog=getAbility(self.c)
        if dialog.exec()==QDialog.Accepted:
            self.c.abilitylist.append(ability(dialog.getData(),self.c))
            self.c.abilitylist[-1].show()
            self.c.update()
    def newItem(self):
        dialog=getItem()
        if dialog.exec()==QDialog.Accepted:
            self.c.backpacklist.append(item(dialog.getData(),self.c))
            self.c.backpacklist[-1].show()
            self.c.update()
    def newEquip(self):
        dialog=getEquip()
        if dialog.exec()==QDialog.Accepted:
            self.c.equiplist.append(equipment(dialog.getData(),self.c))
            self.c.equiplist[-1].show()
            self.c.update()
    def newSpell(self):
        dialog=getSpell(self.c.masterspellsdict)
        if dialog.exec()==QDialog.Accepted:
            temp=spell(dialog.getData(),self.c)
            self.c.spellbookdict[str(temp.level)].append(temp)
            self.c.spellbookdict[str(temp.level)][-1].show()
            self.c.update()
    def editCharacter(self):
        dialog=getStats(self.c)
        if dialog.exec()==QDialog.Accepted: dialog.getData()
    def editFont(self):
        fontSize,ok=QInputDialog.getInt(self,"Set Font Size",'Enter Font Size',value=QApplication.font().pointSize(),minValue=1,maxValue=200)
        if ok: 
            self.setFont(fontSize)
            self.c.fontsize=fontSize
            self.c.update()
    def setFont(self,fontsize):
        font=QApplication.font()
        font.setPointSize(fontsize)
        QApplication.setFont(font)
        # temp=self.menuBar()
        # temp.setFont(font)
        # for menu in temp.findChildren(QWidget): menu.setFont(font)
    def editRemove(self):
        self.removedialog=PopupDialog('Remove...','To remove an Ability, Equipment, Feature, Item, or Spell, simply Right-Click that object and select "Delete" from the drop-down menu.')
        self.removedialog.show()

class getStats(QDialog5e):
    def __init__(self,c):
        super().__init__()
        self.c=c
        self.setWindowTitle('Edit Character')
        mainLayout=QVBoxLayout()
        self.setLayout(mainLayout)
        LRLayout=QHBoxLayout()
        mainLayout.addLayout(LRLayout)
        formLayoutL=QFormLayout()
        formLayoutR=QFormLayout()
        LRLayout.addLayout(formLayoutL)
        LRLayout.addLayout(formLayoutR)
        self.name=QLineEdit(text=self.c.name)
        self.classes=QLineEdit(text=self.c.classes)
        self.maxhp=NoWheelSpinBox(minimum=0,maximum=999999,value=self.c.stats['MAXHP'])
        self.speed=NoWheelSpinBox(minimum=0,maximum=999999,value=self.c.stats['SPEED'])
        self.abscores={i:NoWheelSpinBox(minimum=0,maximum=999999,value=self.c.stats[i]) for i in ['STR','DEX','CON','INT','WIS','CHA','PRO']}
        self.savethrows={i:QCheckBox() for i in ['STR','DEX','CON','INT','WIS','CHA']}
        for i in ['STR','DEX','CON','INT','WIS','CHA']:
            if i in self.c.savethrows: self.savethrows[i].setChecked(True)
        self.skills={i:QCheckBox() for i in [j[0] for j in c.allskills]}
        self.experts={i:QCheckBox() for i in [j[0] for j in c.allskills]}
        for i in [j[0] for j in c.allskills]:
            if i in self.c.skills: self.skills[i].setChecked(True)
            if i in self.c.experts: self.experts[i].setChecked(True)            
        self.caststat=QComboBox()
        self.caststat.addItems(['','STR','DEX','CON','INT','WIS','CHA'])
        self.caststat.setCurrentText(self.c.caststat)
        self.profs=QTextEdit(plainText='\n'.join(self.c.profs))
        self.langs=QTextEdit(plainText='\n'.join(self.c.langs))
        formLayoutL.addRow('Name:',self.name)
        formLayoutL.addRow('Classes',self.classes)
        formLayoutL.addRow('Max HP',self.maxhp)
        formLayoutL.addRow('Casting Stat',self.caststat)
        formLayoutR.addRow(QLabel('Proficient / Expert'))
        for i in self.abscores:
            temp=QHBoxLayout()
            temp.addWidget(self.abscores[i])
            if i!='PRO': temp.addWidget(self.savethrows[i])
            formLayoutL.addRow(i,temp)
        for i in self.skills:
            temp=QHBoxLayout()
            temp.addWidget(self.skills[i])
            temp.addWidget(self.experts[i])
            formLayoutR.addRow(i,temp)
        formLayoutL.addRow('Proficiencies (one per line)',self.profs)
        formLayoutL.addRow('Languages (one per line)',self.langs)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.verifyData)
        buttons.rejected.connect(self.reject)
        mainLayout.addWidget(buttons)
    def verifyData(self):
        if len(self.name.text())<1: 
            QMessageBox.warning(self,'Invalid Name','No character name provided.')
            return 
        self.accept()
    def getData(self):
        self.c.name=self.name.text().strip()
        self.c.classes=self.classes.text().strip()
        self.c.caststat=self.caststat.currentText()
        self.c.cstats['MAXHP']+=self.maxhp.value()-self.c.stats['MAXHP']
        self.c.stats['MAXHP']=self.maxhp.value()
        self.c.cstats['SPEED']+=self.speed.value()-self.c.stats['SPEED']
        self.c.stats['SPEED']=self.speed.value()
        for i in ['PRO','STR','DEX','CON','INT','WIS','CHA']:
            self.c.cstats[i]+=self.abscores[i].value()-self.c.stats[i]
            self.c.stats[i]=self.abscores[i].value()
        self.c.skills=[i[0] for i in self.c.allskills if self.skills[i[0]].isChecked()]
        self.c.experts=[i[0] for i in self.c.allskills if self.experts[i[0]].isChecked()]
        self.c.langs=sorted([lang.strip() for lang in self.langs.toPlainText().split('\n') if len(lang.strip())>0])
        self.c.profs=sorted([prof.strip() for prof in self.profs.toPlainText().split('\n') if len(prof.strip())>0])
        self.c.update()
        return