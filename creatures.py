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
specials_list = {} #a dictionary of special moves that are stored separately from the normal moves, as the move in moves_list is what actually gets called by the player which then calls the version in specials_list
test_dummy = ''
battling = False

#########################################
#               CLASSES                 #
#########################################

class Creature:
    def __init__(self, name, level, XP, maxHP, gold, moves, intro):
        self.name = name
        self.level = level
        self.XP = XP
        self.maxHP = maxHP
        self.health = maxHP
        self.gold = gold
        self.moves = moves
        self.intro = intro
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
                if moves_list[response].mana <= p.mana:
                    p.mana -= moves_list[response].mana
                    moves_list[response](target)
                    break
                else:
                    print(f"You don't have enough Mana to use that move! it requires {moves_list[response].mana} Mana!")
            except Exception as e:
                moves_list[response](target)
                break
        else:
            print(f"Response \'{response}\' not recognized or unlearnt. Try \'options\' for a list of valid options.")

def heal(target): #heals the target back to full health
    target.health = target.maxHP
    #print(f"{target.name} has been fully healed to {target.health} HP!")

def dummy_init(dummy):
    return globals()[dummy]

def fight(target): #starts a battle between the player and an enemy
    global battling
    battling = True
    print(f"You begin battle with the enemy {target.name}!")
    while True:
        player_move(target)
        if hpcheck(target) == True or battling == False:
            break
        print(f"The enemy {target.name} has {target.health}/{target.maxHP} HP remaining!")
        target.creature_attack(player)
        if hpcheck(target) == True or battling == False:
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

class s_Execute:
    def __init__(self):
        self.name = "Execute"
        self.damage = 99999999999
        specials_list[self.name] = self
        
    def __str__(self):
        return f"{self.name}: Deletes the enemy from existence."
        
    def __call__(self, target):
        global moves_list
        basic_attack(self, player, target, f"You deleted the {target.name}")
        
class s_Lunch:
    def __init__(self):
        self.name = "Lunch"
        self.damage = 50
        specials_list[self.name] = self
        
    def __str__(self):
        return f"{self.name}: A swift lunch that deals {self.damage} damage."
        
    def __call__(self, target):
        global moves_list
        basic_attack(self, player, target, f"You lunched the {target.name} in the face")
        
class Attack:
    def __init__(self, learned, name, description, damage, accuracy, mana, verb, special):
        self.learned = learned
        self.name = name
        self.description = description
        self.damage = damage
        self.accuracy = accuracy
        self.mana = mana
        self.verb = verb
        self.special = special
        global moves_list
        moves_list[self.name] = self
        if self.learned == True:
            player.moves[self.name] = moves_list[self.name]
        
    def __str__(self):
        return f"{self.name}: {self.description} that deals {self.damage} damage. [{self.mana} Mana]"
        
    def __call__(self, target):
        global moves_list
        if len(self.special) <= 0:
            basic_attack(self, player, target, f"{self.verb} {target.name}")
        else:
            specials_list[self.special](target)
        
class m_Flee:
    def __init__(self):
        self.name = "Flee"
        global moves_list
        moves_list[self.name] = self
        player.moves[self.name] = moves_list[self.name]
        
    def __str__(self):
        return f"{self.name}: You attempt to flee combat."
        
    def __call__(self, target):
        global battling
        battling = False
        print(f"You fled from the enemy {target.name}!")

#########################################
#               CREATURES               #
#########################################

goblin = Creature("Goblin", 1, 10, 50, 35, [[Stab(), 70], [Claw(), 30], [Bite(), 50]], "You hear a rustle of leaves from a nearby bush... as you get closer to investigate, a goblin springs out, with a shortsword in its hand!")
wolf = Creature("Wolf", 3, 25, 200, 0, [[Claw(), 150], [Bite(), 80]], "You hear a deep, loud bark behind you... you turn to see a growling wolf with its teeth bared!")
player = Creature("Player", 1, 0, 100, 0, {}, "You encountered... yourself?")

#########################################
#               ATTACKS                 #
#########################################

slash = Attack(True, "Slash", "A swift slash with your weapon", 20, 100, 0, "You slashed the", "")
stab = Attack(False, "Stab", "A harsh jab with your weapon", 30, 80, 5, "You stabbed the", "")
punch = Attack(True, "Punch", "A quick punch with your first", 10, 100, 0, "You punched the", "")
lunch = Attack(False, "Lunch", "Eat this", 50, 50, 10, "You fed the", "Lunch")
execute = Attack(False, "Execute", "Execute this", -1, 100, 0, "You executed the", "Execute")

#########################################
#            INITIALIZATION             #
#########################################

temp_globals = globals().copy() #initializes all the player moves, which add themselves to a list of possible player moves
for globals_object in temp_globals:
    if globals_object[:2] == "m_" or globals_object[:2] == "s_":
        globals()[globals_object]()
