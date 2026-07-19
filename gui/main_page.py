from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QScrollArea, QFrame, QInputDialog
from PySide6.QtCore import Qt

class mainPage(QWidget):
    def __init__(self,c):
        super().__init__()
        self.c=c
        self.cLayout=QVBoxLayout()
        self.setLayout(self.cLayout)
        
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
        self.cMiddleLayout.addLayout(self.cAbilityLayout)
        self.cMiddleLayout.addWidget(QFrame(frameShape=QFrame.HLine))
        
        self.cAbilityLayout.addWidget(QLabel('Abilities:',alignment=Qt.AlignmentFlag.AlignCenter))
        self.cAbilityLayout.addStretch()

        self.cEquipLayout=QVBoxLayout()
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
        self.featureLayout.addStretch()
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