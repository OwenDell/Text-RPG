#########################################
#               IMPORTS                 #
#########################################

import random
from inspect import signature
import functions as f
import playerstats as p
import creatures as c
import areas as a
import encounters as e
import battle as b
import statuses as s

#########################################
#           GLOBAL VARIABLES            #
#########################################

print = f.print_override
player = c.player
moves_list = c.moves_list
activities_list = a.activities_list
heal = b.heal
cleanse = s.cleanse
dummy = c.wwe_champ
fight = b.fight
loot = p.loot
commands_list = {}
p.current_area = a.chalgos
test_iteration = 1 #used for the run_test function, that keeps track of how many tests have been run during this instance of the program.
running = True #while true, the main gameplay loop will continue running. Ends with either the end_game() function or if the player dies.

#########################################
#          BACK-END FUNCTIONS           #
#########################################

def converter(*args): #converts string inputs into either global objects, integers, floats, or lists based on the tag at the beginning of the string.
    args = list(args)
    for index, parameter in enumerate(args):
        if "/O/" in parameter[:3].upper():
            args[index] = globals()[parameter[3:]]
        elif "/I/" in parameter[:3].upper():
            args[index] = int(parameter[3:])
        elif "/F/" in parameter[:3].upper():
            args[index] = float(parameter[3:])
        elif "/L/" in parameter[:3].upper():
            args[index] = parameter[3:].split()
        else:
            pass
    return args

def learn_move(move_name): #adds a new move to the player.moves dictionary
    move_name = f.capitalize(move_name)
    try:
        player.moves[move_name] = moves_list[move_name]
        print(f"You learned {move_name}!")
    except:
        print(f"Unrecognized move: \'{move_name}\'.")
    
def run_test(*args): #used for running tests, mainly intended to be used through devcmds, where you can feed in however many arguments you want and it will try to print them back to you.
    global test_iteration
    print(f"Running Test #{test_iteration}...")
    print(args)
    print(f"Test #{test_iteration} complete.")
    test_iteration += 1

def set_dummy(dummy_name):
    global dummy
    dummy = c.dummy_init(dummy_name)
    
def end_game(): #ends the game.
    global running
    running = False
    print("Ending gameplay loop...")
        
def duel(duelist1, duelist2): #mostly just used for testing, at least currently.
    victor = False
    loser = False
    print(f"A 1v1 Duel begins between the {duelist1.name} and the {duelist2.name}!")
    while duelist1.health > 0 and duelist2.health > 0:
        duelist1.creature_attack(duelist2)
        duelist2.creature_attack(duelist1)
    if duelist1.health <= 0 and duelist2.health <= 0:
        print(f"Both duelists felled each other simultaneously, ending in a draw!")
        victor = False
    elif duelist1.health > 0:
        victor = duelist1
        loser = duelist2
    elif duelist2.health > 0:
        victor = duelist2
        loser = duelist1
    if victor != False:
        victor.gold += loser.gold
        print(f"The {victor.name} has felled the {loser.name} in single combat, earning them {loser.gold} gold!")

def teleport(area):
    try:
        p.current_area = a.areas[f.capitalize(area)]
        print(f"You have arrived at {p.current_area.name}.")
    except:
        print(f"Invalid area name \'{f.capitalize(area)}\'")

def devmode(allitems=False, allmoves=False):
    if allitems != False:
        for item in p.items_list:
            loot(item, 999)
    if allmoves != False:
        for move in c.moves_list:
            learn_move(move)

#########################################
#          FRONT-END FUNCTIONS          #
#########################################

def f_devcmds(): #hidden command that the player can run that allows them to run any function in the game by inputting the name of the function. Will request the player to input additional arguments for every parameter required by the function.
    try:
        command = globals()[input("Enter a command: ")]
        params_list = str(signature(command).parameters)[13:-2].split(">), (")
        try:
            if params_list != ['']:
                params_count = len(params_list)
            else:
                params_count = 0
            params_response = [input(f"Argument #{i+1}/{params_count}: ") for i in range(params_count)]
            try:
                if params_response[0].upper() == "SET_ARGS":
                    params_count = int(input("How many arguments? "))
                    params_response = [input(f"Argument #{i+1}/{params_count}: ") for i in range(params_count)]
            except:
                pass
            params_response = converter(*params_response)
            command(*params_response)
        except Exception as e:
            print("An error has occurred [1].")
            print(e)
    except:
        print("Unrecognized command.")
        
def f_commands(): #prints a list of all the front-end functions to the player, with the exception of devcmds (devcmds must be the first of the front-end functions to be initialized for this to work)
    f.header("Commands List")
    for command in commands_list:
        if command != "Devcmds":
            print(commands_list[command])
    f.header("Activities List")
    for activity in activities_list:
        if activity in p.current_area.activities:
            print(activities_list[activity])
    f.header()
            
def f_inventory():
    p.inventory_check()

def f_use():
    c.moves_list["Use"](player, player)

def f_stats():
    f.header("Player Stats")
    print(f"Level: {player.level}\nExperience: {player.XP}/{p.reqXP}\nHealth: {player.health}/{player.maxHP}\nMana: {p.mana}/{p.maxMana}\nEnergy: {p.energy}/{p.maxEnergy}\nGold: {player.gold}\nStrength: {p.strength} (+{p.effective_strength-p.strength})\
          \nDexterity: {p.dexterity} (+{p.effective_dexterity-p.dexterity})\nIntelligence: {p.intelligence} (+{p.effective_intelligence-p.intelligence})")
    f.header()
    
def f_status_effects():
    f.header("Status Effects")
    for item in player.statuses:
        print(s.statuses_list[item[0]])
    if len(player.statuses) < 1:
        print("You don't have any status effects.")
    f.header()

#########################################
#               COMMANDS                #
#########################################

class Command:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        commands_list[self.name] = self

    def __str__(self):
        return f"{self.name}: {self.description}."

    def __call__(self):
        globals()["f_"+"_".join(self.name.lower().split())]()

devcmds = Command("Devcmds", "Enter a developer command")
commands = Command("Commands", "Gives a list of all valid commands")
inventory = Command("Inventory", "Gives a list of all items in your inventory")
stats = Command("Stats", "Prints out your characters stats")
status_effects = Command("Status Effects", "Gives a list of all of your current status effects")
use = Command("Use", "Use a consumable item in your inventory while out of combat")

#########################################
#             GAMEPLAY LOOP             #
#########################################

while running == True:
    s.cure_check(player)
    response = f.capitalize(input("What would you like to do? "))
    try:
        if response in p.current_area.activities:
            activities_list[response](p.current_area)
        else:
            commands_list[response]()
    except:
        print(f"Response \'{response}\' not recognized. Try \'Commands\' for a list of valid options.")
        
print("Game has ended.")
