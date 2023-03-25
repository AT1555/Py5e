Py5e - An Interactive Character Sheet for D&D 5th Edition
Developed by Anthony Taylor
Version: 2023_02_04

INTRODUCTION

As its name suggests, Py5e is written in Python 3.8 and condensed into a fully portable EXE by Pyinstaller (https://www.pyinstaller.org/).  As such, it should run on Windows 10 without any dependencies as a standalone EXE.

What it does:
Py5e was created with the intention of having a character sheet that is easy to use during a session for the tracking of ability uses, spell slots, items and equipment. Abilities with limited numbers of uses are tracked, and can be reset with one click on short/long rests, or manually restored for abilities such as "Arcane Recovery" (or similar). Backpack items can be added and discarded on the fly. Equipment, including magic items that affect ability scores, or provide bonuses to AC, can be equipped/unequipped with the associated stats updating automatically. 

What it does not do:
Py5e is not intended to assist in leveling up a character, or in character creation. Permanent changes in a character's stats or a character's abilities require manual editing of a .5e character file (more on this later). Py5e's purpose is to automate resource management and stat calculations during a session, not to provide full character editing, which is best performed outside a session.

INSTALLATION

As a standalone executable, Py5e does not require any installation, or dependencies. 

STARTING THE PROGRAM

Simply run the EXE by double-clicking on it, or by calling it from the command line. First, a command prompt will open while Py5e loads. This command prompt is simply a background window and may be minimized, but closing it will terminate Py5e. Next, Py5e will open an Explore-like window to select a character file. Character files (stylized as '.5e' files) are simply ASCII/text files containing all of the information necessary to define a character. After selecting an appropriate file, Py5e's main window will open. This window is divided into 3-4 tabs (depending on if the character has spells or not). 

CHARACTER TAB

The Character Tab contains a number of widgets related to the character's core stats, and current status. 

HEADER: The header section contains the character's name, classes, HP, Temp HP, current AC, and movement speed. 
Name and Classes: These are not interactive, and simply display the character's name and class(es). 
HP: Clicking on the character's HP will open a dialog box for applying damage or healing. For damage, enter a negative integer, for healing, enter a positive integer. If a character heals above their max HP, they will instead cap at their max HP. 
Temporary HP: Temporary HP can be assigned using the button to the right of the HP. As per 5e rules, Temp HP does not stack, thus in this dialog box, enter the new total Temp HP, not the change in Temp HP. When applying damage via the HP button, Py5E will automatically damage the Temp HP first, then damage regular HP after the Temp HP is exhausted. Temp HP also resets to 0 on a short or long rest. 
AC: The character's AC is calculated and updated automatically based on the character's DEX, and any equipment that provides an AC bonus. (If a character's DEX changes, be sure to doff then re-don any armor with a dexterity bonus limit (medium/heavy armor) for an accurate AC.)
Speed: Simply shows the character's base movement speed.
Color: The paintbrush icon allows the user to customize the sheet's background and font colors. This will open a popup window with prompts. Select "Preview" to test the new color selection in the popup window. Select "Set" to apply the new colors to the whole sheet. When a sheet is saved, the active color options are also saved. 

STATS: The stat block shows the character's current ability scores and Proficiency Bonus. For each ability score, the current score is shown (with bonuses from equipment, etc.), then the corresponding ability modifier, then the saving throw bonus. 

SKILLS: The skill block shows a character's bonuses to each skill (including passive skills, and initiative), calculated from the character's ability scores, equipment, Skill Proficiencies, and Expertise’s. This block also supports the Jack of All Trades feature, if such a feature is added as a Feature (See below) with the specific name "Jack of All Trades". Proficient skills are marked with an "*", and expertise skills are marked with "**". Passive skills are marked with "(P)". 

LANGUAGES AND PROFICIENCIES: These blocks are non-interactive, and simply show the character’s languages and proficiencies. Listing a proficiency here does not affect the rest of the sheet. See equipment proficiency in the .5 file equipment section). 

ABILITIES: This block shows the abilities of a character. Each entry may be clicked to expend one use. This may be reversed by clicking the "+" button next to each feature. Each feature is also tied to a type of rest (see Recovery) and will reset to max when the corresponding rest is triggered. New abiliites may be added by clicking on the "Abilities (+)" header.

EQUIPMENT: This block shows a characters equipped (box with checkmark) and unequipped (empty box) gear. Clicking on a piece of gear will toggle its equipped status. Equipped gear that provides stat bonuses will only do so when equipped. Gear with bonuses will show display the bonus next to its name. Gear that can deal damage will show its current "To Hit" bonus, and damage output, based on the gear's intrinsic stats, as well as if the character is tagged as proficient in its use, and the character's ability scores. Abilities or features provided by gear should have those abilites entered separately in the Abilities section. New equipment may be added by clicking on the "Equipment (+)" header. 

FEATURES: This block shows a character's features. Features consist of a Name, Mods, and a Description. By clicking on a feature's name, the description will appear in a popup window. Mods in features function the same as Equipment mods. New features may be added by clicking on the Feature (+)" header.

RECOVERY: This block shows three types of recovery: Long/Short rests, and Days. Clicking a recovery options will automatically reset all Features and Abilities that restore on that recovery option. Note that a Long Rest will also trigger the effects of a Short Rest. However, a Day will not trigger a Long Rest or Short Rest. (Other time intervals may be added in future releases.)

SAVE/&/QUIT: The Save, &, and Quit buttons are fairly self explanatory. Clicking "Save" will open an Explorer dialog for providing a save filename and location. This saves the character sheet's current configuration in a .5e file. Pressing "&" will provide the same prompts as "Save", then exit the program. Selecting "Quit" will exit the program.

BACKPACK TAB

The backpack tab shows items that a character currently holds, along with the quantity of each item. Clicking an item lets the user adjust its quantity. Clicking the "X" next to an item will remove it from the list. Clicking "Add Item" will guide the user though a few prompts to add a new item to the list. Gold is shown at the top of the list, and can be modified by clicking on it. (There is currently no support for Platinum, silver, or coppers. Simply use fraction gold pieces to represent these denominations). 

SPELLBOOK TAB

The Spellbook Tab contains a listing of a character's spells, as well as any spell slots to which they have access. New spells may be added with the "Add Spell" button. Clicking on a spell will show its description in a popup window. Spell slots may be added by creating an ability that is marked as a spell slot (see add ability popup window). The name of such an ability must start with an integer [0-9] to correctly display it on the Spellbook tab. When first added, new spell slots will appear at the bottom of the spell list. This is a known bug that resolves itself if the sheet is saved and reloaded.

NOTES TAB

The Notes tab is a free-form space for taking notes. These are saved in the character sheet and may be modified freely. 

LOG TAB

The Log tab keep track of all actions taken in Py5e for a given runtime. This log is also appended to a .log file when Py5e is closed. 

CHANGELOG
(2021/03/15): Added try/except functionality to import to allow for characters with missing sections. Section order no longer matters. Finished Character section of creation script.
(2021/03/16): Added "Add Ability" functionality. No way to delete them yet, but this could be solved with an X button.
(2021/03/17): Added "Add Equipment" functionality. No way to delete them yet, but this could be solved with an X button. Added remove equipment and ability functions with Are You Sure? Popup. Also applied to backpack. 
(2021/03/18): Added Proficiency tag to Add Equipment function. Spellcasting added to character creator. Added "Add Spells" function. 
(2021/07/06): Abilities and Equipment can now be deleted. Features, languages, and proficiencies are now automatically alphabetized. 
(2021/07/10): Added logging.
(2021/07/17): Fixed egregious spelling mistake. Fixed bug where new abilities/spells/equipment did not write to the log file. Now compiling using '-w' option to remove the command prompt popup. Added Log page to track events live.
(2021/09/05): Fixed bug where saving a charcter without Expertise left an empty EXPERTISE line in the savefile. Replaced logfile writing commands with simply writing the running log to file when the sheet is closed. Calling a Long Rest now calls a Short Rest simultanesouly in the same function call without recursion. 
(2021/10/03): Implmented spell descriptions. Spell syntax was changed as a result, and the add spell function was updated accordingly. Old savefiles must be manually updated to work with the new version.
(2021/10/10): Added custom coloring of backgrounds and fonts. Select the paintbursh icon near the Character's name to customize colors. No save file modifications are needed. Upon saving for the first itme, the sheet will automatically add the new (optional) keywords.
(2021/10/23): Fixed bugs in the character creation wizard that did not properly format a new sheet to conform with the current sheet parser. 
(2021/11/21): Quitting without using "Save and Quit" (pressing "Quit" or closing the window) now confirms with the user whether they wish to quit without saving. 
(2021/11/25): Logs are now written in a single logfile per character that is appended to upon closing a sheet. Execute the file CondenseLogs.exe in the directory with the previous log file to condense them inot a single new-style log file. 
(2022/05/06): Font size now automatically resizes when window is resized.
(2022/05/07): Overhauled save file read-in and treatment of spells and spell slots. .5e files from before this version are no longer compatible and must be updated using 2022_05_06-2022_05_07.exe before they will open succesfully in the new version. The start screen now automatically finds .5e files in the launch directory to open quickly. The automatic text resizing has been replaced by a button in the upper right of the character tab. A bug involving a "Day" rest period was fixed that caused "Day" to be case senstive. Class specific spell slots are now supported. 
(2022/05/08): Features are now an new class. They accept the keywords: NAME, MODS, TEXT, and can be added from the GUI. MODS will directly modify the calculated ability scores, HP, AC, skills, etc. MODS activate immediately on load, and deactivate if a feature is delated. The feature name may be clicked to see a qualitative description of the feature. The old features listing has been removed from the program and the old character FEATURES keyword will be automatically removed from .5e files when saved with the latest Py5e version. The startup screen has been revamped with character colors from .5e files. Exiting the startup screen with the window manger now fully kills the script. Upon exit, the new character creator will now automatically load the created character. Jack of all Trades now applies by looking for the word "Jack" at the start of a feature's name. The old JACK keyword functionality had been removed. Expanded README text.
(2022/07/21): Fixed bug that caused a feature that granted an AC bonus to call a character update on startup before the featurelist was compiled.
(2023/02/04): Introduced functionality to automatically fill spell descriptions from a 5etools directory. Simply place the directory '5etools-v*' in the same direcotry as Py5e and spell descriptions will import automatically. Spell text is now for custom spells or for adding notes and flavor to official spells. Full backwards compatibility is supported with old sheets. 
(2023/03/25): Cleaned up some backend code. Fixed a bug requiring a spell level for a published spell when creating a new spell (now level is assumed to be zero if not provided). Fixed a bug that did not show lists of effects for spells such as Prestidigitation. Fixed the early-quit-out bug. Introduced automatic updates. Py5e will now automatically check for updates and download the latest version if available.