#########################################
#               IMPORTS                 #
#########################################

import random
import functions as f
import playerstats as p
import creatures as c
import statuses as s

#########################################
#           GLOBAL VARIABLES            #
#########################################

print = f.print_override
player = c.player
moves_list = c.moves_list
specials_list = c.specials_list
statuses_list = s.statuses_list
basic_attack = f.basic_attack
test_dummy = ''
battling = False

#########################################
#               CLASSES                 #
#########################################

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
        damage_desc = f" that deals {self.damage} damage" if self.damage != -1 else ""
        accuracy_desc =  f" | {self.accuracy}% Accuracy" if self.accuracy != -1 else ""
        return f"{self.name}: {self.description}{damage_desc}. [Costs {self.mana} Mana{accuracy_desc}]"
        
    def __call__(self, user, target):
        global moves_list
        message = ["You", f"the {target.name}"] if user is player else [f"The {user.name}", "You"]
        if (random.randint(0, 100) <= self.accuracy-target.evasion and target.evasion != -1) or self.accuracy == -1:
            if len(self.special) <= 0:
                basic_attack(self, user, target, f"{message[0]} {self.verb} {message[1]}")
            else:
                specials_list[self.special](user, target, message)
        else:
            print(f"{message[0]} tried to use {self.name}, but it missed!")
        user.health, p.mana, p.energy, target.health = f.limit([user.health, p.mana, p.energy, target.health], [user.maxHP, p.maxMana, p.maxEnergy, target.maxHP])

#########################################
#          BACK-END FUNCTIONS           #
#########################################
     
def player_move(target): #gets a move input from the player, checks if that move exists in the players list of known moves, and performs it if so.
    while True:
        response = f.capitalize(input(f"You have {player.health}/{player.maxHP} HP and {p.mana}/{p.maxMana} Mana, what do you do? "))
        if response == "Options":
            moves_list[response](player, target)
        elif response in player.moves:
            try:
                if moves_list[response].mana <= p.mana:
                    p.mana -= moves_list[response].mana
                    moves_list[response](player, target)
                    break
                else:
                    print(f"You don't have enough Mana to use that move! it requires {moves_list[response].mana} Mana!")
            except Exception as e:
                moves_list[response](player, target)
                break
        else:
            print(f"Response \'{response}\' not recognized or unlearnt. Try \'options\' for a list of valid options.")
        player.health, p.mana, p.energy, target.health = f.limit([player.health, p.mana, p.energy, target.health], [player.maxHP, p.maxMana, p.maxEnergy, target.maxHP])

def heal(target): #heals the target back to full health
    target.health = target.maxHP

def fight(target): #starts a battle between the player and an enemy
    global battling
    battling = True
    turn_count = 1
    print(f"You begin battle with the enemy {target.name}!")
    while True:
        f.header(f"Battle with {target.name}: Turn {turn_count}")
        s.recur_statuses(player)
        if hpcheck(target) == True or battling == False:
            break
        player_move(target)
        if hpcheck(target) == True or battling == False:
            break
        s.recur_statuses(target)
        print(f"The enemy {target.name} has {target.health}/{target.maxHP} HP remaining.")
        if hpcheck(target) == True or battling == False:
            break
        target.creature_attack(player)
        if hpcheck(target) == True or battling == False:
            break
        turn_count += 1
    f.header()
    player.cures_list["Conclusion"] = True
    battling = False
    f.printing = False
    s.recur_statuses(target, True)
    f.printing = True
    s.cure_check(player)
    player.health, p.mana, p.energy, target.health = f.limit([player.health, p.mana, p.energy, target.health], [player.maxHP, p.maxMana, p.maxEnergy, target.maxHP])
    heal(target)

def hpcheck(target, checkup=False): #checks the hp of both the player and the target enemy, if one of their HP is at 0 then it ends the battle by returning True. Awards the target enemies xp and gold to the player if the player defeats them in combat.
    s.cure_check(player)
    s.cure_check(target)
    if player.health <= 0:
        if battling == True:
            print(f"You've been defeated in battle by the enemy {target.name}...")
            player.cures_list["Defeat"] = True
            return True
        print(f"You're too weak to carry on...")
    elif target.health <= 0:
        print(f"You defeated the enemy {target.name} in battle!")
        gold_gain = round(random.uniform(target.gold-target.gold*0.1, target.gold+target.gold*0.1))
        player.gold += gold_gain
        player.XP += target.XP
        print(f"You gained {gold_gain} gold and {target.XP} XP!")
        player.cures_list["Victory"] = True
        return True
    if checkup == True:
        print(f"HP of {target.name}: {target.health}/{target.maxHP}")

#########################################
#                 MOVES                 #
#########################################

class m_Options:
    def __init__(self):
        self.name = "Options"
        global moves_list
        moves_list[self.name] = self
        player.moves[self.name] = moves_list[self.name]
        
    def __str__(self):
        return f"{self.name}: Returns a list of all available actions you can take during combat."
        
    def __call__(self, player, target):
        global moves_list
        f.header("Available Actions")
        for i in player.moves:
            print(player.moves[i])
        f.header()
    
class m_Flee:
    def __init__(self):
        self.name = "Flee"
        global moves_list
        moves_list[self.name] = self
        player.moves[self.name] = moves_list[self.name]
        
    def __str__(self):
        return f"{self.name}: You attempt to flee combat."
        
    def __call__(self, player, target):
        global battling
        battling = False
        print(f"You fled from the enemy {target.name}!")
           
class m_Use:
    def __init__(self):
        self.name = "Use"
        global moves_list
        moves_list[self.name] = self
        player.moves[self.name] = moves_list[self.name]
        
    def __str__(self):
        return f"{self.name}: Use a consumable item."
        
    def __call__(self, player, target):
        p.inventory_check()
        try:
            response = p.items_list[f.capitalize(input("What item do you want to use? "))]
            if response.quantity >= 1:
                if response.affect == "Damage" and target is player:
                    print(f"You can't use a {response.name} on yourself!")
                elif (random.randint(0, 100) <= response.accuracy-target.evasion and target.evasion != -1) or response.accuracy == -1:
                    response.quantity -= 1
                    if response.affect != "":
                        player.health = player.health + response.val1 if response.affect == "Health" else player.health
                        p.mana = p.mana + response.val1 if response.affect == "Mana" else p.mana
                        p.energy = p.energy + response.val1 if response.affect == "Energy" else p.energy
                        target.health = target.health - response.val1 if response.affect == "Damage" else target.health
                        if response.action == "Potion":
                            print(f"You drank a {response.name}.")
                        else:
                            print(f"{response.action[0]} {response.name}, {response.action[1]} {response.val1} {response.action[2]}.")
                    for eff in response.effects:
                        eff_target = player if eff[2] == "user" else target
                        statuses_list[eff[0]].apply(eff_target, eff[1])
                else:
                    response.quantity -= 1
                    print(f"You tried to use {response.name}, but it missed!")
            else:
                print(f"You don't have any {response.name}'s!")
                if battling == True:
                    player_move(target)
        except:
            print("Unknown response.")
            if battling == True:
                player_move(target)
        player.health, p.mana, p.energy = f.limit([player.health, p.mana, p.energy], [player.maxHP, p.maxMana, p.maxEnergy])

#########################################
#               SPECIALS                #
#########################################

class s_Execute:
    def __init__(self):
        self.name = "Execute"
        self.damage = 99999999999
        specials_list[self.name] = self
        
    def __str__(self):
        return f"{self.name}: Deletes the enemy from existence."
        
    def __call__(self, user, target, message):
        global moves_list
        basic_attack(self, user, target, f"{message[0]} deleted {message[1]} from existence")
        
class s_Uppercut:
    def __init__(self):
        self.name = "Uppercut"
        self.damage = 50
        specials_list[self.name] = self
        
    def __str__(self):
        return f"{self.name}: A powerful uppercut that deals {self.damage} damage."
        
    def __call__(self, user, target, message):
        global moves_list
        basic_attack(self, user, target, f"{message[0]} struck {message[1]} with a powerful uppercut to the head")

class s_Bowshot: #in the future, make a separate bowshot MOVE for the player, where they choose what arrow to shoot and what effects it has.
    def __init__(self):
        self.name = "Bowshot"
        self.damage = 40
        self.accuracy = 50
        specials_list[self.name] = self
        
    def __str__(self):
        return f"{self.name}"
        
    def __call__(self, user, target, message):
        global moves_list
        hit_chance = random.randint(0, 100)
        if hit_chance+30 <= self.accuracy-target.evasion and target.evasion != -1:
            damage_dealt = round(self.damage*1.2)
            print(f"{message[0]} headshot {message[1]} with an arrow, dealing {damage_dealt} damage!")
        elif hit_chance <= self.accuracy-target.evasion and target.evasion != -1:
            damage_dealt = self.damage
            print(f"{message[0]} struck {message[1]} with an arrow, dealing {damage_dealt} damage!")
        elif hit_chance-30 <= self.accuracy-target.evasion and target.evasion != -1:
            damage_dealt = round(self.damage*.3)
            print(f"{message[0]} grazed {message[1]} with an arrow, dealing {damage_dealt} damage!")
        else:
            damage_dealt = 0
            print(f"{message[0]} shot at {message[1]}, but it completely missed!")
        target.health -= damage_dealt

#########################################
#            INITIALIZATION             #
#########################################

temp_globals = globals().copy() #initializes all the moves and specials, which add themselves to moves_list and specials_list
for globals_object in temp_globals:
    if globals_object[:2] == "m_" or globals_object[:2] == "s_":
        globals()[globals_object]()

#########################################
#               ATTACKS                 #
#########################################

punch = Attack(True, "Punch", "A quick punch with your fist", 10, 110, 0, "punched", "")
slash = Attack(True, "Slash", "A swift slash with your weapon", 20, 100, 0, "slashed", "")
stab = Attack(False, "Stab", "A harsh jab with your weapon", 30, 90, 5, "stabbed", "")
uppercut = Attack(False, "Uppercut", "A powerful uppercut", 50, 80, 10, "delivered a devastating uppercut to", "Uppercut")
execute = Attack(False, "Execute", "You delete the enemy from existence", -1, -1, 0, "executed", "Execute")
claw = Attack(False, "Claw", "A painful slash with your claws", 10, 90, 0, "clawed", "")
bite = Attack(False, "Bite", "A deadly bite with your fangs", 20, 85, 0, "bit", "")
bowshot = Attack(False, "Bowshot", "You shoot an arrow out of your bow", -1, -1, 0, "shot", "Bowshot")