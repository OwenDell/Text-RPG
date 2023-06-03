#########################################
#               IMPORTS                 #
#########################################

import functions as f

#########################################
#           GLOBAL VARIABLES            #
#########################################

items_list = {}
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

#########################################
#               CLASSES                 #
#########################################

class item:
    def __init__(self, slot, name, description, action, tier, quantity, value, effect, val1, val2, val3):
        self.slot = slot
        self.name = name
        self.description = description
        self.action = action
        self.tier = tier
        self.quantity = quantity
        self.value = value
        self.effect = effect
        self.val1 = val1
        self.val2 = val2
        self.val3 = val3
        items_list[self.name] = self

    def __str__(self):
        print(f"{self.name}: {self.description}. ({self.quantity} owned)")

class weapon:
    def __init__(self, slot, name, description, tier, quantity, value):
        pass

#########################################
#          BACK-END FUNCTIONS           #
#########################################

def inventory_check():
    print("Item Inventory:")
    for item in items_list:
        if items_list[item].quantity > 0:
            print(f"{items_list[item].quantity}x {items_list[item].name}: {items_list[item].description}.")

def loot(item, quantity):
    if isinstance(item, str):
        item = items_list[f.capitalize(item)]
        quantity = int(quantity)
    item.quantity += quantity
    operator = "-" if quantity < 0 else "+"
    print(f"{operator}{quantity} {item.name}")

#########################################
#              EQUIPMENT                #
#########################################



#########################################
#              INVENTORY                #
#########################################

small_health_potion = item("consumable", "Small Health Potion", f"A small red flask that heals you for 20 HP when drank", health_potion_action, 1, 5, 10, "Health", 20, 0, 0)
health_potion = item("consumable", "Health Potion", f"A red bottle that heals you for 50 HP when drank", health_potion_action, 3, 0, 40, "Health", 50, 0, 0)
large_health_potion = item("consumable", "Large Health Potion", f"A large red draught that heals you for 100 HP when drank", health_potion_action, 7, 0, 125, "Health", 100, 0, 0)
small_mana_potion = item("consumable", "Small Mana Potion", f"A small blue flask that restores 10 MP when drank", mana_potion_action, 1, 3, 7, "Mana", 10, 0, 0)
mana_potion = item("consumable", "Mana Potion", f"A blue bottle that restores 30 MP when drank", mana_potion_action, 3, 0, 30, "Mana", 35, 0, 0)
large_mana_potion = item("consumable", "Large Mana Potion", f"A large blue draught that restores 75 MP when drank", mana_potion_action, 6, 0, 100, "Mana", 75, 0, 0)
bread_chunk = item("consumable", "Chunk of Bread", "A stale yet hearty chunk of bread. Restores 25 Energy when consumed", food_action, 1, 3, 8, "Energy", 25, 0, 0)
bread_loaf = item("consumable", "Loaf of Bread", "A nutritious loaf of bread. Restores 60 Energy when consumed", food_action, 2, 1, 15, "Energy", 60, 0, 0)
hearty_stew = item("consumable", "Bowl of Hearty Stew", "A warm bowl of stew that restores 75 Energy and grants the 'Well Fed' buff for the next 5 encounters", food_action, 3, 0, 40, "Energy", 75, ["Well Fed", 5], 0)
