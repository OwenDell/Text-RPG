#########################################
#               IMPORTS                 #
#########################################

import random
import time
from inspect import signature
import functions as f
import playerstats as p
import creatures as c
import areas as a
import encounters as e
import battle as b
import statuses as s
import npc as n
import encyclopedia as y

#########################################
#           GLOBAL VARIABLES            #
#########################################

print = f.print_override 
sleep = f.sleep 
player = c.player
moves_list = c.moves_list
activities_list = a.activities_list
heal = b.heal
dummy = c.wwe_champ #Used with the fight developer command, stores a 'dummy' version of an enemy that can be changed out with the set_dummy command to make testing specific enemies easy
fight = b.fight
loot = p.loot
level_up = c.level_up
commands_list = {} #Dictionary of all front-end commands that the player can enter, using the Command class
p.current_area = a.chalgos
test_iteration = 1 #used for the run_test function, that keeps track of how many tests have been run during this instance of the program.
running = True #while true, the main gameplay loop will continue running. Ends with either the end_game() function or if the player dies.

#########################################
#          BACK-END FUNCTIONS           #
#########################################

def converter(*args): #converts string inputs into either global objects, integers, floats, or lists based on the tag at the beginning of the string. Mainly used for developer console commands
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
        elif "/B/" in parameter[:3].upper():
            args[index] = True if parameter[3:] == "True" else False
        else:
            pass
    return args

def learn_move(move_name): #adds a new move to the player.moves dictionary. Mainly used for testing purposes
    move_name = f.capitalize(move_name)
    try:
        player.moves[move_name] = moves_list[move_name]
        moves_list[move_name].learned = True
        print(f"You learned {move_name}!", 0.15)
    except:
        print(f"Unrecognized move: \'{move_name}\'.", 0.5)
    
def run_test(*args): #used for running tests, mainly intended to be used through devcmds, where you can feed in however many arguments you want and it will try to print them back to you.
    global test_iteration
    print(f"Running Test #{test_iteration}...")
    print(args)
    print(f"Test #{test_iteration} complete.")
    test_iteration += 1

def set_dummy(dummy_name): #Sets the dummy to any creature in the game, so that they can be fought with the fight command by targetting the dummy object. Used for testing.
    global dummy
    dummy = c.dummy_init(dummy_name)
    
def end_game(): #Developer command to end the game.
    global running
    running = False
    print("Ending gameplay loop...")
        
def duel(duelist1, duelist2): #Choose any two creatures to fight each other in a duel until one dies. Mostly just used for testing, at least currently. 
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
        print(f"The {victor.name} has felled the {loser.name} in single combat, earning them {loser.gold} gold!")

def teleport(area): #Developer command to instantly teleport to any area without having to go through the travel process.
    try:
        p.current_area = a.areas[f.capitalize(area)]
        p.position = a.areas[f.capitalize(area)].distance
        print(f"You have arrived at {p.current_area.name}!", 0.7)
    except:
        print(f"Invalid area name \'{f.capitalize(area)}\'", 0.3)

def set_rep(npc, rep): #Developer command to set reputation with any NPC to any value.
    n.npc_list[npc].relation = rep

def devmode(allitems=False, allmoves=False, gold=False): #Developer command to quickly and easily get access to all items, moves, and a lot of gold. Makes testing much quicker and easier.
    if allitems != False and allitems != "False":
        for item in p.items_list:
            loot(item, 999)
    if allmoves != False and allmoves != "False":
        for move in c.moves_list:
            learn_move(move)
    if gold != False and gold != "False":
        player.gold += 9999999

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
    f.header("Commands List", 0.5)
    for command in commands_list:
        if command != "Devcmds":
            print(commands_list[command], 0.3)
    f.header("Activities List", 0.5)
    for activity in activities_list:
        if activity in p.current_area.activities:
            print(activities_list[activity], 0.3)
    f.header("", 0.5)
    
def f_settings(): #prints out a list of changeable settings and their current values. Allows the player to change the settings as they desire.
    f.header("Settings", 0.5)
    print(f"Text Speed: {f.sleepmultiplier}x Speed", 0.3)
    f.header("", 0.5)
    response = f.capitalize(input("What setting do you want to change? "))
    if response == "Text Speed":
        response2 = input(f"What do you want to set {response} to? ")
        try:
            if float(response2) <= 0:
                response2 = 999
            f.sleepmultiplier = float(response2)
            print(f"{response} changed to {response2}x Speed.")
        except:
            print(f"Invalid response \'{response2}\'.")
    else:
        print(f"Invalid option \'{response}\'.")
            
def f_inventory(): #prints out the players full inventory
    p.inventory_check(0.15)

def f_use(): #allows the player to use any consumable item while out of combat
    c.moves_list["Use"](player, player)

def f_stats(): #prints out current information about the player
    f.header(f"{p.player_name}'s Stats", 0.5)
    print(f"\nCurrent Area: {p.current_area.name}", 0.25)
    print(f"Level: {player.level}", 0.25)
    print(f"Experience: {player.XP}/{p.reqXP}", 0.25)
    print(f"Health: {player.health}/{player.maxHP}", 0.25)
    print(f"Mana: {p.mana}/{p.maxMana}", 0.25)
    print(f"Energy: {p.energy}/{p.maxEnergy}", 0.25)
    print(f"Evasion: {player.evasion}%", 0.25)
    print(f"Speed: {p.speed}%", 0.25)
    print(f"Gold: {player.gold}", 0.25)
    operator = "+" if p.effective_vitality-p.vitality >= 0 else ""
    print(f"\nVitality: {p.vitality} ({operator}{p.effective_vitality-p.vitality})", 0.25)
    operator = "+" if p.effective_strength-p.strength >= 0 else ""
    print(f"Strength: {p.strength} ({operator}{p.effective_strength-p.strength})", 0.25)
    operator = "+" if p.effective_dexterity-p.dexterity >= 0 else ""
    print(f"Dexterity: {p.dexterity} ({operator}{p.effective_dexterity-p.dexterity})", 0.25)
    operator = "+" if p.effective_intelligence-p.intelligence >= 0 else ""
    print(f"Intelligence: {p.intelligence} ({operator}{p.effective_intelligence-p.intelligence})", 0.25)
    operator = "+" if p.effective_faith-p.faith >= 0 else ""
    print(f"Faith: {p.faith} ({operator}{p.effective_faith-p.faith})", 0.25)
    print(f"\nReceived Damage Multipliers:", 0.25)
    for resistance in player.damage_resistances:
        print(f"{resistance}: {round(player.damage_resistances[resistance]*100, 1)}%", 0.25)
    print("")
    f.header("", 0.5)

def f_equipment(): #prints out the players currently equipped gear, as well as allowing them to inspect any piece of equipment and swapping out their currently equipped gear
    while True:
        f.header("Currently Equipped Gear", 0.5)
        for equipped in p.equipment:
            print(f"{f.capitalize(equipped)}: {p.equipment[equipped]}", 0.2)
        f.header("", 0.5)
        print("Would you like to Inspect a piece of equipment, Swap out your equipment, or Exit?", 1)
        response = f.capitalize(input("Enter either (1) 'Inspect' (2) 'Swap' or (3) 'Exit': "))
        sleep(0.5)
        if response == "Inspect" or response == "1":
            response = f.capitalize(input("What piece of equipment would you like to inspect? "))
            sleep(0.5)
            if response in p.weapons_list:
                y.check_encyclopedia(response, "Weapons")
            elif response in p.armor_list:
                y.check_encyclopedia(response, "Armor")
            else:
                print("Invalid response, your response must be the name of a piece of equipment.", 1)
        elif response == "Swap" or response == "2":
            try:
                print("What piece of equipment would you like to swap out?", 0.8)
                response = f.capitalize(input("Enter either the name of the piece of equipment or the name of the equipment slot you want to swap out: "))
                sleep(0.5)
                if response in p.equipment.keys():
                    pass
                elif p.equipment_list[response].slot == "Both":
                    response = "Mainhand"
                else:
                    response = p.equipment_list[response].slot
                p.inventory_check(0.15, response)
                response2 = f.capitalize(input("What do you want to swap it out with? (or enter 'Unequip' to unequip the item and move it to your inventory) "))
                sleep(0.5)
                try:
                    if response2 == "Unequip":
                        if p.equipment_list[p.equipment[response]].name == "Empty" or p.equipment_list[p.equipment[response]].name == "None":
                            print(f"You don't have anything equipped in your {response} slot.", 1)
                        else:
                            print(f"You unequipped your {p.equipment_list[p.equipment[response]].name} and moved it to your inventory.", 1.5)
                            p.equipment_list[p.equipment[response]].quantity += 1
                            if response == "Mainhand" or response == "Offhand" or response == "Special":
                                if p.equipment_list[p.equipment[response]].slot == "Both":
                                    b.equipment_swap("Mainhand", "Empty")
                                    b.equipment_swap("Offhand", "Empty")
                                else:
                                    b.equipment_swap(response, "Empty")
                            else:
                                b.equipment_swap(response, "None")
                    elif p.equipment_list[response2].quantity < 1:
                        print(f"You need at least 1 {p.equipment_list[response2].name} in your inventory to equip it.", 1)
                    elif p.equipment_list[response2].slot == response:
                        if p.equipment_list[p.equipment[response]].name != "Empty" and p.equipment_list[p.equipment[response]].name != "None":
                            print(f"You swapped out your {p.equipment[response]} for {p.equipment_list[response2].name}!", 1.5)
                            p.equipment_list[p.equipment[response]].quantity += 1
                        else:
                            print(f"You equipped a {p.equipment_list[response2].name}!", 1.5)
                        p.equipment_list[response2].quantity -= 1
                        if p.equipment_list[p.equipment[response]].slot == "Both" and response == "Mainhand":
                            b.equipment_swap("Offhand", "Empty")
                        if p.equipment_list[p.equipment[response]].slot == "Both" and response == "Offhand":
                            b.equipment_swap("Mainhand", "Empty")
                        b.equipment_swap(response, response2)
                    elif p.equipment_list[response2].slot == "Both" and (response == "Mainhand" or response == "Offhand"):
                        print(f"You equipped a {p.equipment_list[response2].name} in both your Mainhand and Offhand slots!", 1.5)
                        p.equipment_list[p.equipment["Mainhand"]].quantity = p.equipment_list[p.equipment["Mainhand"]].quantity + 1 if p.equipment_list[p.equipment["Mainhand"]].name != "Empty" else p.equipment_list[p.equipment["Mainhand"]].quantity
                        p.equipment_list[p.equipment["Offhand"]].quantity = p.equipment_list[p.equipment["Offhand"]].quantity + 1 if p.equipment_list[p.equipment["Offhand"]].name != "Empty" else p.equipment_list[p.equipment["Offhand"]].quantity
                        p.equipment_list[response2].quantity -= 1
                        b.equipment_swap("Mainhand", response2)
                        b.equipment_swap("Offhand", response2)
                    else:
                        print(f"That's the wrong slot for that item! The correct slot for {p.equipment_list[response2].name} is {p.equipment_list[response2].slot}.", 1)
                except Exception as e:
                    print("Invalid response, your response must be the name of a piece of equipment in your inventory.", 1)
            except:
                print("Invalid response, your response must be the name of a piece of currently equipped equipment.", 1)
        elif response == "Exit" or response == "3":
            break
        else:
            print("Invalid response, please enter one of the provided options. (You can also respond with the corresponding number to quickly choose a response)", 1)
    
def f_moves(): #prints out the players list of currently known moves
    f.header("Available Moves", 0.5)
    for i in player.moves:
        print(player.moves[i], 0.2)
    f.header("", 0.5)

def f_status_effects(): #prints out all status effects currently affecting the player
    f.header("Status Effects", 0.5)
    for item in player.statuses:
        print(s.statuses_list[item[0]], 0.3)
    if len(player.statuses) < 1:
        print("You don't have any status effects.", 0.5)
    f.header("", 0.5)

def f_travel(): #prints out list of all areas and allows the player to travel between them. Travelling time is determined by the players speed stat and the distance between the target location and the current area
    f.header("List of Areas", 0.5)
    for area in a.areas:
        print(a.areas[area], 0.3)
    f.header("", 0.3)
    response = f.capitalize(input("Where would you like to travel to? "))
    sleep(0.5)
    if response in a.areas:
        if a.areas[response].access == True:
            if a.areas[response] is p.current_area:
                print(f"You're already at {p.current_area.name}!", 0.5)
            else:
                print(f"You set out on the journey to {response}...", 3)
                a.areas[response].travel()
        else:
            print(f"You don't have access to \'{response}\'! {a.areas[response].denialmessage}")
    else:
        print(f"Unkown response \'{response}\'.")

def f_encyclopedia(): #Opens the players encyclopedia, which contains information on various subjects, mechanics, and tutorials. Some subjects will be available from the start of the game, where as others such as specific enemies will be unavailable until the player encounters them for the first time to avoid spoilers.
    y.check_encyclopedia()

#########################################
#               COMMANDS                #
#########################################

class Command: #simple class for the player commands system
    def __init__(self, name, description):
        self.name = name
        self.description = description
        commands_list[self.name] = self

    def __str__(self):
        return f"{self.name}: {self.description}."

    def __call__(self):
        globals()["f_"+"_".join(self.name.lower().split())]()

devcmds = Command("Devcmds", "Enter a developer command")
settings = Command("Settings", "View and change the game settings")
commands = Command("Commands", "Gives a list of all valid commands")
inventory = Command("Inventory", "Gives a list of all items in your inventory")
equipment = Command("Equipment", "Lets you inspect and change your equipment")
stats = Command("Stats", "Prints out your characters stats")
moves = Command("Moves", "Gives a list of all available moves in combat")
status_effects = Command("Status Effects", "Gives a list of all of your current status effects")
use = Command("Use", "Use a consumable item in your inventory while out of combat")
travel = Command("Travel", "Begin the journey to a different area")
encyclopedia = Command("Encyclopedia", "View information on various game subjects and mechanics")

#########################################
#             GAMEPLAY LOOP             #
#########################################

if f.capitalize(input("Do you want to skip the intro (Y/N)? ")) != "Y": #the story intro to the game and where the player chooses their name, gives the player the chance to skip it if they want, doing so defaults the player name to "Henry"
    sleep(1)
    print(f"Welcome to the grand, fantastical land of Myravolt, a land of both danger and opportunity.", 4.5)
    print(f"You are a young lad born in the quaint village of Chalgos, a secluded town in the middle of the Gavlynn Forest, and you've never known life outside it.", 6)
    print(f"However, you've never been quite satisfied with this life, you yearn for adventure and glory.", 3.5)
    print(f"So, armed with only your grandfather's old sword that he gave you on your 18th birthday, you decide today's finally the day you set off out into the great unknown...", 6)
    p.player_name = input("Enter your name: ")
    sleep(1)
    print(f"Now go off into the lands of Myravolt {p.player_name}, and best of luck to you!", 4)

while running == True and player.health > 0: #the main gameplay loop, the player can use various front end commands.
    b.hpcheck(player)
    sleep(0.5)
    response = f.capitalize(input("What would you like to do? "))
    try:
        sleep(0.5)
        if response in p.current_area.activities:
            activities_list[response](p.current_area)
        else:
            commands_list[response]()
    except Exception as e:
        print(e)
        print(f"Response \'{response}\' not recognized. Try \'Commands\' for a list of valid options.")
        
print("Game has ended.")
