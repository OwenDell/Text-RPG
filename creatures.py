#########################################
#               IMPORTS                 #
#########################################

import random
import functions as f
import playerstats as p

#########################################
#           GLOBAL VARIABLES            #
#########################################

print = f.print_override
sleep = f.sleep
enemies = [] #a list of all enemies that gets filled every time a new creature is initialized. No purpose for it currently.
moves_list = {} #a dictionary of all player moves in the game that gets filled with they're initialized. The key is the string name of the move, and the value is the move class object itself, making it easy to call a desired move using the string input from the player.
specials_list = {} #a dictionary of special moves that are stored separately from the normal moves, as the move in moves_list is what actually gets called by the player which then calls the version in specials_list

#########################################
#               CLASSES                 #
#########################################

class Creature: #The class for all creatures, including the player. Using the same class for both has some complications, and in a lot of cases it means that the variables don't entirely mean the same thing for the player vs enemies, but it works.
    def __init__(self, name, level, XP, maxHP, gold, evasion, moves, weaknesses, resistances, immunities, intro):
        self.name = name #name of the creature
        self.level = level #level of the creature, in the case of enemies this is just used to determine its difficulty.
        self.XP = XP #In the case of the player, this is how much XP they have to determine how close they are to levelling up. For enemies, this is how much XP they give when defeated by the player.
        self.maxHP = maxHP #The creatures maxHP, used for internal calculations to be reverted back to after battle or to limit overhealing.
        self.health = maxHP #The creatures health, this is the value that will change through a battle.
        self.gold = gold #Works the same way as XP, total gold for the player, and the amount of gold dropped in the case of enemies.
        self.evasion = evasion #Determines how likely it is for this creature to avoid getting hit by an attack.
        self.moves = moves #List of moves this creature can perform during combat, for the player this is actually a dictionary that will change throughout the game as the player learns new moves and changes out their gear.
        self.intro = intro #The intro text played when the player encounters this creature.
        self.weaknesses = weaknesses #List of damage types this creature is weak to, and will take 50% more damage from.
        self.resistances = resistances #List of damage types this creature is resistant to, and will take 50% less damage from.
        self.immunities = immunities #List of damage types this creature is immune to, and will take 100% less damage from.
        self.statuses = [] #List of statuses currently affecting this creature. Statuses come in the form of lists, where the first part is the name of the status, and the second part is the duration.
        self.cures_list = { #Dictionary of status cures this creature has access to. If the creature is impacted by a status and one of it's cures are in here as True, then they will be cured of it. This is stored here as it can't be universal or else the player using an antidote would trigger the enemy to be cured of their poison or visa versa.
            "Conclusion": False,
            "Victory": False,
            "Defeat": False,
            "Cleanse": False,
            "Saturated": True,
            "Lesser Antidote": False,
            "Antidote": False
        }
        self.damage_affinities = { #Dictionary of every damage type and this creatures 'affinity' for it. Affinity impacts how much damage they do with this damage type. For now they are all at base of 1 and will only change due to statuses or player upgrades, but in the future it may be changed so this can be vary between creatures who do more damage with different damage types.
            "Physical": 1,
            "Slash": 1,
            "Pierce": 1,
            "Blunt": 1,
            "Magic": 1,
            "Fire": 1,
            "Lightning": 1,
            "Holy": 1,
            "Dark": 1
        }
        enemies.append(self)
    
    def __str__(self):
        return f"Lvl: {self.level} {self.name}, with {self.health} HP!"
        
    def creature_attack(self, target): #randomly chooses an attack from the creatures attack pool. Takes into account the chance of the move to be chosen out of the total pool.
        moves_list[f.weighted_random(self.moves)](self, target)

#########################################
#          BACK-END FUNCTIONS           #
#########################################

def dummy_init(dummy): #Sets the dummy to any creature in the game so it can be fought using developer commands. Used for testing purposes.
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

player = Creature("Player", 1, 0, 100, 0, 0, {}, [], [], [], "You encountered... yourself?")
goblin = Creature("Goblin", 1, 10, 50, 35, 5, [["Stab", 30], ["Claw", 70], ["Bite", 50]], [], [], [], "You hear a rustle of leaves from a nearby bush... as you get closer to investigate, a goblin springs out, with a shortsword in its hand!")
wolf = Creature("Wolf", 2, 45, 150, 50, 10, [["Claw", 150], ["Bite", 80]], ["Fire"], [], [], "You hear a deep, loud bark behind you... you turn to see a growling wolf with its teeth bared!")
skeleton_archer = Creature("Skeletal Archer", 2, 50, 80, 60, 0, [["Punch", 35], ["Bowshot", 65]], ["Holy", "Blunt"], ["Slash", "Fire"], ["Dark"], "An arrow suddenly strikes the ground right between your legs, and as you turn around you see a skeletal archer in the process of knocking another arrow!")
wwe_champ = Creature("WWE Champion", 5, 200, 200, 150, 10, [["Punch", 70], ["Uppercut", 30]], ["Slash"], ["Blunt"], [], "You approach a mysterious boxing ring as smoke fills up around you... just as you get the feeling you've arrived somewhere you shouldn't be you hear a bell ring and a burly man emerges from the fog looking ready for bloodshed.") #used for testing purposes
elusive_ghost = Creature("Elusive Ghost", 3, 100, 30, 55, 15, [["Punch", 40], ["Claw", 40], ["Slash", 20]], ["Holy", "Magic"], ["Dark", "Fire"], ["Physical", "Slash", "Pierce", "Blunt"], "A swirling mist ahead of you congeals into a spectral figure... it's an elusive ghost! They can't be damaged by normal means!")
bandit = Creature("Bandit", 2, 25, 70, 50, 0, [["Stab", 50], ["Slash", 70], ["Bowshot", 20], ["Punch", 30]], [], [], [], "As your walking along a dirt path a grizzled man jumps out from behind a tree in front of you! 'Surrender your posessions or die!' he shouts at you. He gives you a mean snear as you draw your weapon...")