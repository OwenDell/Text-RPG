#########################################
#               IMPORTS                 #
#########################################

import random
import functions as f
import playerstats as p

#########################################
#           GLOBAL VARIABLES            #
#########################################

enemies = [] #a list of all enemies that gets filled every time a new creature is initialized. No purpose for it currently.
moves_list = {} #a dictionary of all player moves in the game that gets filled with they're initialized. The key is the string name of the move, and the value is the move class object itself, making it easy to call a desired move using the string input from the player.
specials_list = {} #a dictionary of special moves that are stored separately from the normal moves, as the move in moves_list is what actually gets called by the player which then calls the version in specials_list

#########################################
#               CLASSES                 #
#########################################

class Creature:
    def __init__(self, name, level, XP, maxHP, gold, evasion, moves, intro):
        self.name = name
        self.level = level
        self.XP = XP
        self.maxHP = maxHP
        self.health = maxHP
        self.gold = gold
        self.evasion = evasion
        self.moves = moves
        self.intro = intro
        self.statuses = []
        enemies.append(self)
    
    def __str__(self):
        return f"Lvl: {self.level} {self.name}, with {self.health} HP!"
        
    def creature_attack(self, target): #randomly chooses an attack from the creatures attack pool. Takes into account the chance of the move to be chosen out of the total pool.
        moves_list[f.weighted_random(self.moves)](self, target)

#########################################
#          BACK-END FUNCTIONS           #
#########################################

def dummy_init(dummy):
    return globals()[dummy]

#########################################
#            INITIALIZATION             #
#########################################

""" #not necessary anymore but is being left here for reference sake.
temp_globals = globals().copy() 
for globals_object in temp_globals:
    if globals_object[:2] == "m_" or globals_object[:2] == "s_":
        globals()[globals_object]()
"""

#########################################
#               CREATURES               #
#########################################

player = Creature("Player", 1, 0, 100, 0, 0, {}, "You encountered... yourself?")
goblin = Creature("Goblin", 1, 10, 50, 35, 5, [["Stab", 70], ["Claw", 30], ["Bite", 50]], "You hear a rustle of leaves from a nearby bush... as you get closer to investigate, a goblin springs out, with a shortsword in its hand!")
wolf = Creature("Wolf", 2, 45, 150, 50, 10, [["Claw", 150], ["Bite", 80]], "You hear a deep, loud bark behind you... you turn to see a growling wolf with its teeth bared!")
skeleton_archer = Creature("Skeletal Archer", 2, 50, 80, 60, 0, [["Punch", 35], ["Bowshot", 65]], "An arrow suddenly strikes the ground right between your legs, and as you turn around you see a skeletal archer in the process of knocking another arrow!")
wwe_champ = Creature("WWE Champion", 5, 200, 200, 150, 10, [["Punch", 70], ["Uppercut", 30]], "You approach a mysterious boxing ring as smoke fills up around you... just as you get the feeling you've arrived somewhere you shouldn't be you hear a bell ring and a burly man emerges from the fog looking ready for bloodshed.") #used for testing purposes
elusive_ghost = Creature("Elusive Ghost", 3, 100, 30, 55, -1, [["Punch", 40], ["Claw", 40], ["Slash", 20]], "A swirling mist ahead of you congeals into a spectral figure... it's an elusive ghost! They're master of evasion!")
