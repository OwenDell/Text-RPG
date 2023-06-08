#########################################
#               IMPORTS                 #
#########################################

import functions as f

#########################################
#           GLOBAL VARIABLES            #
#########################################

print = f.print_override
sleep = f.sleep
items_list = {}
equipment_list = {}
health_potion_action = ["You drank a", "healing", "HP"]
mana_potion_action = ["You drank a", "restoring", "Mana"]
food_action = ["You ate a", "restoring", "Energy"]
damage_action = ["You used a", "dealing", "damage"]

#########################################
#                STATS                  #
#########################################

current_area = "Chalgos"
position = 0
mana = 20 
maxMana = 20
energy = 100
maxEnergy = 100
reqXP = 250
strength = 1
dexterity = 1
intelligence = 1
effective_strength = 1
effective_dexterity = 1
effective_intelligence = 1
speed = 100

#########################################
#               CLASSES                 #
#########################################

class item:
    def __init__(self, slot, name, description, action, tier, quantity, value, affect, val1, val2, val3, effects, accuracy):
        self.slot = slot
        self.name = name
        self.description = description
        self.action = action
        self.tier = tier
        self.quantity = quantity
        self.value = value
        self.affect = affect
        self.val1 = val1
        self.val2 = val2
        self.val3 = val3
        self.effects = effects
        self.accuracy = accuracy
        items_list[self.name] = self

    def __str__(self):
        print(f"{self.name}: {self.description}. ({self.quantity} owned)")

class weapon: #for equipment, store every piece of equipment in equipment_list. The player can collect duplicates of gear that is stored in quantity, make function allowing player to swap out equipment of same {slot}, which decrements the quantity value of newly equipped item by 1 and increments quantity of swapped out equipment by 1. Therefore equipped items do not show up in equipment_list to make it easier to restrict player from selling equipped gear or something like that.
    def __init__(self, slot, name, description, tier, quantity, value):
        pass

#########################################
#          BACK-END FUNCTIONS           #
#########################################

def inventory_check(sleeptime=0):
    f.header("Inventory", 0.5)
    for item in items_list:
        if items_list[item].quantity > 0:
            print(f"{items_list[item].quantity}x {items_list[item].name}: {items_list[item].description}.", sleeptime)
    f.header("", 0.7)

def loot(item, quantity):
    if isinstance(item, str):
        item = items_list[f.capitalize(item)]
        quantity = int(quantity)
    item.quantity += quantity
    operator = "-" if quantity < 0 else "+"
    print(f"{operator}{quantity} {item.name}", 0.15)

#########################################
#              EQUIPMENT                #
#########################################



#########################################
#              INVENTORY                #
#########################################

small_health_potion = item("consumable", "Small Health Potion", f"A small red flask that heals you for 20 HP when drank", health_potion_action, 1, 5, 10, "Health", 20, 0, 0, [], -1)
health_potion = item("consumable", "Health Potion", f"A red bottle that heals you for 50 HP when drank", health_potion_action, 3, 0, 40, "Health", 50, 0, 0, [], -1)
large_health_potion = item("consumable", "Large Health Potion", f"A large red draught that heals you for 100 HP when drank", health_potion_action, 7, 0, 125, "Health", 100, 0, 0, [], -1)
small_mana_potion = item("consumable", "Small Mana Potion", f"A small blue flask that restores 10 MP when drank", mana_potion_action, 1, 3, 7, "Mana", 10, 0, 0, [], -1)
mana_potion = item("consumable", "Mana Potion", f"A blue bottle that restores 30 MP when drank", mana_potion_action, 3, 0, 30, "Mana", 35, 0, 0, [], -1)
large_mana_potion = item("consumable", "Large Mana Potion", f"A large blue draught that restores 75 MP when drank", mana_potion_action, 6, 0, 100, "Mana", 75, 0, 0, [], -1)
bread_chunk = item("consumable", "Chunk Of Bread", "A stale yet hearty chunk of bread. Restores 25 Energy when consumed", food_action, 1, 3, 8, "Energy", 25, 0, 0, [], -1)
bread_loaf = item("consumable", "Loaf Of Bread", "A nutritious loaf of bread. Restores 60 Energy when consumed", food_action, 2, 1, 15, "Energy", 60, 0, 0, [], -1)
hearty_stew = item("consumable", "Hearty Stew", "A warm bowl of stew that restores 75 Energy and grants the 'Well Fed' buff for the next 5 encounters", food_action, 3, 0, 40, "Energy", 75, 0, 0, [["Well Fed", 5, "user"]], -1)
poisoned_throwing_knife = item("consumable", "Poison Throwing Knife", "A throwing knife that deals 25 Damage and inflicts a minor poison", damage_action, 4, 0, 20, "Damage", 25, 0, 0, [["Lesser Poison", 3, "target"]], 80)
lesser_antidote = item("consumable", "Lesser Antidote", "Cures you of minor poisons and ailments", "Potion", 3, 0, 25, "Potion", 0, 0, 0, [["Lesser Antidote", 0, "user"]], -1)
antidote = item("consumable", "Antidote", "Makes you immune to common poisons and ailments for 5 turns", "Potion", 6, 0, 70, "Potion", 0, 0, 0, [["Lesser Antidote", 5, "user"], ["Antidote", 5, "user"]], -1)
poison_vial = item("consumable", "Poison Vial", "Afflicts the drinker with a minor poison for 5 turns", "Potion", -5, 0, 30, "Potion", 0, 0, 0, [["Lesser Poison", 5, "user"]], -1)
eternal_poison_vial = item("consumable", "Eternal Poison Vial", "Afflicts the drinker with a permanent minor poison", "Potion", -5, 0, 100, "Potion", 0, 0, 0, [["Lesser Poison", -1, "user"]], -1)
holy_water = item("consumable", "Holy Water", "Cures you of nearly every ailment and restores 100 HP", "Potion", 10, 0, 300, "Health", 100, 0, 0, [["Cleanse", 0, "user"]], -1)
