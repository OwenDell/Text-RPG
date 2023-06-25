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
sleep = f.sleep
player = c.player
moves_list = c.moves_list
specials_list = c.specials_list
statuses_list = s.statuses_list
battling = False #boolean for whether the player is currently engaged in combat, necessary for a few function checks.

#########################################
#          BACK-END FUNCTIONS           #
#########################################

def calculate_damage(move, user, target, weapon, print_crit=False): #calculates the amount of damage to be done to a target based on multiple factors such as the move, the users damage affinity multipliers, the users weapon, and critical hit bonuses
    if weapon.name == "Empty":
        damage = move.damage*user.damage_affinities[move.damagetype]*target.damage_resistances[move.damagetype]
    else:
        damage = 0
        for i, dmg in enumerate(weapon.damages):
            bonus = 0
            if dmg == move.damagetype:
                bonus += move.bonusdamage
            elif i <= 3:
                continue
            damage = damage+((weapon.damages[dmg]+bonus)*target.damage_resistances[dmg]*user.damage_affinities[dmg])
    damage = round(damage)
    critchance = move.critchance+weapon.critchance+p.effective_dexterity if user is player else move.critchance+weapon.critchance
    if random.randint(0, 100) <= critchance and move.critchance != -1:
        returnval = [round(damage*weapon.critmultiplier), " (CRITICAL HIT)"] if print_crit == True else round(damage*weapon.critmultiplier)
    else:
        returnval = [damage, ""] if print_crit == True else damage
    return returnval

def basic_attack(move, user, target, weapon, message=f"the attacker attacked"): #used for both creature and player attacks that don't have any special functions to them, and simply do damage.
        damage, critmsg = calculate_damage(move, user, target, weapon, True)
        target.health -= damage
        print(f"{message}, dealing {damage} damage!{critmsg}")

#########################################
#               CLASSES                 #
#########################################

class Attack: #class for every basic attack in the game used by both enemies and players.
    def __init__(self, learned, name, description, damage, bonusdamage, damagetype, accuracy, critchance, mana, energy, verb, special):
        self.learned = learned #Bool for whether the player has learned this move, meaning it will remain permanently available to them regardless of it's association to equipped weapons. New moves can be learned through events, tutors, or using spell scrolls.
        self.name = name #The name of the attack.
        self.description = description #The description of the attack.
        self.damage = damage #The amount of damage the attack does while unassociated with any weapon. This means if the player has learned the move and doesn't have a weapon that supersecedes it, or for enemies using this move who don't have equipped weapons.
        self.bonusdamage = bonusdamage #The bonus damage added to the attack only weapon associated with a weapon. The bonus damage will be applied in the form of the moves damagetype
        self.damagetype = damagetype #The damage type of this move, if unassociated to a weapon then this will just be the form of damage that the moves damage stat comes in. If it is associated to a weapon then this is the type of physical damage it will use from that weapon, or apply this moves bonus damage if not physical to the associated elemental damage.
        self.accuracy = accuracy #The % chance for the move to hit the target. Accuracy is not the only factor, the associated weapons bonus accuracy, the targets evasion, the players stats, and any effects on either side will also have an impact. An accuracy of -1 means the move is guaranteed to hit/activate
        self.critchance = critchance #The % chance for the move to be a critical hit, in which case the associated weapons critical multiplier will be applied to all damage dealt (usually 1.5x).
        self.mana = mana #The mana cost of using this move, does not apply to enemies.
        self.energy = energy #The energy cost of using this move, does not apply to enemies.
        self.verb = verb #The verb that will be printed when using this move.
        self.special = special #The special move that will be used instead of a basic attack when this attack is used (if any).
        self.associated_weapon = p.empty #The associated weapon of this move, necessary for many of the stats when using the move. The associated weapon is by default empty, which applies no bonuses and has baseline stats for the attack to function, and is used when enemies attack as they don't have weapons, and if the player learns a move without associating a weapon to it.
        moves_list[self.name] = self 
        if self.learned == True:
            player.moves[self.name] = moves_list[self.name]
        
    def __str__(self):
        damage_desc = f"that deals {self.damage} {self.damagetype} damage" if self.damage != -1 and self.associated_weapon is p.empty else f"that does {self.damagetype} damage"
        accuracy_desc =  f" | {self.accuracy}% Accuracy" if self.accuracy != -1 else ""
        return f"{self.name}: {self.description} {damage_desc}. [{self.critchance}% Critical Chance{accuracy_desc}] (Costs {self.mana} Mana & {self.energy} Energy)"
        
    def __call__(self, user, target): #called when either the player or an enemy uses an attack, and goes through all the associated procedures to see if it will hit, if it crits, applying damage and potentially any special effects.
        global moves_list
        weapon = self.associated_weapon if user is player else p.empty #the associated weapon will always be empty for enemies
        message = ["You", f"the {target.name}"] if user is player else [f"The {user.name}", "You"]
        accuracy = self.accuracy+weapon.accuracy+(p.effective_dexterity*2) if user is player else self.accuracy+weapon.accuracy
        f.encyclopedia["Moves"][self.name] = self
        if (random.randint(0, 100) <= (accuracy)-target.evasion and target.evasion != -1) or self.accuracy == -1: #-1 accuracy means the move is unmissable, and takes precedence over the targets -1 evasion, which means the target is unhittable.
            if len(self.special) <= 0:
                basic_attack(self, user, target, weapon, f"{message[0]} {self.verb} {message[1]}")
            else:
                specials_list[self.special](user, target, weapon, message)
            sleep(0.4)
        else:
            print(f"{message[0]} tried to use {self.name}, but it missed!", 0.3)
        user.health, p.mana, p.energy, target.health = f.limit([user.health, p.mana, p.energy, target.health], [user.maxHP, p.maxMana, p.maxEnergy, target.maxHP])

#########################################
#          BACK-END FUNCTIONS           #
#########################################
     
def player_move(target): #gets a move input from the player, checks if that move exists in the players list of known moves, and performs it if so.
    while True:
        response = f.capitalize(input(f"You have {player.health}/{player.maxHP} HP and {p.mana}/{p.maxMana} Mana, what do you do? "))
        sleep(0.5)
        if response == "Options" or response == "Encyclopedia":
            moves_list[response](player, target)
        elif response in player.moves:
            try:
                if moves_list[response].mana <= p.mana:
                    if moves_list[response].energy <= p.energy:
                        p.energy -= moves_list[response].energy
                        p.mana -= moves_list[response].mana
                        moves_list[response](player, target)
                        break
                    else:
                        print(f"You don't have enough Energy to use that move! it requires {moves_list[response].energy} Energy!", 1)
                else:
                    print(f"You don't have enough Mana to use that move! it requires {moves_list[response].mana} Mana!", 1)
            except Exception as e:
                moves_list[response](player, target)
                break
        else:
            print(f"Response \'{response}\' not recognized or unlearnt. Try \'options\' for a list of valid options.", 0.7)
        player.health, p.mana, p.energy, target.health = f.limit([player.health, p.mana, p.energy, target.health], [player.maxHP, p.maxMana, p.maxEnergy, target.maxHP])

def heal(target): #heals the target back to full health
    target.health = target.maxHP

def fight(target): #starts a battle between the player and an enemy. The battle only ends if either side reaches 0 HP or flees combat.
    global battling
    battling = True
    turn_count = 1
    print(f"You begin battle with the enemy {target.name}!", 1.5)
    f.encyclopedia["Enemies"][target.name] = target
    while True:
        f.header(f"Battle with {target.name}: Turn {turn_count}", 0.7)
        s.recur_statuses(player)
        sleep(0.25)
        if hpcheck(target) == True or battling == False:
            break
        player_move(target)
        sleep(0.5)
        if hpcheck(target) == True or battling == False:
            break
        s.recur_statuses(target)
        sleep(0.25)
        print(f"The enemy {target.name} has {target.health}/{target.maxHP} HP remaining.", 1)
        if hpcheck(target) == True or battling == False:
            break
        target.creature_attack(player)
        sleep(1)
        if hpcheck(target) == True or battling == False:
            break
        turn_count += 1
    f.header("", 1.3)
    player.cures_list["Conclusion"] = True
    battling = False
    f.printing = False
    s.recur_statuses(target, True)
    f.printing = True
    s.cure_check(player)
    player.health, p.mana, p.energy, target.health = f.limit([player.health, p.mana, p.energy, target.health], [player.maxHP, p.maxMana, p.maxEnergy, target.maxHP])
    heal(target)

def hpcheck(target, checkup=False): #checks the hp of both the player and the target enemy, if one of their HP is at 0 then it ends the battle by returning True. Awards the target enemies xp and gold to the player if the player defeats them in combat. Also checks if any cures are applicable for any current status effects.
    if p.energy <= 0:
        player.cures_list["Saturated"] = False
        existed = False
        for eff in player.statuses:
            if eff[0] == s.exhaustion.name:
                existed = True
        if not existed:
            s.exhaustion.apply(player, -1)
    else:
        player.cures_list["Saturated"] = True
    s.cure_check(player)
    s.cure_check(target)
    c.level_up()
    player.maxHP = 100+20*p.effective_vitality
    p.maxMana = 20+(10*(p.effective_faith+p.effective_intelligence))+p.maxMana_buff
    p.maxEnergy = 100+(10*p.effective_dexterity)
    player.evasion = 2*p.effective_dexterity
    player.damage_affinities = {
        "Physical": 1+(.1*p.effective_strength)+p.dmg_affinity_buffs["Physical"],
        "Slash": 1+(.1*p.effective_strength)+p.dmg_affinity_buffs["Slash"],
        "Pierce": 1+(.1*p.effective_strength)+p.dmg_affinity_buffs["Pierce"],
        "Blunt": 1+(.1*p.effective_strength)+p.dmg_affinity_buffs["Blunt"],
        "Magic": 1+(.2*p.effective_intelligence)+p.dmg_affinity_buffs["Magic"],
        "Fire": 1+(.1*p.effective_faith)+(.1*p.effective_intelligence)+p.dmg_affinity_buffs["Fire"],
        "Lightning": 1+(.2*p.effective_faith)+p.dmg_affinity_buffs["Lightning"],
        "Holy": 1+(.2*p.effective_faith)+p.dmg_affinity_buffs["Holy"],
        "Dark": 1+(.2*p.effective_intelligence)+p.dmg_affinity_buffs["Dark"],
        "True": 1+p.dmg_affinity_buffs["True"]
    }
    player.health, p.mana, p.energy = f.limit([player.health, p.mana, p.energy], [player.maxHP, p.maxMana, p.maxEnergy])
    for item in p.items_list:
        if p.items_list[item].quantity > 0:
            if item in p.weapons_list:
                f.encyclopedia["Weapons"][item] = p.items_list[item]
            elif item in p.armor_list:
                f.encyclopedia["Armor"][item] = p.items_list[item]
            else:
                f.encyclopedia["Items"][item] = p.items_list[item]
    for move in player.moves:
        f.encyclopedia["Moves"][move] = moves_list[move]
    if player.health <= 0:
        sleep(0.3)
        if battling == True:
            print(f"You've been defeated in battle by the enemy {target.name}...", 0.7)
            player.cures_list["Defeat"] = True
            return True
        print(f"You're too weak to carry on...", 0.5)
    elif target.health <= 0:
        sleep(1.2)
        print(f"You defeated the enemy {target.name} in battle!", 1.5)
        gold_gain = round(random.uniform(target.gold-target.gold*0.1, target.gold+target.gold*0.1))
        player.gold += gold_gain
        player.XP += (target.XP*p.xp_gain_multiplier)
        print(f"You gained {gold_gain} gold and {target.XP*p.xp_gain_multiplier} XP!", 1)
        player.cures_list["Victory"] = True
        return True
    if checkup == True:
        print(f"HP of {target.name}: {target.health}/{target.maxHP}")

def equipment_swap(slot, equipment): #Goes through the procedure when the player swaps out a piece of equipment throught the equipment command. Removes any moves from the players move list that were tied to the old weapon, and gives any moves tied to the new one. 
    for buff in p.equipment_list[equipment].buffs:
        s.buffs_list[buff[0]].add(buff[1])
    for buff in p.equipment_list[p.equipment[slot]].buffs:
        s.buffs_list[buff[0]].remove(buff[1])
    if slot == "Mainhand" or slot == "Offhand" or slot == "Special":
        for attack in moves_list:
            try:
                if moves_list[attack].associated_weapon == p.equipment_list[p.equipment[slot]]:
                    if attack in p.equipment_list[p.equipment["Mainhand"]].moves and slot != "Mainhand":
                        moves_list[attack].associated_weapon = p.equipment_list[p.equipment["Mainhand"]]
                    elif attack in p.equipment_list[p.equipment["Offhand"]].moves and slot != "Offhand":
                        moves_list[attack].associated_weapon = p.equipment_list[p.equipment["Offhand"]]
                    elif attack in p.equipment_list[p.equipment["Special"]].moves and slot != "Special":
                        moves_list[attack].associated_weapon = p.equipment_list[p.equipment["Special"]]
                    else:
                        moves_list[attack].associated_weapon = p.empty
                        if not moves_list[attack].learned:
                            player.moves.pop(attack)
            except:
                pass
        for attack in p.equipment_list[equipment].moves:
            if (moves_list[attack].associated_weapon is p.empty and not moves_list[attack].learned) or moves_list[attack].associated_weapon.name == equipment:
                moves_list[attack].associated_weapon = p.equipment_list[equipment]
                player.moves[attack] = moves_list[attack]
            else: #gives the player the choice to leave the attack bound to another weapon if that move is already known by the player either through a different weapon or it's learned
                if moves_list[attack].learned:
                    print(f"{p.equipment_list[equipment].name} has the move {moves_list[attack].name}, however you've already learned that move, would you like to rebind it to {p.equipment_list[equipment].name}?", 1.5)
                else:
                    print(f"{p.equipment_list[equipment].name} has the move {moves_list[attack].name}, however that move is already bound to {moves_list[attack].associated_weapon.name}, would you like to rebind it to {p.equipment_list[equipment].name}?", 1.5)
                while True:
                    response = f.capitalize(input(f"Enter either (1) 'Yes' to rebind the move to {p.equipment_list[equipment].name}, or (2) 'No' to leave it as it is: "))
                    sleep(0.5)
                    if response == "Yes" or response == "1":
                        print(f"{moves_list[attack].name} has been rebound to {p.equipment_list[equipment].name}.", 0.8)
                        moves_list[attack].associated_weapon = p.equipment_list[equipment]
                        break
                    elif response == "No" or response == "2":
                        print(f"{moves_list[attack].name} will remain bound to {moves_list[attack].associated_weapon.name}.", 0.8)
                        break
                    else:
                        print("Invalid response, please enter one of the provided options. (You can also respond with the corresponding number to quickly choose a response)", 1)
    else:
        for resistance in player.damage_resistances:
            player.damage_resistances[resistance] -= p.equipment_list[equipment].resistances[resistance]
            player.damage_resistances[resistance] += p.equipment_list[p.equipment[slot]].resistances[resistance]
    p.equipment[slot] = equipment
    hpcheck(player)

#########################################
#                 MOVES                 #
#########################################

class m_Options: #prints a list of all available moves and actions the player can take in combat. Does not use up the players turn.
    def __init__(self):
        self.name = "Options"
        global moves_list
        moves_list[self.name] = self
        player.moves[self.name] = moves_list[self.name]
        
    def __str__(self):
        return f"{self.name}: Returns a list of all available actions you can take during combat."
        
    def __call__(self, player, target):
        global moves_list
        f.header("Available Actions", 0.5)
        for i in player.moves:
            print(player.moves[i], 0.2)
        f.header("", 0.5)

class m_Encyclopedia: #prints a list of all available moves and actions the player can take in combat. Does not use up the players turn.
    def __init__(self):
        self.name = "Encyclopedia"
        global moves_list
        moves_list[self.name] = self
        player.moves[self.name] = moves_list[self.name]
        
    def __str__(self):
        return f"{self.name}: Views the encylopedia entry of the target enemy."
        
    def __call__(self, player, target):
        global moves_list
        f.check_encyclopedia(target.name, "Enemies")
    
class m_Flee: #Attempts to flee from combat, odds of success is 50% chance + the players evasion - the enemies evasion.
    def __init__(self):
        self.name = "Flee"
        global moves_list
        moves_list[self.name] = self
        player.moves[self.name] = moves_list[self.name]
        
    def __str__(self):
        return f"{self.name}: You attempt to flee combat."
        
    def __call__(self, player, target):
        global battling
        if random.randint(0, 100) <= 50+(player.evasion-target.evasion):
            battling = False
            print(f"You successfully fled combat from the enemy {target.name}!", 2)
        else:
            print(f"You tried to escape the enemy {target.name}, but they caught you!", 2)
           
class m_Use: #use a consumable item, which can be something simple that affects mana, energy, or health, or something more complex that applies a status effect.
    def __init__(self):
        self.name = "Use"
        global moves_list
        moves_list[self.name] = self
        player.moves[self.name] = moves_list[self.name]
        
    def __str__(self):
        return f"{self.name}: Use a consumable item."
        
    def __call__(self, player, target):
        p.inventory_check(0.1, "Consumables")
        try:
            response = p.consumables_list[f.capitalize(input("What item do you want to use? "))]
            sleep(0.5)
            if response.quantity >= 1:
                if response.affect == "Damage" and target is player:
                    print(f"You can't use a {response.name} on yourself!", 0.7)
                elif (random.randint(0, 100) <= response.accuracy+(p.effective_dexterity*2)-target.evasion and target.evasion != -1) or response.accuracy == -1:
                    response.quantity -= 1
                    if response.affect != "":
                        player.health = player.health + response.val1 if response.affect == "Health" else player.health
                        p.mana = p.mana + response.val1 if response.affect == "Mana" else p.mana
                        p.energy = p.energy + response.val1 if response.affect == "Energy" else p.energy
                        target.health = target.health - response.val1 if response.affect == "Damage" else target.health
                        if response.affect == "Spell":
                            player.moves[response.val1] = moves_list[response.val1]
                            moves_list[response.val1].learned = True
                        if response.action == "Potion":
                            print(f"You drank a {response.name}.", 1)
                        else:
                            print(f"{response.action[0]} {response.name}, {response.action[1]} {response.val1}{response.action[2]}.", 1.5)
                    for eff in response.effects:
                        eff_target = player if eff[2] == "user" else target
                        statuses_list[eff[0]].apply(eff_target, eff[1])
                else:
                    response.quantity -= 1
                    print(f"You tried to use {response.name}, but it missed!", 1)
            else:
                print(f"You don't have any {response.name}'s!", 0.8)
                if battling == True:
                    player_move(target)
        except:
            sleep(0.5)
            print("Unknown response.", 0.6)
            if battling == True:
                player_move(target)
        player.health, p.mana, p.energy = f.limit([player.health, p.mana, p.energy], [player.maxHP, p.maxMana, p.maxEnergy])

#########################################
#               SPECIALS                #
#########################################

class s_Execute: #instantly kills the target, developer command used for testing
    def __init__(self):
        self.name = "Execute"
        self.damage = 99999999999
        self.damagetype = "Magic"
        self.critchance = -1
        specials_list[self.name] = self
        
    def __str__(self):
        return f"{self.name}: Deletes the enemy from existence."
        
    def __call__(self, user, target, weapon, message):
        global moves_list
        basic_attack(self, user, target, weapon, f"{message[0]} deleted {message[1]} from existence")
        
class s_Uppercut:
    def __init__(self):
        self.name = "Uppercut"
        self.damage = 50
        self.damagetype = "Blunt"
        self.critchance = 20
        specials_list[self.name] = self
        
    def __str__(self):
        return f"{self.name}: A powerful uppercut that deals {self.damage} damage."
        
    def __call__(self, user, target, weapon, message):
        global moves_list
        basic_attack(self, user, target, weapon, f"{message[0]} struck {message[1]} with a powerful uppercut to the head")

class s_Bowshot: #in the future, make a separate bowshot MOVE for the player, where they choose what arrow to shoot and what effects it has.
    def __init__(self):
        self.name = "Bowshot"
        self.damage = 30
        self.damagetype = "Pierce"
        self.critchance = -1
        self.accuracy = 50
        specials_list[self.name] = self
        
    def __str__(self):
        return f"{self.name}"
        
    def __call__(self, user, target, weapon, message):
        global moves_list
        hit_chance = random.randint(0, 100)
        if hit_chance+30 <= self.accuracy-target.evasion and target.evasion != -1:
            damage_dealt = round(calculate_damage(self, user, target, weapon)*1.2)
            print(f"{message[0]} headshot {message[1]} with an arrow, dealing {damage_dealt} damage!")
        elif hit_chance <= self.accuracy-target.evasion and target.evasion != -1:
            damage_dealt = calculate_damage(self, user, target, weapon)
            print(f"{message[0]} struck {message[1]} with an arrow, dealing {damage_dealt} damage!")
        elif hit_chance-30 <= self.accuracy-target.evasion and target.evasion != -1:
            damage_dealt = round(calculate_damage(self, user, target, weapon)*.3)
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

punch = Attack(True, "Punch", "A quick punch with your fist", 10, 3, "Blunt", 110, 5, 0, 0, "punched", "")
slash = Attack(False, "Slash", "A sharp slash with your weapon", 20, 3, "Slash", 100, 8, 0, 0, "slashed", "")
stab = Attack(False, "Stab", "A piercing jab with your weapon", 25, 5, "Pierce", 85, 12, 0, 0, "stabbed", "")
bash = Attack(False, "Bash", "A crushing bash with your weapon", 15, 3, "Blunt", 95, 5, 0, 0, "bashed", "")
uppercut = Attack(False, "Uppercut", "A powerful uppercut", 50, 20, "Blunt", 80, 20, 15, 0, "delivered a devastating uppercut to", "Uppercut")
execute = Attack(False, "Execute", "You delete the enemy from existence", -1, 999999, "Physical", -1, 0, 0, 0, "executed", "Execute")
claw = Attack(False, "Claw", "A painful slash with your claws", 10, 10, "Slash", 90, 10, 0, 0, "clawed", "")
bite = Attack(False, "Bite", "A deadly bite with your fangs", 20, 15, "Pierce", 85, 7, 0, 0, "bit", "")
bowshot = Attack(False, "Bowshot", "You shoot an arrow out of your bow", -1, 0, "Pierce", -1, 25, 0, 10, "shot", "Bowshot")