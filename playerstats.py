#########################################
#               IMPORTS                 #
#########################################



#########################################
#           GLOBAL VARIABLES            #
#########################################

items_list = {}

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
    def __init__(self, name, description, tier, quantity, value, val1, val2, val3):
        self.name = name
        self.description = description
        self.tier = tier
        self.quantity = quantity
        self.value = value
        self.val1 = val1
        self.val2 = val2
        self.val3 = val3
        items_list[self.name] = self

    def __str__(self):
        print(f"{self.name}: {self.description}. ({self.quantity} owned)")

#########################################
#              EQUIPMENT                #
#########################################



#########################################
#              INVENTORY                #
#########################################

small_health_potion = item("Small Health Potion", f"A small red flask that heals you for 20 HP when drank", 1, 5, 10, 20, 0, 0)
health_potion = item("Health Potion", f"A red bottle that heals you for 50 HP when drank", 3, 0, 40, 50, 0, 0)
large_health_potion = item("Large Health Potion", f"A large red draught that heals you for 100 HP when drank", 7, 0, 125, 100, 0, 0)
small_mana_potion = item("Small Mana Potion", f"A small blue flask that restores 10 MP when drank", 1, 3, 7, 10, 0, 0)
mana_potion = item("Mana Potion", f"A blue bottle that restores 30 MP when drank", 3, 0, 30, 35, 0, 0)
large_mana_potion = item("Large Mana Potion", f"A large blue draught that restores 75 MP when drank", 6, 0, 100, 75, 0, 0)
bread_chunk = item("Chunk of Bread", "A stale yet hearty chunk of bread. Restores 25 Energy when consumed", 1, 3, 8, 25, 0, 0)
bread_loaf = item("Loaf of Bread", "A nutritious loaf of bread. Restores 60 Energy when consumed", 2, 1, 15, 60, 0, 0)
hearty_stew = item("Bowl of Hearty Stew", "A warm bowl of stew that restores 75 Energy and grants the 'Well Fed' buff for the next 5 encounters", 3, 0, 40, 75, ["Well Fed", 5], 0)