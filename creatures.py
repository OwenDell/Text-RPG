#########################################
#               IMPORTS                 #
#########################################

import functions as f
import playerstats as p

#########################################
#           GLOBAL VARIABLES            #
#########################################

enemies = [] #a list of all enemies that gets filled every time a new creature is initialized. No purpose for it currently.
moves_list = {} #a dictionary of all player moves in the game that gets filled with they're initialized. The key is the string name of the move, and the value is the move class object itself, making it easy to call a desired move using the string input from the player.
test_dummy = ''

#########################################
#               CLASSES                 #
#########################################

class Creature:
    def __init__(self, name, level, XP, maxHP, gold, moves):
        self.name = name
        self.level = level
        self.XP = XP
        self.maxHP = maxHP
        self.health = maxHP
        self.gold = gold
        self.moves = moves
        enemies.append(self)
    
    def __str__(self):
        return f"Lvl: {self.level} {self.name}, with {self.health} HP!"
        
    def creature_attack(self, target): #randomly chooses an attack from the creatures attack pool. Takes into account the chance of the move to be chosen out of the total pool.
        f.weighted_random(self.moves)(self, target)
        
#########################################
#          BACK-END FUNCTIONS           #
#########################################
        
def basic_attack(move, user, target, message=f"attacked you"): #used for both creature and player attacks that don't have any special functions to them, and simply do damage.
    target.health -= move.damage
    if user is player:
        print(f"{message}, dealing {move.damage} damage!")
    elif target is player:
        print(f"The {user.name} {message}, dealing {move.damage} damage!")
    else:
        print(f"The {user.name} attacked the {target.name}, dealing {move.damage} damage!")
        
def player_move(target): #gets a move input from the player, checks if that move exists in the players list of known moves, and performs it if so.
    while True:
        response = input(f"You have {player.health}/{player.maxHP} HP and {p.mana}/{p.maxMana} Mana, what do you do? ")
        response = response[0].upper()+response[1:].lower()
        if response == "Options":
            moves_list[response](target)
        elif response in player.moves:
            try:
                moves_list[response](target)
                break
            except Exception as e:
                print(f"An error has occured [2].")
                print(e)
        else:
            print(f"Response \'{response}\' not recognized or unlearnt. Try \'options\' for a list of valid options.")

def dummy_init(dummy):
    return globals()[dummy]
        
#########################################
#            CREATURE MOVES             #
#########################################

class Claw:
    def __init__(self):
        self.damage = 10
        
    def __call__(self, user, target):
        basic_attack(self, user, target, f"gouged you with their claws")
        
class Bite:
    def __init__(self):
        self.damage = 20
        
    def __call__(self, user, target):
        basic_attack(self, user, target, f"bit your arm")
        
class Stab:
    def __init__(self):
        self.damage = 30
        
    def __call__(self, user, target):
        basic_attack(self, user, target, f"stabbed you in the torso")
        
#########################################
#             PLAYER MOVES              #
#########################################

class m_Options:
    def __init__(self):
        self.name = "Options"
        global moves_list
        moves_list[self.name] = self
        player.moves[self.name] = moves_list[self.name]
        
    def __str__(self):
        return f"{self.name}: Returns a list of all available actions you can take during combat."
        
    def __call__(self, target):
        global moves_list
        print("List of valid options:")
        for i in player.moves:
            print(player.moves[i])

class m_Execute:
    def __init__(self):
        self.name = "Execute"
        self.damage = 99999999999
        global moves_list
        moves_list[self.name] = self
        
    def __str__(self):
        return f"{self.name}: Deletes the enemy from existence."
        
    def __call__(self, target):
        global moves_list
        basic_attack(self, player, target, f"You deleted the {target.name}")
        
class m_Punch:
    def __init__(self):
        self.name = "Punch"
        self.damage = 5
        global moves_list
        moves_list[self.name] = self
        player.moves[self.name] = moves_list[self.name]
        
    def __str__(self):
        return f"{self.name}: A swift punch that deals {self.damage} damage."
        
    def __call__(self, target):
        global moves_list
        basic_attack(self, player, target, f"You punched the {target.name} in the face")
        
class m_Flee:
    def __init__(self):
        self.name = "Flee"
        global moves_list
        moves_list[self.name] = self
        player.moves[self.name] = moves_list[self.name]
        
    def __str__(self):
        return f"{self.name}: You attempt to flee combat."
        
    def __call__(self, target):
        global moves_list
        print(f"You fled from the enemy {target.name}!")

#########################################
#               CREATURES               #
#########################################

goblin = Creature("Goblin", 1, 10, 50, 35, [[Stab(), 70], [Claw(), 30], [Bite(), 50]])
dog = Creature("Dog", 3, 25, 200, 0, [[Claw(), 150], [Bite(), 80]])
player = Creature("Player", 1, 0, 100, 0, {})

temp_globals = globals().copy() #initializes all the player moves, which add themselves to a list of possible player moves
for globals_object in temp_globals:
    if globals_object[:2] == "m_":
        globals()[globals_object]()