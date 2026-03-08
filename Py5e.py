from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget, QTabWidget, QInputDialog, QScrollArea, QFrame, QFileDialog, QMessageBox, QDialog, QSpinBox, QTextEdit, QFormLayout, QLineEdit, QDialogButtonBox, QCheckBox, QComboBox
from PySide6.QtCore import Qt
import sys
from glob import glob
from bs4 import BeautifulSoup
import requests
import json
from os import getcwd

version='2026_03_08'

class character():
    def __init__(self): #initalize blank character
        self.filepath=None
        self.bonusfeatures=[]
        self.features=[]
        self.langs=[]
        self.profs=[]
        self.skills=[]
        self.experts=[]
        self.savethrows=[]
        self.caststat=''
        self.stats={}
        self.notes=''
        self.color=[236,230,220]
        self.fontcolor=[0,0,0]
        self.fontsize=10
        self.name='NAME'
        self.classes='CLASS'
        self.stats['HP']=0
        self.stats['MAXHP']=0
        self.stats['TEMPHP']=0
        self.stats['SPEED']=30
        self.stats['STR']=10
        self.stats['DEX']=10
        self.stats['CON']=10
        self.stats['INT']=10
        self.stats['WIS']=10
        self.stats['CHA']=10
        self.stats['PRO']=0
        self.featurelist=[]
        self.spellist=[]
        self.abilitylist=[]
        self.equiplist=[]
        self.backpacklist=[]
        self.spellbooklist=[]
        self.allskills=sorted([['Investigation (P)','INT'],['Insight (P)','WIS'],['Perception (P)','WIS'],['Initiative', 'DEX'],['Athletics','STR'],['Acrobatics','DEX'],['Sleight of Hand','DEX'],['Stealth','DEX'],['Arcana','INT'],['History','INT'],['Investigation','INT'],['Nature','INT'],['Religion','INT'],['Animal Handling','WIS'],['Insight','WIS'],['Medicine','WIS'],['Perception','WIS'],['Survival','WIS'],['Deception','CHA'],['Intimidation','CHA'],['Performance','CHA'],['Persuasion','CHA']])
        self.cstats={i:self.stats[i] for i in self.stats} #make dictionary of current stats that can be modified by items etc
        self.cstats['AC']=10#+statmod(self.cstats['DEX']) #now treated as bonus to AC to allow for AC changes when dex changes
        self.cstats['CAST'],self.cstats['DC'],self.cstats['SAB']=0,0,0 #even if a character doesn't have spells, they could still have equipment that buffs these values
        for skill in self.allskills: 
            self.cstats[skill[0]]=0 #store bonuses to skills granted by items etc. Zero to start.
            self.cstats[skill[0]+'bonus']=0 #store the actual bonus with ability scores, skills, and expertises (and Jack of All Trades) for easy lookup
        self.shown=False #flag to check if the sheet has been shown yet, added so that abilites cannot update() without rendering buttons yet.
    def load(self,filepath):
        self.filepath=filepath
        with open(filename,'r') as file:
            linesdict={}
            for line in file:
                if line.strip()=='': continue
                elif line.strip()[:2]=='%%':
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
            elif line[0]=='HP': self.stats['HP']=int(line[1])
            elif line[0]=='MAXHP': self.stats['MAXHP']=int(line[1])
            elif line[0]=='TEMPHP': self.stats['TEMPHP']=int(line[1])
            elif line[0]=='SPEED': self.stats['SPEED']=int(float(line[1]))
            elif line[0]=='STR': self.stats['STR']=int(line[1])
            elif line[0]=='DEX': self.stats['DEX']=int(line[1])
            elif line[0]=='CON': self.stats['CON']=int(line[1])
            elif line[0]=='INT': self.stats['INT']=int(line[1])
            elif line[0]=='WIS': self.stats['WIS']=int(line[1])
            elif line[0]=='CHA': self.stats['CHA']=int(line[1])
            elif line[0]=='PRO': self.stats['PRO']=int(line[1])
            elif line[0]=='GOLD': self.stats['GOLD']=float(line[1]) #to be removed in future versions as character.stats['GOLD'] will be removed
            elif line[0]=='LANGUAGES': self.langs=[i.strip() for i in line[1].split(',')]
            elif line[0]=='PROFS': self.profs=[i.strip() for i in line[1].split(',')]
            elif line[0]=='FEATURES': self.features=[i.strip() for i in line[1].strip().split(',')]
            elif line[0]=='SKILLS': self.skills=[i.strip() for i in line[1].strip().split(',')]
            elif line[0]=='EXPERT': self.experts=[i.strip() for i in line[1].strip().split(',')]
            elif line[0]=='SAVETHROWS': self.savethrows=[i.strip() for i in line[1].strip().split(',')]
            elif line[0]=='COLOR': self.color=[int(i) for i in line[1].strip().split(',')]
            elif line[0]=='FONTCOLOR': self.fontcolor=[int(i) for i in line[1].strip().split(',')]
            elif line[0]=='FONTSIZE': self.fontsize=int(float(line[1].strip()))
            elif line[0]=='CASTINGSTAT': self.caststat=line[1].strip()
            else: self.bonusfeatures.append(line[0].strip())
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
        if 'SPELL' in self.attributes: self.spellbooklist=[spell(spelldict,self) for spelldict in self.attributes['SPELL']]
        else: self.spellbooklist=[]
        self.cstats['CAST'],self.cstats['DC'],self.cstats['SAB']=0,0,0 #even if a character doesn't have spells, they could still have equipment that buffs these values
        for bonus in self.bonusfeatures:
            try: self.cstats[bonus.split(':')[0]]+=int(bonus.split(':')[-1])
            except: pass
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
        self.gui.setWindowTitle(self.filepath.split('/')[-1].split('\\')[-1])
    def show(self):
        self.gui=MainWindow(self)
        self.gui.show()
        self.gui.showContent()
    # def show(self):
    #     Button(self.titleframe, text="\N{Lower Left Pencil}", command=self.edit).pack(side=LEFT,fill=Y)
    #     Button(self.titleframe, text="\N{Lower Left Paintbrush}", command=getcolor).pack(side=LEFT,fill=Y)
    #     Button(self.titleframe,text='\N{left right arrow}',command=updatefontsize).pack(side=LEFT,fill=Y)
    #     setallcolor(root,self.color,self.fontcolor)
    def update(self):
        if self.stats['HP']>self.cstats['MAXHP']: self.stats['HP']=self.cstats['MAXHP']
        for stat in ['STR','DEX','CON','INT','WIS','CHA']:
            savebonus=statmod(self.cstats[stat])
            if stat in self.savethrows: savebonus+=self.cstats['PRO']
        for skill in self.allskills:
            training=''
            if '(P)' in skill[0]:
                bonus=self.cstats[skill[0]]+self.cstats[skill[0][:-4]]
                bonus+=statmod(self.cstats[skill[1]])
                if skill[0][:-4] in self.experts: 
                    bonus+=2*self.cstats['PRO']
                    training+='**'
                elif skill[0][:-4] in self.skills: 
                    bonus+=self.cstats['PRO']
                    training+='*'
                elif 'JACK' in [feat.name[:4].upper() for feat in self.featurelist]: bonus+=self.cstats['PRO']//2
            else:
                bonus=self.cstats[skill[0]]
                bonus+=statmod(self.cstats[skill[1]])
                if skill[0] in self.experts: 
                    bonus+=2*self.cstats['PRO']
                    training+='**'
                elif skill[0] in self.skills: 
                    bonus+=self.cstats['PRO']
                    training+='*'
                elif 'JACK' in [feat.name[:4].upper() for feat in self.featurelist]: bonus+=self.cstats['PRO']//2
            self.cstats[skill[0]+'bonus']=bonus #save bonus for easier lookup
        if self.shown:
            for ab in self.abilitylist: ab.update()
            for equip in self.equiplist: equip.update()
        self.gui.update()
    def rest(self,resttype):
        if resttype=='LR': resttype=['LR','SR']
        else: resttype=[resttype]
        for j in resttype:
            for i in self.abilitylist: i.rest(j.upper())
            if j=='LR': 
                self.stats['TEMPHP']=0
                self.stats['HP']=self.stats['MAXHP'] 
        self.update()
    #     #spells
    #     self.spelleditframe=VerticalScrolledFrame(self.roottabs)
    #     self.spelleditframe.pack(expand=True,fill=BOTH)
    #     self.roottabs.add(self.spelleditframe,text='Spells')
    #     for num,key in enumerate(['Index','Display Name','Lookup Name (optional)','Level','Additional Description','Remove?']):
    #         Label(self.spelleditframe.viewPort, text=f"{key}").grid(row=0,column=num,sticky=N+S+E+W)
    #     self.allspelldata=[]
    #     self.spelleditframe.viewPort.grid_columnconfigure(4, weight=1)
    #     for num,i in enumerate(self.spellbooklist+[spell({'NAME':'','LEVEL':0,'LOOKUP':'','TEXT':'','PREP':0})]*50): 
    #         spelldata={}
    #         spelldata['index']=Entry(self.spelleditframe.viewPort,font=f'Times {self.fontsize}',width=5)
    #         spelldata['index'].insert(0,str(num+1))
    #         spelldata['index'].grid(row=num+1,column=0,sticky=N+S+E+W)
    #         spelldata['name']=Entry(self.spelleditframe.viewPort,font=f'Times {self.fontsize}')
    #         spelldata['name'].insert(0,i.name)
    #         spelldata['name'].grid(row=num+1,column=1,sticky=N+S+E+W)
    #         spelldata['lookup']=searchComboBox(self.spelleditframe.viewPort,font=f'Times {self.fontsize}')
    #         spelldata['lookup'].index=num
    #         spelldata['lookup'].insert(0,i.lookup)
    #         spelldata['lookup']['values']=['']+sorted([name for name in masterspellsdict])
    #         spelldata['lookup'].bind('<KeyRelease>',searchspells)
    #         spelldata['lookup'].grid(row=num+1,column=2,sticky=N+S+E+W)
    #         spelldata['level']=ttk.Combobox(self.spelleditframe.viewPort,font=f'Times {self.fontsize}',width=1)
    #         spelldata['level'].insert(0,str(i.level))
    #         spelldata['level']['values']=[str(i) for i in range(10)]
    #         spelldata['level'].grid(row=num+1,column=3,sticky=N+S+E+W)
    #         spelldata['text']=Entry(self.spelleditframe.viewPort,font=f'Times {self.fontsize}')
    #         spelldata['text'].insert(0,i.text)
    #         spelldata['text'].grid(row=num+1,column=4,sticky=N+S+E+W)
    #         spelldata['delete']=IntVar()
    #         temp=Checkbutton(self.spelleditframe.viewPort,variable=spelldata['delete'],onvalue=1,offvalue=0)
    #         temp.grid(row=num+1,column=5,sticky=N+S+E+W)
    #         spelldata['prep']=i.prep
    #         self.allspelldata.append(spelldata)
    #     setallcolor(root,self.color,self.fontcolor)
    #     #features
    #     self.featureeditframe=VerticalScrolledFrame(self.roottabs)
    #     self.featureeditframe.pack(expand=True,fill=BOTH)
    #     self.roottabs.add(self.featureeditframe,text='Features')
    #     for num,key in enumerate(['Index','Name','Mods','Text','Remove?']):
    #         Label(self.featureeditframe.viewPort, text=f"{key}").grid(row=0,column=num,sticky=N+S+E+W)
    #     self.allfeaturedata=[]
    #     # self.featureeditframe.viewPort.grid_columnconfigure(4, weight=1)
    #     for num,i in enumerate(self.featurelist+[feature({'NAME':'','MODS':'','TEXT':''},self)]*50): 
    #         featuredata={}
    #         featuredata['index']=Entry(self.featureeditframe.viewPort,font=f'Times {self.fontsize}',width=5)
    #         featuredata['index'].insert(0,str(num+1))
    #         featuredata['index'].grid(row=num+1,column=0,sticky=N+S+E+W)
    #         featuredata['name']=Entry(self.featureeditframe.viewPort,font=f'Times {self.fontsize}')
    #         featuredata['name'].insert(0,i.name)
    #         featuredata['name'].grid(row=num+1,column=1,sticky=N+S+E+W)
    #         tempstring=''
    #         for mod in i.mods: tempstring+=f"{mod[0]}:{mod[1]:+d},"
    #         featuredata['mods']=Entry(self.featureeditframe.viewPort,font=f'Times {self.fontsize}')
    #         featuredata['mods'].insert(0,tempstring[:-1])
    #         featuredata['mods'].grid(row=num+1,column=2,sticky=N+S+E+W)
    #         featuredata['text']=Entry(self.featureeditframe.viewPort,font=f'Times {self.fontsize}')
    #         featuredata['text'].insert(0,i.text)
    #         featuredata['text'].grid(row=num+1,column=3,sticky=N+S+E+W)
    #         featuredata['delete']=IntVar()
    #         temp=Checkbutton(self.featureeditframe.viewPort,variable=featuredata['delete'],onvalue=1,offvalue=0)
    #         temp.grid(row=num+1,column=4,sticky=N+S+E+W)
    #         self.allfeaturedata.append(featuredata)
    #     setallcolor(root,self.color,self.fontcolor)
    # def acceptedit(self):
    #     for num,i in enumerate(self.allspelldata): 
    #         try: self.allspelldata[num]['index']=float(self.allspelldata[num]['index'].get())
    #         except: self.allspelldata[num]['index']=1e9
    #     self.allspelldata=sorted(self.allspelldata,key=lambda x:x['index'])
    #     self.spellbooklist=[spell({'NAME':data['name'].get(),'LEVEL':data['level'].get(),'LOOKUP':data['lookup'].get(),'TEXT':data['text'].get().replace('\n','\\'),'PREP':data['prep']}) for data in self.allspelldata if (data['delete'].get()!=1 and len(data['name'].get())>0)]
    #     for num,i in enumerate(self.allfeaturedata): 
    #         try: self.allfeaturedata[num]['index']=float(self.allfeaturedata[num]['index'].get())
    #         except: self.allfeaturedata[num]['index']=1e9
    #     self.allfeaturedata=sorted(self.allfeaturedata,key=lambda x:x['index'])
    #     self.featurelist=[feature({'NAME':data['name'].get(),'MODS':data['mods'].get(),'TEXT':data['text'].get().replace('\n','\\')},self) for data in self.allfeaturedata if (data['delete'].get()!=1 and len(data['name'].get())>0)]
    #     for item in root.winfo_children(): item.destroy()
    #     self.show()
    #     self.update()
    # def canceledit(self):
    #     for item in root.winfo_children(): item.destroy()
    #     self.show()
    #     self.update()
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
            for bonusfeature in self.bonusfeatures: file.write(f'{bonusfeature}\n')
            file.write('\n%%ATTRIBUTES\n')
            for ability in self.abilitylist: file.write(ability.save())
            for equip in self.equiplist: file.write(equip.save())
            for spell in self.spellbooklist: file.write(spell.save())
            for feature in self.featurelist: file.write(feature.save())
            file.write('%%BACKPACK\n')
            for item in self.backpacklist:file.write(item.save())
            file.write(f"\n%%NOTES\n{self.gui.notes.toPlainText()}")
            file.write(f"%%VERSION\n{version}")

class NoWheelSpinBox(QSpinBox):
    def wheelEvent(self, event): event.ignore()

class MainWindow(QMainWindow):
    def __init__(self,c):
        super().__init__()
        self.c=c
        self.setFont(c.fontsize)
        self.resize(int(700*(c.fontsize/9)),int(800*(c.fontsize/9))) #700 is a guess for width, 800 perfectly fits all skills
        # self.resize(700,800)
        self.setWindowTitle('Py5e')

        self.quitAllowed=False

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

        self.cPage=QWidget()
        self.tabs.addTab(self.cPage,'Character')
        self.cLayout=QVBoxLayout()
        self.cPage.setLayout(self.cLayout)
        
        self.titleBar=QHBoxLayout()
        self.cLayout.addLayout(self.titleBar)
        self.displayNameClass=QLabel("Name and Class Go Here",alignment=Qt.AlignmentFlag.AlignCenter|Qt.AlignmentFlag.AlignTop)
        self.titleBar.addWidget(self.displayNameClass)
        self.displayHP=QPushButton('HP: ?/?',clicked=self.damage)
        self.titleBar.addWidget(self.displayHP)
        self.displayTempHP=QPushButton('?',clicked=self.addtemphp)
        self.titleBar.addWidget(self.displayTempHP)
        self.displayACSpeed=QLabel("AC: ? Speed: ?")
        self.titleBar.addWidget(self.displayACSpeed)
        self.titleBar.addStretch()

        self.cBody=QWidget()
        self.cScroll=QScrollArea()
        self.cScroll.setWidget(self.cBody)
        self.cScroll.setWidgetResizable(True)
        self.cScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.cScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.cLayout.addWidget(self.cScroll)
        self.cBodyLayout=QHBoxLayout()
        self.cBody.setLayout(self.cBodyLayout)

        self.cStatsLayout=QVBoxLayout()
        self.cBodyLayout.addStretch() #left side stretch
        self.cBodyLayout.addLayout(self.cStatsLayout)
        self.displayStats={}
        for stat in ['Proficiency','STR','DEX','CON','INT','WIS','CHA']:
            self.displayStats[stat]=QLabel(f"{stat}: ?",alignment=Qt.AlignmentFlag.AlignCenter)
            self.cStatsLayout.addWidget(self.displayStats[stat])
        self.cStatsLayout.addWidget(QFrame(frameShape=QFrame.HLine))
        self.cStatsLayout.addWidget(QLabel('Skills:'),alignment=Qt.AlignmentFlag.AlignCenter)
        for stat in [i[0] for i in self.c.allskills]:
            self.displayStats[stat]=QLabel(f"{stat}: ?",alignment=Qt.AlignmentFlag.AlignRight)
            self.cStatsLayout.addWidget(self.displayStats[stat])
        self.cStatsLayout.addStretch()
        
        self.cMiddleLayout=QVBoxLayout()
        self.cBodyLayout.addWidget(QFrame(frameShape=QFrame.VLine))
        self.cBodyLayout.addLayout(self.cMiddleLayout)
        self.cBodyLayout.addWidget(QFrame(frameShape=QFrame.VLine))

        self.cAbilityLayout=QVBoxLayout()
        # self.cAbilityLayout.setSpacing(0)
        self.cMiddleLayout.addLayout(self.cAbilityLayout)
        self.cMiddleLayout.addWidget(QFrame(frameShape=QFrame.HLine))
        
        self.cAbilityLayout.addWidget(QLabel('Abilities:',alignment=Qt.AlignmentFlag.AlignCenter))
        self.cAbilityLayout.addStretch()

        self.cEquipLayout=QVBoxLayout()
        # self.cEquipLayout.setSpacing(0)
        self.cMiddleLayout.addLayout(self.cEquipLayout)
        self.cEquipLayout.addWidget(QLabel('Equipment:',alignment=Qt.AlignmentFlag.AlignCenter))
        self.cMiddleLayout.addStretch()
        
        self.featurecolumnLayout=QVBoxLayout()
        self.cBodyLayout.addLayout(self.featurecolumnLayout)
        self.featureLayout=QVBoxLayout()
        self.featurecolumnLayout.addLayout(self.featureLayout)
        self.cBodyLayout.addStretch() #right side stretch
        self.featurecolumnLayout.addWidget(QFrame(frameShape=QFrame.HLine))
        self.featureLayout.addWidget(QLabel('Features:',alignment=Qt.AlignmentFlag.AlignCenter))
        self.langLayout=QVBoxLayout()
        self.featurecolumnLayout.addLayout(self.langLayout)
        self.featurecolumnLayout.addWidget(QFrame(frameShape=QFrame.HLine))
        self.langLayout.addWidget(QLabel('Languages:',alignment=Qt.AlignmentFlag.AlignCenter))
        for lang in self.c.langs: self.langLayout.addWidget(QLabel(lang))
        self.profLayout=QVBoxLayout()
        self.featurecolumnLayout.addLayout(self.profLayout)
        self.profLayout.addWidget(QLabel('Proficiencies:',alignment=Qt.AlignmentFlag.AlignCenter))
        for prof in self.c.profs: self.profLayout.addWidget(QLabel(prof))
        self.profLayout.addStretch()
        self.featurecolumnLayout.addStretch()
                
        self.spellsPage=QWidget()
        self.tabs.addTab(self.spellsPage,'Spells')
        self.spellsLayout=QVBoxLayout()
        self.spellsPage.setLayout(self.spellsLayout)
        self.spellsHeader=QLabel('Casting ability: ?, Save DC: ?, Spell Attack Bonus: ?',alignment=Qt.AlignmentFlag.AlignCenter)
        self.spellsLayout.addWidget(self.spellsHeader)

        self.spellsBody=QWidget()
        self.spellsScroll=QScrollArea()
        self.spellsScroll.setWidget(self.spellsBody)
        self.spellsScroll.setWidgetResizable(True)
        self.spellsScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.spellsScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.spellsLayout.addWidget(self.spellsScroll)
        self.spellsBodyLayout=QHBoxLayout()
        self.spellsBody.setLayout(self.spellsBodyLayout)
        self.spellsBodyLayout.addStretch()
        self.spellsLLayout=QVBoxLayout()
        self.spellsBodyLayout.addLayout(self.spellsLLayout)
        self.spellsBodyLayout.addWidget(QFrame(frameShape=QFrame.VLine))
        self.spellsCLayout=QVBoxLayout()
        self.spellsBodyLayout.addLayout(self.spellsCLayout)
        self.spellsBodyLayout.addWidget(QFrame(frameShape=QFrame.VLine))
        self.spellsRLayout=QVBoxLayout()
        self.spellsBodyLayout.addLayout(self.spellsRLayout)
        self.spellsBodyLayout.addStretch()

        self.spellLVLLayouts={str(i):QVBoxLayout() for i in range(10)}
        self.spellsLLayout.addLayout(self.spellLVLLayouts['0'])
        self.spellsLLayout.addWidget(QFrame(frameShape=QFrame.HLine))
        self.spellsLLayout.addLayout(self.spellLVLLayouts['1'])
        self.spellsLLayout.addStretch()
        self.spellsCLayout.addLayout(self.spellLVLLayouts['2'])
        self.spellsCLayout.addWidget(QFrame(frameShape=QFrame.HLine))
        self.spellsCLayout.addLayout(self.spellLVLLayouts['3'])
        self.spellsCLayout.addWidget(QFrame(frameShape=QFrame.HLine))
        self.spellsCLayout.addLayout(self.spellLVLLayouts['4'])
        self.spellsCLayout.addStretch()
        self.spellsRLayout.addLayout(self.spellLVLLayouts['5'])
        self.spellsRLayout.addWidget(QFrame(frameShape=QFrame.HLine))
        self.spellsRLayout.addLayout(self.spellLVLLayouts['6'])
        self.spellsRLayout.addWidget(QFrame(frameShape=QFrame.HLine))
        self.spellsRLayout.addLayout(self.spellLVLLayouts['7'])
        self.spellsRLayout.addWidget(QFrame(frameShape=QFrame.HLine))
        self.spellsRLayout.addLayout(self.spellLVLLayouts['8'])
        self.spellsRLayout.addWidget(QFrame(frameShape=QFrame.HLine))
        self.spellsRLayout.addLayout(self.spellLVLLayouts['9'])
        self.spellsRLayout.addStretch()

        self.bpPage=QWidget()
        self.tabs.addTab(self.bpPage,'Inventory')
        self.bpLayout=QVBoxLayout()
        self.bpPage.setLayout(self.bpLayout)
        self.bpBody=QWidget()
        self.bpScroll=QScrollArea()
        self.bpScroll.setWidget(self.bpBody)
        self.bpScroll.setWidgetResizable(True)
        self.bpScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.bpScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.bpLayout.addWidget(self.bpScroll)
        self.itemLayout=QVBoxLayout()
        self.bpBody.setLayout(self.itemLayout)
        self.itemLayout.addStretch()

        self.notesPage=QWidget()
        self.tabs.addTab(self.notesPage,'Notes')
        self.notesLayout=QVBoxLayout()
        self.notesPage.setLayout(self.notesLayout)
        self.notes=QTextEdit()
        self.notesLayout.addWidget(self.notes)

    def showContent(self):
        for feat in self.c.featurelist: feat.show()
        for ability in self.c.abilitylist: ability.show()
        for equip in self.c.equiplist: equip.show()
        for item in self.c.backpacklist: item.show()
        if len([i for i in self.c.spellbooklist if i.level==0])>0: self.spellLVLLayouts['0'].addWidget(QLabel('Cantrips',alignment=Qt.AlignmentFlag.AlignCenter))
        for spell in self.c.spellbooklist: spell.show()
        self.notes.setText(self.c.notes)
    def update(self):
        self.setWindowTitle('*'+self.c.filepath.split('/')[-1].split('\\')[-1])
        self.displayNameClass.setText(f"{self.c.name}\n{self.c.classes}")
        self.displayHP.setText(f"HP: {self.c.stats['HP']}/{self.c.stats['MAXHP']}")
        if self.c.stats['TEMPHP']>0: self.displayTempHP.setText(f"{self.c.stats['TEMPHP']:+d}")
        else: self.displayTempHP.setText("")
        self.displayACSpeed.setText(f"AC: {self.c.cstats['AC']+statmod(self.c.cstats['DEX'])}, Speed: {self.c.cstats['SPEED']}ft")
        self.displayStats['Proficiency'].setText(f"Proficiency: {self.c.cstats['PRO']}")
        for stat in ['STR','DEX','CON','INT','WIS','CHA']:
            savebonus=statmod(self.c.cstats[stat])
            if stat in self.c.savethrows: savebonus+=self.c.cstats['PRO']
            self.displayStats[stat].setText(f"{stat}: {self.c.cstats[stat]} ({statmod(self.c.cstats[stat]):+d}) ({savebonus:+d})")
        for skill in self.c.allskills:
            training=''
            if '(P)' in skill[0]:
                bonus=self.c.cstats[skill[0]]+self.c.cstats[skill[0][:-4]]
                bonus+=statmod(self.c.cstats[skill[1]])
                if skill[0][:-4] in self.c.experts: 
                    bonus+=2*self.c.cstats['PRO']
                    training+='**'
                elif skill[0][:-4] in self.c.skills: 
                    bonus+=self.c.cstats['PRO']
                    training+='*'
                elif 'JACK' in [feat.name[:4].upper() for feat in self.c.featurelist]: bonus+=self.c.cstats['PRO']//2
            else:
                bonus=self.c.cstats[skill[0]]
                bonus+=statmod(self.c.cstats[skill[1]])
                if skill[0] in self.c.experts: 
                    bonus+=2*self.c.cstats['PRO']
                    training+='**'
                elif skill[0] in self.c.skills: 
                    bonus+=self.c.cstats['PRO']
                    training+='*'
                elif 'JACK' in [feat.name[:4].upper() for feat in self.c.featurelist]: bonus+=self.c.cstats['PRO']//2
            self.displayStats[skill[0]].setText(f"{training}{skill[0]}: {bonus:+d}")
            self.c.cstats[skill[0]+'bonus']=bonus #save bonus for easier lookup
        if self.c.caststat!='': self.spellsHeader.setText(f"Casting ability: {statmod(self.c.cstats[self.c.caststat])+self.c.cstats['PRO']:+d}, Save DC: {8+statmod(self.c.cstats[self.c.caststat])+self.c.cstats['PRO']:+d}, Spell Attack Bonus: {statmod(self.c.cstats[self.c.caststat])+self.c.cstats['PRO']:+d}")
        #remove and reconstruct land and profs in case of new ones added during editing
        while self.langLayout.count(): 
            item=self.langLayout.takeAt(0)
            widget=item.widget()
            if widget is not None: widget.deleteLater()
        self.langLayout.addWidget(QLabel('Languages:',alignment=Qt.AlignmentFlag.AlignCenter))
        for lang in self.c.langs: self.langLayout.addWidget(QLabel(lang))
        while self.profLayout.count():
            item=self.profLayout.takeAt(0)
            widget=item.widget()
            if widget is not None: widget.deleteLater()
        self.profLayout.addWidget(QLabel('Proficiencies:',alignment=Qt.AlignmentFlag.AlignCenter))
        for prof in self.c.profs: self.profLayout.addWidget(QLabel(prof))
        self.profLayout.addStretch()
    def rest(self,restType):
        self.c.rest(restType)
    def saveAs(self):
        filepath,selectedfilter=QFileDialog.getSaveFileName(self,"Save File","","Py5e Files (*.5e);;All Files (*)")
        self.c.save(filepath)
    def save(self):
        if self.c.filepath is not None: self.c.save(self.c.filepath)
        else: self.saveAs()
    def save_and_quit(self):
        self.save()
        self.quitAllowed=True
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
    def damage(self):
        value,ok=QInputDialog.getInt(self,'Input','Enter HP Change:')
        if value<0:
            if abs(value)<self.c.stats['TEMPHP']: self.c.stats['TEMPHP']+=value
            else: 
                self.c.stats['HP']+=self.c.stats['TEMPHP']+value
                self.c.stats['TEMPHP']=0
            self.c.update()
        if value>0:  
            self.c.stats['HP']+=value
            self.c.update()
    def addtemphp(self):
        value,ok=QInputDialog.getInt(self,'Input','Enter Temp HP:',minValue=0)
        if value>0:
            self.c.stats['TEMPHP']=value
            self.c.update()

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
        dialog=getEquip(self.c)
        if dialog.exec()==QDialog.Accepted:
            self.c.equiplist.append(equipment(dialog.getData(),self.c))
            self.c.equiplist[-1].show()
            self.c.update()
    def newSpell(self):
        dialog=getSpell()
        if dialog.exec()==QDialog.Accepted:
            self.c.spellbooklist.append(spell(dialog.getData(),self.c))
            self.c.spellbooklist[-1].show()
            self.c.update()
    def editCharacter(self):
        dialog=getStats(self.c)
        if dialog.exec()==QDialog.Accepted: dialog.getData()
    def editFont(self):
        fontSize,ok=QInputDialog.getInt(self,"Set Font Size",'Enter Font Size',value=QApplication.font().pointSize(),minValue=1,maxValue=200)
        if ok: 
            self.setFont(fontSize)
            c.fontsize=fontSize
            self.c.update()
    def setFont(self,fontsize):
        font=QApplication.font()
        font.setPointSize(fontsize)
        QApplication.setFont(font)
        # temp=self.menuBar()
        # temp.setFont(font)
        # for menu in temp.findChildren(QWidget): menu.setFont(font)

class getStats(QDialog):
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

class getSpell(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('New Spell')
        mainLayout=QVBoxLayout()
        self.setLayout(mainLayout)
        formLayout=QFormLayout()
        self.name=QLineEdit()
        self.lookup=QComboBox()
        self.lookup.addItems(['']+sorted([i for i in masterspellsdict]))
        self.level=NoWheelSpinBox(minimum=0,maximum=9,value=0)
        self.description=QTextEdit()
        formLayout.addRow('Display Name:',self.name)
        formLayout.addRow('Level',self.level)
        formLayout.addRow('Lookup Spell',self.lookup)
        formLayout.addRow('Description',self.description)
        mainLayout.addLayout(formLayout)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.verifyData)
        buttons.rejected.connect(self.reject)
        mainLayout.addWidget(buttons)
    def verifyData(self):
        if len(self.name.text())<1: 
            QMessageBox.warning(self,'Invalid Name','No display name provided.')
            return 
        self.accept()
    def getData(self):
        return {'NAME':self.name.text().strip(),'LEVEL':self.level.value(),'LOOKUP':self.lookup.currentText(),'TEXT':self.description.toPlainText().strip()}

class getFeature(QDialog):
    def __init__(self):
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

class getItem(QDialog):
    def __init__(self):
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

class getAbility(QDialog):
    def __init__(self,c):
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
        formLayout.addRow('Spellslot?',self.spellslot)
        formLayout.addRow('Description:',self.description)
        mainLayout.addLayout(formLayout)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.verifyData)
        buttons.rejected.connect(self.reject)
        mainLayout.addWidget(buttons)
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
        return {'NAME':self.name.text().strip(),'MAX':self.name.text().strip(),'REST':self.resttype.currentData(),'SPELLSLOT':'y' if self.spellslot.isChecked() else 'n','TEXT':self.description.toPlainText().strip()}

class getEquip(QDialog):
    def __init__(self,c):
        super().__init__()
        self.c=c
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
    
class feature():
    def __init__(self,featdict,c):
        self.c=c
        if 'NAME' in featdict: self.name=featdict['NAME']
        else: self.name='?'
        if 'MODS' in featdict: 
            if featdict['MODS']=='':self.mods=[]
            else:                 
                self.mods=featdict['MODS']
                self.mods=[mod.strip().split(':') for mod in self.mods.split(',')]
                for mod in self.mods: mod[1]=int(mod[1])
        else: self.mods=[]
        if 'TEXT' in featdict: 
            self.text=featdict['TEXT'].replace('\n','\\')
            self.description=featdict['TEXT'].replace('\\','\n')
        else: 
            self.description='(No Description)'
            self.text=''
        for mod in self.mods: self.c.cstats[mod[0]]+=mod[1]
    def show(self):
        self.gui=featureWidget(self)
    def delete(self):
        self.c.featurelist.remove(self)
        self.disable(c)
        self.c.update()
    def disable(self,c):
        for mod in self.mods: c.cstats[mod[0]]-=mod[1]
        c.update()
    def save(self):
        tempstring=f"%FEATURE\nNAME={self.name}"
        if len(self.mods)>0: 
            tempstring+="\nMODS="
            for mod in self.mods: tempstring+=f"{mod[0]}:{mod[1]:+d}, "
            tempstring=tempstring[:-2]
        return tempstring+f'\nTEXT={self.text}\n\n'

class featureWidget(QWidget):
    def __init__(self,feat):
        super().__init__()
        self.feat=feat
        self.layout=QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.delButton=QPushButton(text='\u00d7',clicked=self.delete)
        self.delButton.setFixedWidth(self.delButton.sizeHint().height())
        self.layout.addWidget(self.delButton)
        self.layout.addWidget(QPushButton(text=self.feat.name,clicked=self.showinfo))
        self.feat.c.gui.featureLayout.insertWidget(self.feat.c.gui.featureLayout.count(),self)
    def delete(self):
        self.feat.c.gui.featureLayout.removeWidget(self)
        self.setParent(None)
        self.deleteLater()
        self.feat.delete()
    def showinfo(self):
        self.dialog=PopupDialog(self.feat.name,self.feat.description.replace('\\','\n'))
        self.dialog.show()
        
class PopupDialog(QDialog):
    def __init__(self,title,text):
        super().__init__()
        self.setWindowTitle(title)
        layout=QVBoxLayout(self)
        label=QLabel(text,alignment=Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)

class ability():
    def __init__(self,abilitydict,c):
        self.c=c
        if 'NAME' in abilitydict: self.name=abilitydict['NAME']
        else: self.name='(N/A)'
        if 'MAX' in abilitydict:
            self.maxnumraw=abilitydict['MAX']
            try: self.maxnum=int(abilitydict['MAX'])
            except ValueError: self.maxnum=max(1,self.c.cstats[abilitydict['MAX']+'bonus']) if abilitydict['MAX'] in [i[0] for i in self.c.allskills] else (max(1,statmod(self.c.cstats[abilitydict['MAX']])) if abilitydict['MAX'] in ['STR','DEX','CON','INT','WIS','CHA'] else (self.c.cstats[abilitydict['MAX']] if abilitydict['MAX']=='PRO' else 0))
        else: 
            self.maxnum=0
            self.maxnumraw=0
        if 'REMAINING' in abilitydict: self.numleft=int(abilitydict['REMAINING'])
        else: self.numleft=0
        if 'REST' in abilitydict: self.resttype=abilitydict['REST']
        else: self.resttype='none'
        if 'SPELLSLOT' in abilitydict: 
            if 'y' in abilitydict['SPELLSLOT'].lower(): self.spellslot=True
            else: self.spellslot=False
        else: self.spellslot=False
        if 'TEXT' in abilitydict: 
            self.text=abilitydict['TEXT'].replace('\n','\\')
            self.description=abilitydict['TEXT'].replace('\\','\n')
        else: 
            self.description='(No Description)'
            self.text=''
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
        if self.spellslot: self.spellgui.delete()
        self.gui.delete()
        self.c.abilitylist.remove(self)
    def save(self):
        if self.spellslot: return f"%ABILITY\nNAME={self.name}\nMAX={self.maxnum}\nREMAINING={self.numleft}\nREST={self.resttype}\nSPELLSLOT=YES\nTEXT={self.text}\n\n"
        else: return f"%ABILITY\nNAME={self.name}\nMAX={self.maxnumraw}\nREMAINING={self.numleft}\nREST={self.resttype}\nSPELLSLOT=NO\nTEXT={self.text}\n\n"

class abilityWidget(QWidget):
    def __init__(self,ability,spellslot=False):
        super().__init__()
        self.ability=ability
        self.layout=QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self.unuseButton=QPushButton(text='+',clicked=self.unuse)
        self.unuseButton.setFixedWidth(self.unuseButton.sizeHint().height())
        self.layout.addWidget(self.unuseButton)
        if spellslot: 
            # self.useButton.setFlat(True)
            # self.uesButton.setStyleSheet("border: none;")# background: none;")
            self.useButton=QPushButton(text='?',clicked=self.use)
            self.layout.addWidget(self.useButton)
            self.guiLocation=self.ability.c.gui.spellLVLLayouts[ability.name[0]]
            self.guiLocation.insertWidget(0,self)
        else: 
            self.useButton=QPushButton(text='-',clicked=self.use)
            self.useButton.setFixedWidth(self.unuseButton.sizeHint().height())
            self.infoButton=QPushButton(text='?',clicked=self.showinfo)
            self.delButton=QPushButton(text='\u00d7',clicked=self.senddelete)
            self.delButton.setFixedWidth(self.delButton.sizeHint().height())
            self.layout.addWidget(self.useButton)
            self.layout.addWidget(self.infoButton)
            self.layout.addWidget(self.delButton)
            
            self.guiLocation=self.ability.c.gui.cAbilityLayout
            self.guiLocation.insertWidget(self.guiLocation.count()-1,self)
    def use(self):
        self.ability.use()
    def unuse(self):
        self.ability.unuse()
    def senddelete(self):
        self.ability.delete()
    def showinfo(self):
        self.dialog=PopupDialog(self.ability.name,self.ability.description.replace('\\','\n'))
        self.dialog.show()
    def delete(self):
        self.guiLocation.removeWidget(self)
        self.setParent(None)
        self.deleteLater()
    
class equipment():
    def __init__(self,equipdict,c):
        self.c=c
        if 'NAME' in equipdict: self.name=equipdict['NAME']
        else: self.name='?'
        if 'MODS' in equipdict: 
            self.mods=equipdict['MODS']
            self.mods=[mod.strip().split(':') for mod in self.mods.split(',')]
            for mod in self.mods: mod[1]=int(mod[1])
        else: self.mods=[]
        if 'HITDAMAGE' in equipdict: self.hitdamage=[int(equipdict['HITDAMAGE'].split()[0]),equipdict['HITDAMAGE'].split()[1]]
        else: self.hitdamage=[0,0]  
        if 'SCALING' in equipdict: self.scaling=equipdict['SCALING']
        else: self.scaling='no'   
        if 'EQUIPPED' in equipdict: 
            if equipdict['EQUIPPED'].strip().lower() in 'yes': self.equipped=True
            elif equipdict['EQUIPPED'].strip().lower() in 'no': self.equipped=False
        else: self.equipped=False   
        if 'PROF' in equipdict: 
            if equipdict['PROF'].strip().lower() in 'yes': self.prof=True
            elif equipdict['PROF'].strip().lower() in 'no': self.prof=False
        else: self.prof=False  
        if 'MAXDEX' in equipdict: self.maxdex=int(equipdict['MAXDEX'])
        else: self.maxdex=False
        if 'TEXT' in equipdict: 
            self.text=equipdict['TEXT'].replace('\n','\\')
            self.description=equipdict['TEXT'].replace('\\','\n')
        else: 
            self.description='(No Description)'
            self.text=''
        if self.equipped: 
            for mod in self.mods:
                if mod[0]=='AC' and type(self.maxdex)==int and (self.maxdex<statmod(self.c.cstats['DEX']) or self.maxdex==0): #heavy armor, maxdex==0 and negative dex mod is not counted
                    self.ACadded=mod[1]+self.maxdex-statmod(self.c.cstats['DEX']) #fix infinite AC exploit
                    c.cstats[mod[0]]+=self.ACadded
                elif mod[0]=='AC' and type(self.maxdex)==int:
                    self.ACadded=mod[1]
                    self.c.cstats[mod[0]]+=self.ACadded
                else: self.c.cstats[mod[0]]+=mod[1]
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
        if self.equipped: self.gui.togglebutton.setText('\u2611')
        else: self.gui.togglebutton.setText('\u2610')
        self.gui.infobutton.setText(tempstring)
        if upc: 
            self.c.update()
            self.update()
        if upe:
            for i in self.c.equiplist: i.update()
    def toggle(self):
        if self.equipped: 
            self.equipped=False
            for mod in self.mods:
                if mod[0]=='AC' and type(self.maxdex)==int and (self.maxdex<statmod(self.c.cstats['DEX']) or self.maxdex==0): #heavy armor, maxdex==0 and negative dex mod is not counted
                    self.c.cstats[mod[0]]-=self.ACadded #fix infinite AC exploit
                elif mod[0]=='AC' and type(self.maxdex)==int: self.c.cstats[mod[0]]-=self.ACadded
                else: self.c.cstats[mod[0]]-=mod[1]
        else: 
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

class equipWidget(QWidget):
    def __init__(self,equip):
        super().__init__()
        self.equip=equip
        self.layout=QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.togglebutton=QPushButton(text='[?]',clicked=self.toggle)
        self.togglebutton.setFixedWidth(self.togglebutton.sizeHint().height())
        self.layout.addWidget(self.togglebutton)
        self.infobutton=QPushButton(text=self.equip.name,clicked=self.showinfo)
        self.layout.addWidget(self.infobutton)
        self.delButton=QPushButton(text='\u00d7',clicked=self.delete)
        self.delButton.setFixedWidth(self.delButton.sizeHint().height())
        self.layout.addWidget(self.delButton)
        self.equip.c.gui.cEquipLayout.insertWidget(self.equip.c.gui.cEquipLayout.count(),self)
    def delete(self):
        self.equip.c.gui.cEquipLayout.removeWidget(self)
        self.setParent(None)
        self.deleteLater()
        self.equip.delete()
    def toggle(self):
        self.equip.toggle()
    def showinfo(self):
        self.dialog=PopupDialog(self.equip.name,self.equip.description.replace('\\','\n'))
        self.dialog.show()

class item():
    def __init__(self,bpline,c):
        self.c=c
        self.quantity=int(bpline.split(':')[1])
        self.name=bpline.split(':')[0].strip()
        if len(bpline.split(':'))>2: 
            self.text=':'.join(bpline.split(':')[2:]).strip().replace('\n','\\')
            self.description=self.text.replace('\n','\\').strip()
            if len(self.description)==0: self.description='(No Description)'
        else: 
            self.text=''
            self.description='(No Description)'
    def show(self):
        self.gui=itemWidget(self)
    def delete(self):
        self.c.backpacklist.remove(self)
    def save(self):
        return f"{self.name}:{self.quantity}:{self.text}\n"
    
class itemWidget(QWidget):
    def __init__(self,item):
        super().__init__()
        self.item=item
        self.layout=QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self.quantity=NoWheelSpinBox(minimum=-2147483648,maximum=2147483647,value=self.item.quantity)
        self.quantity.valueChanged.connect(self.changeValue)
        self.quantity.setFixedWidth(self.quantity.sizeHint().height()*5)
        self.layout.addWidget(self.quantity)
        self.layout.addWidget(QPushButton(self.item.name,clicked=self.showinfo))
        self.delButton=QPushButton(text='\u00d7',clicked=self.delete)
        self.delButton.setFixedWidth(self.delButton.sizeHint().height())
        self.layout.addWidget(self.delButton)
        self.item.c.gui.itemLayout.insertWidget(self.item.c.gui.itemLayout.count()-1,self)
    def changeValue(self,value):
        self.item.quantity=value
    def showinfo(self):
        self.dialog=PopupDialog(self.item.name,self.item.description.replace('\\','\n'))
        self.dialog.show()
    def delete(self):
        self.item.c.gui.itemLayout.removeWidget(self)
        self.setParent(None)
        self.deleteLater()
        self.item.delete()

class spell():
    def __init__(self,spelldict,c):
        self.c=c
        if 'NAME' in spelldict: self.name=spelldict['NAME']
        else: self.name='?'
        if 'LOOKUP' in spelldict: 
            if spelldict['LOOKUP']=='1': self.lookup=spelldict['NAME'] #needed for the transtion to new code.
            elif spelldict['LOOKUP']==0: self.lookup=''
            else: self.lookup=spelldict['LOOKUP']
        else: self.lookup=spelldict['NAME']
        self.description=''
        if self.lookup in masterspellsdict:
            match=masterspellsdict[self.lookup]
            self.level=match['level']
            self.description+=f"{numsuffix(match['level'])}-level {schools[match['school']]}\n\nCasting Time: {match['time'][0]['number']} {match['time'][0]['unit']}\n\n"
            if match['range']['type']!='special': self.description+=f"Range: {match['range']['distance']['amount'] if match['range']['distance']['type']=='feet' else ''} {match['range']['distance']['type']}\n\n"
            self.description+=f"Components: {'V ' if 'v' in match['components'] else ''}{'S ' if 's' in match['components'] else ''}{'M: '+match['components']['m']['text'] if 'm' in match['components'] and 'text' in match['components']['m'] and isinstance(match['components']['m'],dict) else 'M: '+match['components']['m'] if 'm' in match['components'] else ''}\n\n"
            self.description+=f"Duration: {match['duration'][0]['type'] if match['duration'][0]['type']!='timed' else str(match['duration'][0]['duration']['amount'])+' '+match['duration'][0]['duration']['type']+(', Concentration' if 'concentration' in match['duration'][0] else '')}\n\n"
            self.description+='\n\n'.join([i for i in [entry if isinstance(entry,str) else '\n'.join(entry['items']) if (isinstance(entry,dict) and 'items' in entry) else '' for entry in match['entries']] if len(i)>0])+'\n\n'
            #self.description+='\n\n'.join([entry for entry in match['entries'] if isinstance(entry,str)  else '\n'.join(entry['items']) if (isinstance(entry,dict) and 'items' in entry)])+'\n\n'
            if 'entriesHigherLevel' in match: self.description+=match['entriesHigherLevel'][0]['name']+': '+match['entriesHigherLevel'][0]['entries'][0]+'\n\n'
            for badchar in ['}','{','(',')']: self.description=self.description.replace(badchar,'')
            self.description=" ".join([word for word in self.description.split(' ') if '@' not in word])
            self.description=" ".join([word.split('|')[-1] for word in self.description.split(' ')])
        else:
            if 'LEVEL' in spelldict: 
                try: self.level=int(spelldict['LEVEL'])
                except ValueError: self.level=0
            else: self.level=0
        if 'PREP' in spelldict: self.prep=bool(int(spelldict['PREP']))
        else: self.prep=False
        if 'TEXT' in spelldict: 
            self.text=spelldict['TEXT'].replace('\n','\\')
            self.description+=spelldict['TEXT'].replace('\\','\n') 
        else: self.text=''
    def update(self):
        if not self.prep: self.gui.togglebutton.setText('\u2610')
        else: self.gui.togglebutton.setText('\u2611')
    def toggle(self):
        if self.prep: self.prep=False
        else: self.prep=True
        self.update()
    def show(self):
        self.gui=spellWidget(self)
        self.update()
    def save(self):
        return f"%SPELL\nNAME={self.name}\nLOOKUP={self.lookup}\nLEVEL={self.level}\nPREP={int(self.prep)}\nTEXT={self.text}\n\n"

class spellWidget(QWidget):
    def __init__(self,spell):
        super().__init__()
        self.spell=spell
        self.layout=QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self.togglebutton=QPushButton(text='[?]',clicked=self.toggle)
        self.togglebutton.setFixedWidth(self.togglebutton.sizeHint().height())
        self.layout.addWidget(self.togglebutton)
        self.layout.addWidget(QPushButton(text=self.spell.name,clicked=self.showinfo))
        # self.delButton=QPushButton(text='\u00d7',clicked=self.delete)
        # self.delButton.setFixedWidth(self.delButton.sizeHint().height())
        # self.layout.addWidget(self.delButton)
        self.spell.c.gui.spellLVLLayouts[(str(self.spell.level))].insertWidget(self.spell.c.gui.spellLVLLayouts[(str(self.spell.level))].count(),self)
    # def delete(self):
    #     self.spell.c.gui.spellsCLayout.removeWidget(self)
    #     self.setParent(None)
    #     self.deleteLater()
    #     # self.spell.delete()
    def toggle(self):
        self.spell.toggle()
    def showinfo(self):
        self.dialog=PopupDialog(self.spell.name,self.spell.description.replace('\\','\n'))
        self.dialog.show()

def numsuffix(num):
    if int(num)==1: return f'{num}st'
    elif int(num)==2: return f'{num}nd'
    elif int(num)==3: return f'{num}rd'
    else: return f'{num}th'

def statmod(stat):
    return int((stat-10)//2)

def rgb2hex(rgb):
    r, g, b = rgb[0],rgb[1],rgb[2]
    return f'#{r:02x}{g:02x}{b:02x}'

color1=[236,230,220]
fcolor1=[0,0,0]

#load master spells dictionary
masterspellsdict={}
for spellfile in glob('5etools*/data/spells/spells*.json'):
    with open(spellfile) as temp:
        data=json.load(temp)
        for rawspell in data['spell']:
            masterspellsdict[rawspell['name']]=rawspell
schools={'V':'evocation','N':'necromancy','T':'transmutation','I':'illusion','E':'enchantment','D':'divination','C':'conjuration','A':'abjuration'}

welcomemessage=False

class UpdateWindow(QMainWindow):
    def __init__(self,latest):
        QMainWindow.__init__(self)
        self.setWindowTitle("Py5e Updater")
        layout=QVBoxLayout()
        message=QLabel(f'Latest update ({version} \u2192 {latest}) downloaded. Please exit and relaunch.')
        layout.addWidget(message)
        sublayout=QHBoxLayout()
        layout.addLayout(sublayout)
        # Window dimensions
        # geometry = self.screen().availableGeometry()
        # self.resize(geometry.width() * 0.3, geometry.height() * 0.6)
        quitbutton = QPushButton("Exit",clicked=self.fullquit)
        sublayout.addWidget(quitbutton)
        useoldbutton = QPushButton("Launch Old Version",clicked=self.close)
        sublayout.addWidget(useoldbutton)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    def fullquit(self):
        self.close()
        sys.exit()


def updatecheck():
    #check for updates
    try:
        latest=BeautifulSoup(requests.get("https://github.com/AT1555/Py5e/releases/latest").content,features="html.parser").title.string.split(' ')[1]
        if version!=latest:
            open(getcwd()+f'\\Py5e_{latest}.exe','wb').write(requests.get(f'https://github.com/AT1555/Py5e/releases/download/{latest}/Py5e_{latest}.exe',allow_redirects=True).content)
            app = QApplication()
            window = UpdateWindow(latest)
            window.show()
            app.exec()
            app.shutdown()
            return f'Py5e is out of date ({latest} available, current: {version}).'
        else: return f'Py5e is up to date ({version}).'
    except Exception: return 'Error when checking for updates.'

class CharacterSelectWindow(QMainWindow):
    def __init__(self,updatestatus):
        QMainWindow.__init__(self)
        self.setWindowTitle("Py5e")
        font=QApplication.font()
        font.setPointSize(10)
        QApplication.setFont(font)
        layout=QVBoxLayout()
        message=QLabel(f'Select a Character')
        layout.addWidget(message)
        layout.addWidget(QPushButton(text='New Character',clicked=self.close))
        FiveEfiles=glob('*.5e')
        if len(FiveEfiles)>0:
            for file in FiveEfiles:
                bkgcolor=[236,230,220]
                fontcolor=[0,0,0]
                try:
                    with open(file,'r') as openfile:
                        for line in openfile:
                            if line[:5]=='COLOR': bkgcolor=[int(i) for i in line.strip().split('=')[1].split(',')]
                            elif line[:9]=='FONTCOLOR': fontcolor=[int(i) for i in line.strip().split('=')[1].split(',')]
                except:
                    with open(file,'r',encoding='cp1252') as openfile:
                        for line in openfile:
                            if line[:5]=='COLOR': bkgcolor=[int(i) for i in line.strip().split('=')[1].split(',')]
                            elif line[:9]=='FONTCOLOR': fontcolor=[int(i) for i in line.strip().split('=')[1].split(',')]
                charbutton=QPushButton(text=file.split('/')[-1],clicked=lambda _, file=file: self.pickchar(infile=file))
                charbutton.setStyleSheet(f"background-color: {rgb2hex(bkgcolor)}; color: {rgb2hex(fontcolor)}")
                layout.addWidget(charbutton)
        widget=QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        global masterspellsdict
        self.status=self.statusBar()
        self.status.showMessage(f"{len(masterspellsdict)} spells loaded. "+updatestatus)
    def pickchar(self,*,infile):
        global filename
        filename=infile
        self.close()

def CharacterSelect(updatestatus):
    # Button(subframe,text='New Character',command=root.destroy,relief=FLAT).pack(fill=X)
    app=QApplication()
    window=CharacterSelectWindow(updatestatus)
    window.show()
    app.exec()
    app.shutdown()
    return

if __name__=="__main__":
    updatestatus=updatecheck()
    filename=None
    CharacterSelect(updatestatus)
    print(filename)
    app=QApplication()
    c=character()
    if filename is None: c.show()
    else: c.load(filename)
    app.exec()