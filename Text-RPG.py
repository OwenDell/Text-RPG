#########################################
#               IMPORTS                 #
#########################################

import random
from inspect import signature
import functions as f
import playerstats as p
import creatures as c
import areas as a

#########################################
#           GLOBAL VARIABLES            #
#########################################

player = c.player
moves_list = c.moves_list
dummy = c.goblin
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
    try:
        player.moves[move_name] = moves_list[move_name]
        print(f"You learned {move_name}!")
    except:
        print(f"Unrecognized move: \'{move_name}\'.")
    
def heal(target): #heals the target back to full health
    target.health = target.maxHP
    #print(f"{target.name} has been fully healed to {target.health} HP!")
    
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

def fight(target): #starts a battle between the player and an enemy
    global battling
    battling = True
    print(f"You begin battle with the enemy {target.name}!")
    while True:
        c.player_move(target)
        print(f"The enemy {target.name} has {target.health}/{target.maxHP} HP remaining!")
        if hpcheck(target) == True:
            break
        target.creature_attack(player)
        if hpcheck(target) == True:
            break
    battling = False
    heal(target)

def hpcheck(target, checkup=False): #checks the hp of both the player and the target enemy, if one of their HP is at 0 then it ends the battle by returning True. Awards the target enemies xp and gold to the player if the player defeats them in combat.
    if player.health <= 0:
        if battling == True:
            print(f"You've been defeated in battle by the enemy {target.name}!")
            return True
        print(f"You're too weak to carry on...")
    elif target.health <= 0:
        print(f"You defeated the enemy {target.name} in battle!")
        player.gold += target.gold
        player.XP += target.XP
        print(f"You gained {target.gold} gold and {target.XP} XP!")
        return True
    if checkup == True:
        print(f"HP of {target.name}: {target.health}/{target.maxHP}")

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
        except:
            print("An error has occurred [1].")
    except:
        print("Unrecognized command.")
        
def f_commands(): #prints a list of all the front-end functions to the player, with the exception of devcmds (devcmds must be the first of the front-end functions to be initialized for this to work)
    commands_list = []
    for globals_object in globals():
        if globals_object[:2] == "f_":
            commands_list.append(globals_object[2:])
    print(f"""List of valid commands:\n{", ".join(commands_list[1:])}""")

#########################################
#             GAMEPLAY LOOP             #
#########################################

while running == True:
    response = "f_" + input("What would you like to do? ")
    try:
        globals()[response.lower()]()
    except:
        print(f"Response \'{response[2:]}\' not recognized. Try \'commands\' for a list of valid options.")
        
print("Game has ended.")