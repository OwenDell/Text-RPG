#########################################
#               IMPORTS                 #
#########################################

import functions as f

#########################################
#           GLOBAL VARIABLES            #
#########################################

print = f.print_override
sleep = f.sleep
items_list = {} #Dictionary of all items in the game, this includes consumables, equipment, materials, and key items. All items will be divided into smaller categories below.
consumables_list = {} #Category for consumable items
equipment_list = {} #Category for equipment type items
weapons_list = {} #Sub-category for weapon type equipment
armor_list = {} #Sub-category for armor type equipment
keyitems_list = {} #Category for key item type items
materials_list = {} #Category for key item type items
health_potion_action = ["You drank a", "healing", " HP"] #These 'actions' are used for easy modularity with consumable items, as they are pieced together along with other pieces of information when printing in the Use function.
mana_potion_action = ["You drank a", "restoring", " Mana"]
food_action = ["You ate a", "restoring", " Energy"]
damage_action = ["You used a", "dealing", " damage"]
spell_action = ["You read a", "and learned the move", ""]
encyclopedia = {
    "Enemies": {},
    "Weapons": {},
    "Armor": {},
    "Items": {},
    "Moves": {},
    "Characters": {},
    "Areas": {},
    "Stats": {},
    "Mechanics": {},
    "Tutorials": {}
}

#########################################
#                STATS                  #
#########################################

player_name = "Henry" #The players name, some NPC's will refer to the player by their name, and it shows up in a few other places. Mainly just intended to make the player feel more invested in the world. Defaults to "Henry" if the player chooses to skip the intro.
current_area = "Chalgos" #Tracks the players current area
position = 0 #Tracks the players current position, which affects their current area
mana = 20 #How much mana the player currently has
maxMana = 20 #The players maximum mana
energy = 100 #How much energy the player currently has
maxEnergy = 100 #The players maximum energy
reqXP = 150 #The required amount of XP to level up, this will increase with each level
#The players real stats, this is only increased through level ups:
vitality = 0 #Dictates health, every point of vitality is +20 maxHP
strength = 0 #Dictates physical damage and affects skill checks
dexterity = 0
intelligence = 0
faith = 0
#The players effective stats, which can change from things like statuses or equipment bonuses, and is what's used for all calculations, but is stored separately from the real stats so it knows what to revert to when those bonuses end:
effective_vitality = 0
effective_strength = 0
effective_dexterity = 0
effective_intelligence = 0
effective_faith = 0
speed = 100 #The players speed, which is the number of meters of distance they move during each loop of travelling. This can be changed through various statuses or equipment bonuses.
equipment = { #The players equipment slots, which will be updated throughout the game as the player acquires and swaps out new pieces of equipment.
    "Mainhand": "Empty",
    "Offhand": "Empty",
    "Special": "Empty",
    "Helmet": "None",
    "Armor": "None",
    "Leggings": "None",
    "Boots": "None",
    "Gloves": "None",
    "Ring": "None",
    "Amulet": "None"
}

#########################################
#               CLASSES                 #
#########################################

class item: #for regular items, usually consumables.
    def __init__(self, slot, name, description, action, tier, quantity, value, affect, val1, val2, val3, effects, accuracy, lootweight):
        self.slot = slot #called slot for consistency, but in actuality this determines the type of item.
        self.name = name #the name of the item.
        self.description = description #the description of the item.
        self.action = action #used to determine which of the 'action' text lists is used by the Use function when this item is used.
        self.tier = tier #the tier of the item, used for determining loot pools.
        self.quantity = quantity #how much of this item the player owns, should start as 0 for anything that isn't starting goods.
        self.value = value #the value in gold of this item. Traders will use this price for determining how much to charge/offer for these items while shopping, also provides a clean reference for roughly how much this item is worth.
        self.affect = affect #a string of what this item affects, used by the Use function with simple items that have straightforward properties for modularity.
        self.val1 = val1 #The primary value of this item, nondescript for modularity sake, but this usually applies to whatever is directly being impacted in the 'affect' section.
        self.val2 = val2 #The secondary value of this item, nondescript for modularity sake.
        self.val3 = val3 #The tertiary value of this item, nondescript for modularity sake.
        self.effects = effects #Not to be confused with 'affect', this is a list of all status effects that are applied to the target upon use.
        self.accuracy = accuracy #The accuracy of this item, will usually be -1 (unmissable) for anything that isn't used to harm the enemy.
        self.lootweight = lootweight #The weighted odds on a 1-10 scale of finding this item, higher number means higher odds of finding it compared to other potential items in the same lootpool
        items_list[self.name] = self
        if slot == "Consumables":
            consumables_list[self.name] = self

    def __str__(self):
        return f"{self.name}: {self.description}. ({self.quantity} owned)"

class weapon: #for equipment, store every piece of equipment in equipment_list. The player can collect duplicates of gear that is stored in quantity, make function allowing player to swap out equipment of same {slot}, which decrements the quantity value of newly equipped item by 1 and increments quantity of swapped out equipment by 1. Therefore equipped items do not show up in equipment_list to make it easier to restrict player from selling equipped gear or something like that.
    def __init__(self, slot, name, description, tier, quantity, value, damages, accuracy, critchance, critmultiplier, moves, lootweight):
        self.slot = slot #The slot for the equipment, in the case of weapons, either "mainhand", "offhand", "both", or "special". Most weapons will be equipped in either the mainhand or offhand, ones with both are either 2-hand weapons or dual wield weapons that take up both slots, and special is for special weapons that don't take up a weapon slot, maybe something like a floating magic orb idk
        self.name = name #The name of the piece of equipment
        self.description = description #The description, should be fairly brief and not go into statiscal detail, as that can be viewed with the equipment 'inspect' feature that gives the detailed stats
        self.tier = tier #The tier of the equipment, used to determine where it belongs in loot pools and to give a quick and easy reference for its quality
        self.quantity = quantity #How many the player owns, should be 0 for everything that the player doesn't start with. The player will be able to collect duplicates of equipment they already own so they can separately sell or salvage them
        self.value = value #The baseline buy/sell value of the item. The actual buy/sell value will not be exactly this, as merchants will charge a premium for goods and will buy goods for less, but those prices will be based off this
        self.accuracy = accuracy #The ADDITIONAL accuracy this weapon applies to moves. The baseline for this is 0, as any value other than 0 is added on to the accuracy for moves, and is not a multiplier
        self.critchance = critchance #The ADDITIONAL crit chance this weapon applies to moves. The baseline for this is 0, as any value other than 0 is added on to the crit chance for moves, and is not a multiplier
        self.critmultiplier = critmultiplier #The damage multiplier applied when a critical hit is performed, the baseline should be 1.5x
        self.moves = moves #The list of moves that this weapon has. The player will have access to every move of their currently equipped weapon, and those moves will be automatically unlearnt when the player unequips the weapon
        self.lootweight = lootweight #The weighted odds on a 1-10 scale of finding this item, higher number means higher odds of finding it compared to other potential items in the same lootpool
        self.damages = { #A dictionary of the damage types this weapon does as the keys with the associated base damage value for each damage type as the value. Moves will pick one of the 3 damage physical damage types, or default to the "Physical", damage value, and then add on any of the elemental damage types. This means every weapon must either have a value for all of the first 4 damage values, and then the rest can be 0 as those will be adde don.
            "Physical": damages[0], #Standard physical damage type if none of the other 3 physical damage types apply. Other 3 are prioritized however and it should primarily be 1 of those 3 that are used.
            "Slash": damages[1], #Effective against fleshy & unarmored targets, but less effective against hard & armored ones
            "Pierce": damages[2], #Effective against lightly armored targets, less effective against heavily armored ones
            "Blunt": damages[3], #Effective against armored targets, less effective against unarmored ones
            "Magic": damages[4], #Effective against targets primarily made of or held together by magic, less effective against those with high mental fortitude
            "Fire": damages[5], #Effective against flammable and fleshy foes, inneffective against fire retardant and armored ones
            "Lightning": damages[6], #Effective against conductive and armored foes, less effective against fleshy ones
            "Holy": damages[7], #Effective against undead or dark foes, inneffective against holy foes
            "Dark": damages[8], #Effective against holy foes, inneffective against undead or dark foes
            "True": damages[9] #True damage is equally effective against almost every foe, only special forms of magical protection can provide protection against true damage
        }
        items_list[self.name] = self
        equipment_list[self.name] = self
        weapons_list[self.name] = self

    def __str__(self):
        return f"{self.name}: {self.description}. ({self.quantity} owned)"

#########################################
#          BACK-END FUNCTIONS           #
#########################################

def inventory_check(sleeptime=0, item_type="All Items"): #prints out a list of the players full inventory. Can be separated to only include certain sections of their inventory based on the types of items that should be shown for the situation, such as only showing consumables with the Use command.
    category_print = "" if item_type == "All Items" else f" ({item_type})"
    f.header(f"Inventory{category_print}", 0.5)
    for item in items_list:
        if items_list[item].quantity > 0 and ((item_type == items_list[item].slot or item_type == "All Items") or ((item_type == "Mainhand" or item_type == "Offhand") and items_list[item].slot == "Both")):
            print(f"{items_list[item].quantity}x {items_list[item].name}: {items_list[item].description}.", sleeptime)
    f.header("", 0.7)

def loot(item, quantity=1): #Used when the player loots an item and adds it to their inventory.
    if isinstance(item, str):
        item = items_list[f.capitalize(item)]
        quantity = int(quantity)
    item.quantity += quantity
    operator = "-" if quantity < 0 else "+"
    print(f"{operator}{quantity} {item.name}", 0.15)

#########################################
#              EQUIPMENT                #
#########################################

#example_weapon = weapon(self, slot, name, description, tier, quantity, value, [physical, slash, pierce, blunt, magic, fire, lightning, holy, dark, true], accuracy, critchance, critmultiplier, moves, lootweight)
empty = weapon("Special", "Empty", "You don't have anything equipped in this slot", -1, 0, 0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0, 0, 1.5, [], 0)
bronze_short_sword = weapon("Mainhand", "Bronze Short Sword", "An old short sword made of bronze... it's seen better days..", 0, 1, 25, [15, 20, 15, 10, 0, 0, 0, 0, 0, 0], 0, 0, 1.5, ["Slash", "Stab"], 0)
spiked_club = weapon("Both", "Spiked Club", "A crude wooden club with iron nails in it", 1, 0, 70, [25, 15, 20, 30, 0, 0, 0, 0, 0, 0], -5, -10, 1.5, ["Bash"], 7)
iron_dagger = weapon("Offhand", "Iron Dagger", "A simple iron dagger that's effective at targeting weak spots for critical blows", 2, 0, 125, [15, 15, 25, 5, 0, 0, 0, 0, 0, 0], 10, 10, 2, ["Slash", "Stab"], 6)
flaming_sword = weapon("Mainhand", "Flaming Sword", "An enchanted iron sword that is constantly ablaze", 4, 0, 300, [20, 30, 25, 15, 0, 25, 0, 0, 0, 0], 5, 0, 1.75, ["Slash", "Stab"], 3)

#########################################
#              INVENTORY                #
#########################################

#example_item = item(slot, name, description, action, tier, quantity, value, affect, val1, val2, val3, effects, accuracy, lootweight)
small_health_potion = item("Consumables", "Small Health Potion", f"A small red flask that heals you for 20 HP when drank", health_potion_action, 1, 5, 10, "Health", 20, 0, 0, [], -1, 8)
health_potion = item("Consumables", "Health Potion", f"A red bottle that heals you for 50 HP when drank", health_potion_action, 3, 0, 40, "Health", 50, 0, 0, [], -1, 8)
large_health_potion = item("Consumables", "Large Health Potion", f"A large red draught that heals you for 100 HP when drank", health_potion_action, 7, 0, 125, "Health", 100, 0, 0, [], -1, 7)
small_mana_potion = item("Consumables", "Small Mana Potion", f"A small blue flask that restores 20 MP when drank", mana_potion_action, 1, 3, 7, "Mana", 20, 0, 0, [], -1, 7)
mana_potion = item("Consumables", "Mana Potion", f"A blue bottle that restores 50 MP when drank", mana_potion_action, 3, 0, 30, "Mana", 50, 0, 0, [], -1, 7)
large_mana_potion = item("Consumables", "Large Mana Potion", f"A large blue draught that restores 100 MP when drank", mana_potion_action, 6, 0, 100, "Mana", 100, 0, 0, [], -1, 6)
bread_chunk = item("Consumables", "Chunk Of Bread", "A stale yet hearty chunk of bread. Restores 25 Energy when consumed", food_action, 1, 3, 8, "Energy", 25, 0, 0, [], -1, 9)
bread_loaf = item("Consumables", "Loaf Of Bread", "A nutritious loaf of bread. Restores 60 Energy when consumed", food_action, 2, 1, 15, "Energy", 60, 0, 0, [], -1, 4)
hearty_stew = item("Consumables", "Hearty Stew", "A warm bowl of stew that restores 75 Energy and grants the 'Well Fed' buff for the next 5 encounters", food_action, 3, 0, 40, "Energy", 75, 0, 0, [["Well Fed", 5, "user"]], -1, 5)
throwing_knife = item("Consumables", "Throwing Knife", "A throwing knife that deals 25 Damage", damage_action, 2, 0, 10, "Damage", 25, 0, 0, [], 85, 4)
poisoned_throwing_knife = item("Consumables", "Poison Throwing Knife", "A throwing knife that deals 20 Damage and inflicts a minor poison", damage_action, 4, 0, 25, "Damage", 20, 0, 0, [["Lesser Poison", 3, "target"]], 80, 4)
lesser_antidote = item("Consumables", "Lesser Antidote", "Cures you of minor poisons and ailments", "Potion", 2, 0, 25, "Potion", 0, 0, 0, [["Lesser Antidote", 0, "user"]], -1, 3)
antidote = item("Consumables", "Antidote", "Makes you immune to common poisons and ailments for 5 turns", "Potion", 5, 0, 70, "Potion", 0, 0, 0, [["Lesser Antidote", 5, "user"], ["Antidote", 5, "user"]], -1, 3)
poison_vial = item("Consumables", "Poison Vial", "Afflicts the drinker with a minor poison for 5 turns", "Potion", -5, 0, 30, "Potion", 0, 0, 0, [["Lesser Poison", 5, "user"]], -1, 1)
eternal_poison_vial = item("Consumables", "Eternal Poison Vial", "Afflicts the drinker with a permanent minor poison", "Potion", -5, 0, 100, "Potion", 0, 0, 0, [["Lesser Poison", -1, "user"]], -1, 1)
holy_water = item("Consumables", "Holy Water", "Cures you of nearly every ailment and restores 100 HP", "Potion", 7, 0, 300, "Health", 100, 0, 0, [["Cleanse", 0, "user"]], -1, 2)

scroll_uppercut = item("Consumables", "Uppercut Scroll", "A powerful uppercut that deals 50 damage", spell_action, 3, 0, 200, "Spell", "Uppercut", 0, 0, [], -1, 1)