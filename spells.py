from glob import glob
import json
from gui.common import contextWidget, PopupDialog, QDialog5e, NoWheelSpinBox
from utilities import numsuffix
from PySide6.QtWidgets import QPushButton, QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, QComboBox, QMessageBox, QTextEdit

def get_schools():
    return {'V':'evocation','N':'necromancy','T':'transmutation','I':'illusion','E':'enchantment','D':'divination','C':'conjuration','A':'abjuration'}

def load_spells():
    masterspellsdict={}
    for spellfile in sorted(glob('5etools_spells/spells*.json')):
        try:
            with open(spellfile) as temp:
                data=json.load(temp)
                for rawspell in data['spell']: 
                    if rawspell['name'] in masterspellsdict: masterspellsdict[rawspell['name']+' (Legacy)']=masterspellsdict[rawspell['name']] #do not override reprinted spells, works only because PHB2024 is labelled xPHB and is sorted last.
                    masterspellsdict[rawspell['name']]=rawspell
        except Exception: print(f'Error loading spells from {spellfile}')
    return masterspellsdict

def process_spell_description(entries):
    description=''
    for entry in entries:
        if isinstance(entry,str): description+='\n\n'+entry
        elif entry['type']=='list': 
            for item in entry['items']: #inconsistent use of entires vs list in 5e.tools necessitates this section
                if isinstance(item,str): description+='\n'+item
                elif isinstance(item,dict) and 'entries' in item: description+='\n-'+f"{item['name']+': ' if 'name' in item else ''}{process_spell_description(item['entries'])}"
        elif entry['type']=='entries': description+='\n-'+f"{entry['name']+': ' if 'name' in entry else ''}{process_spell_description(entry['entries'])}"
        elif entry['type']=='table': 
            if 'caption' in entry: description+='\n\n'+entry['caption']
            else: description+='\n\n'
            for rowidx in range(len(entry['rows'])): #clean up rows in case of subdictionaries
                for rowidxidx in range(len(entry['rows'][rowidx])):
                    if isinstance(entry['rows'][rowidx][rowidxidx],dict) and 'roll' in entry['rows'][rowidx][rowidxidx]:
                        if 'exact' in entry['rows'][rowidx][rowidxidx]['roll']: entry['rows'][rowidx][rowidxidx]=entry['rows'][rowidx][rowidxidx]['roll']['exact']
                        elif 'min' in entry['rows'][rowidx][rowidxidx]['roll'] and 'max' in entry['rows'][rowidx][rowidxidx]['roll']: entry['rows'][rowidx][rowidxidx]=str(entry['rows'][rowidx][rowidxidx]['roll']['min'])+'-'+str(entry['rows'][rowidx][rowidxidx]['roll']['max'])
            for row in entry['rows']: description+='\n'+', '.join([f"{entry['colLabels'][num]}: {row[num]}" for num in range(len(row))])
        else: pass
    description=description.replace('[Area of Effect]','') 
    while '{' in description: #clean up bracketed text
        start=0
        end=0
        idx=0
        while start==0 or end==0:
            if description[idx]=='{': start=idx
            if description[idx]=='}': end=idx
            idx+=1
        brackets=description[start:end+1]
        if '@' in brackets: 
            if '@chance' in brackets: description=description.replace(brackets,brackets.split(' ')[1].split('|')[0]+'%')
            elif '@note' in brackets: description=description.replace(brackets,brackets.replace('@note','').strip()[1:-1])
            elif '@creature' in brackets: 
                if brackets.count('|')==2: #a second '|' is used is the creature is plural
                    temp=brackets.split('|')[-1].replace('}','').replace('{','').strip()
                    temp=' '.join([i for i in temp.split(' ') if '@' not in i])
                    description=description.replace(brackets,temp)
                else: 
                    temp=brackets.split('|')[0].replace('}','').replace('{','').strip()
                    temp=' '.join([i for i in temp.split(' ') if '@' not in i])
                    description=description.replace(brackets,temp)
            elif any([key in brackets for key in ['@action','@book','@classFeature','@condition','@filter','@hazard','@item','@quickref','@race','@sense','@skill','@spell','@status','@variantrule']]): #grab preceeding phrase
                temp=brackets.split('|')[0].replace('}','').replace('{','').strip()
                temp=' '.join([i for i in temp.split(' ') if '@' not in i])
                description=description.replace(brackets,temp)
            elif any([key in brackets for key in ['@dice','@scaledamage','@scaledice','@status']]): #grab last phrase
                temp=brackets.split('|')[-1].replace('}','').replace('{','').strip()
                temp=' '.join([i for i in temp.split(' ') if '@' not in i])
                description=description.replace(brackets,temp)
            elif '@adventure' in brackets:
                temp=brackets.replace('|',', ').replace('}','').replace('{','').strip()
                temp=' '.join([i for i in temp.split(' ') if '@' not in i])
                description=description.replace(brackets,temp)
            else: #return all non-@ words in the brackets # ['@b','@d20','@damage','@dc','@hit','@i',]
                description=description.replace(brackets,' '.join([i for i in brackets.split(' ') if '@' not in i]).replace('}','').replace('{','').strip())
        elif '|' in brackets: description=description.replace(brackets,brackets.split('|')[-1].replace('}','').replace('{','').strip())
        else: description=description.replace(brackets,brackets.replace('}','').replace('{','').strip())
    return description.strip()

class spell():
    def __init__(self,spelldict,c):
        self.c=c
        self.name='?'
        self.lookup=''
        self.description=''
        self.text=''
        self.level=0
        self.prep=False
        self.load(spelldict)
    def load(self,spelldict):
        if 'NAME' in spelldict: self.name=spelldict['NAME']
        if 'LOOKUP' in spelldict: 
            if spelldict['LOOKUP']=='1': self.lookup=spelldict['NAME'] #needed for the transtion to new code.
            elif spelldict['LOOKUP']==0: self.lookup=''
            else: self.lookup=spelldict['LOOKUP']
        else: self.lookup=spelldict['NAME']
        self.description=''
        if self.lookup in self.c.masterspellsdict:
            match=self.c.masterspellsdict[self.lookup]
            self.level=match['level']
            self.description+=f"{numsuffix(match['level'])}-level {get_schools()[match['school']]}\nCasting Time: {match['time'][0]['number']} {match['time'][0]['unit']}"
            if match['range']['type']!='special': self.description+=f"\nRange: {match['range']['distance']['amount'] if match['range']['distance']['type']=='feet' else ''} {match['range']['distance']['type']}"
            self.description+=f"\nComponents: {'V ' if 'v' in match['components'] else ''}{'S ' if 's' in match['components'] else ''}{'M: '+match['components']['m']['text'] if 'm' in match['components'] and 'text' in match['components']['m'] and isinstance(match['components']['m'],dict) else 'M: '+match['components']['m'] if 'm' in match['components'] else ''}"
            self.description+=f"\nDuration: {match['duration'][0]['type'] if match['duration'][0]['type']!='timed' else str(match['duration'][0]['duration']['amount'])+' '+match['duration'][0]['duration']['type']+(', Concentration' if 'concentration' in match['duration'][0] else '')}"
            self.description+='\n\n'+process_spell_description(match['entries'])
            if 'entriesHigherLevel' in match: self.description+='\n\n'+process_spell_description(match['entriesHigherLevel'])
        else:
            if 'LEVEL' in spelldict: 
                try: self.level=int(spelldict['LEVEL'])
                except ValueError: self.level=0
        if 'PREP' in spelldict: self.prep=bool(int(spelldict['PREP']))
        if 'TEXT' in spelldict: 
            self.text=spelldict['TEXT'].replace('\n','\\')
            self.description+=spelldict['TEXT'].replace('\\','\n') 
    def update(self):
        if not self.prep: self.gui.toggleButton.setText('\u2610')
        else: self.gui.toggleButton.setText('\u2611')
    def toggle(self):
        if self.prep: self.prep=False
        else: self.prep=True
        self.update()
    def show(self):
        self.gui=spellWidget(self)
        self.update()
    def delete(self):
        self.c.spellbookdict[str(self.level)].remove(self)
        self.c.update()
    def save(self):
        return f"%SPELL\nNAME={self.name}\nLOOKUP={self.lookup}\nLEVEL={self.level}\nPREP={int(self.prep)}\nTEXT={self.text}\n\n"

class spellWidget(contextWidget):
    def __init__(self,spell):
        super().__init__(movable=True)
        self.spell=spell
        self.toggleButton=QPushButton(text='[?]',clicked=self.toggle)
        self.toggleButton.setFixedWidth(self.toggleButton.sizeHint().height())
        self.layout.addWidget(self.toggleButton)
        self.infoButton=QPushButton(text=self.spell.name,clicked=self.showinfo)
        self.layout.addWidget(self.infoButton)
        self.guiLocation=self.spell.c.gui.spellsPage.spellLVLLayouts[(str(self.spell.level))]
        self.guiLocation.insertWidget(self.guiLocation.count(),self)
    def toggle(self):
        self.spell.toggle()
    def showinfo(self):
        self.dialog=PopupDialog(self.spell.name,self.spell.description.replace('\\','\n'))
        self.dialog.show()
    def edit(self):
        dialog=getSpell(self.spell.c.masterspellsdict,self.spell)
        if dialog.exec()==QDialog.Accepted:
            newDict=dialog.getData()
            self.spell.load(newDict)
            self.infoButton.setText(self.spell.name)
        self.spell.c.update()
    def delete(self):
        self.guiLocation.removeWidget(self)
        self.setParent(None)
        self.deleteLater()
        self.spell.delete()
    def moveUp(self):
        self.move(self.spell,self.spell.c.spellbookdict[str(self.spell.level)],self.guiLocation,up=True)
        self.spell.c.update()
    def moveDown(self):
        self.move(self.spell,self.spell.c.spellbookdict[str(self.spell.level)],self.guiLocation,up=False)
        self.spell.c.update()

class getSpell(QDialog5e):
    def __init__(self,masterspellsdict,oldSpell=None):
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
        if oldSpell is not None:
            self.name.setText(oldSpell.name)
            self.lookup.setCurrentText(oldSpell.lookup)
            self.description.setText(oldSpell.text.replace('\\','\n'))
    def verifyData(self):
        if len(self.name.text())<1: 
            QMessageBox.warning(self,'Invalid Name','No display name provided.')
            return 
        self.accept()
    def getData(self):
        return {'NAME':self.name.text().strip(),'LEVEL':self.level.value(),'LOOKUP':self.lookup.currentText(),'TEXT':self.description.toPlainText().strip()}