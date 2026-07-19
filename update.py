import sys
from gui.common import QMainWindow5e
from PySide6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLabel
from bs4 import BeautifulSoup
from pathlib import Path
from os import getcwd, mkdir
import requests
import json

class UpdateWindow(QMainWindow5e):
    def __init__(self,VERSION,latest):
        super().__init__()
        self.setWindowTitle("Py5e Updater")
        layout=QVBoxLayout()
        message=QLabel(f'Latest update ({VERSION} \u2192 {latest}) downloaded. Please exit and relaunch.')
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

def updatecheck(VERSION):
    #check for updates
    try:
        latest=BeautifulSoup(requests.get("https://github.com/AT1555/Py5e/releases/latest").content,features="html.parser").title.string.split(' ')[1]
        if int(VERSION.replace('-',''))<int(latest.replace('-','')):
            if not Path(getcwd()+f'\\Py5e_{latest}.exe').exists(): 
                open(getcwd()+f'\\Py5e_{latest}.exe','wb').write(requests.get(f'https://github.com/AT1555/Py5e/releases/download/{latest}/Py5e_{latest}.exe',allow_redirects=True).content)
                message=download_spells(force=True) #force a redownload when Py5e updates to make sure re-used files are up to date. 
            app=QApplication()
            window=UpdateWindow(VERSION,latest)
            window.show()
            app.exec()
            app.shutdown()
            return f'Py5e is out of date ({latest} available, current: {VERSION}).\n'+message
        else: 
            message=download_spells()
            return f'Py5e is up to date ({VERSION}).\n'+message
    except Exception: return 'Error when checking for updates.'

def download_spells(force=False):
    #automatically get spell data from 5e.tools
    if not Path(getcwd()+"\\5etools_spells").exists(): mkdir(getcwd()+"\\5etools_spells")
    download_count=0
    sources=json.loads(requests.get('https://raw.githubusercontent.com/5etools-mirror-3/5etools-src/refs/heads/main/data/spells/index.json').text)
    for source in sources:
        if not Path(getcwd()+f"\\5etools_spells\\{sources[source]}").exists() or force: 
            open(getcwd()+f"\\5etools_spells\\{sources[source]}",'wb').write(requests.get(f'https://raw.githubusercontent.com/5etools-mirror-3/5etools-src/refs/heads/main/data/spells/{sources[source]}').content)
            download_count+=1
    if download_count>0: return f'{download_count} 5e.tools spells repositories downloaded. '
    else: return f'All 5e.tools spells repositories are present.'
