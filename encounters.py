#########################################
#               IMPORTS                 #
#########################################

import math
import random
import functions as f
import playerstats as p
import creatures as c

#########################################
#           GLOBAL VARIABLES            #
#########################################

#########################################
#              ENCOUNTERS               #
#########################################

class Enemy:
    def __init__(self):
        self.name = "FindEnemy"

    def __str__(self):
        return f"You encountered an enemy."
    
    def __call__(self, area):
        enemy = f.weighted_random(area.local_enemies)
        print(enemy.intro)
        c.fight(enemy)

class GoldPouch:
    def __init__(self):
        self.name = "GoldPouch"

    def __str__(self):
        return f"You found a pouch of gold."
    
    def __call__(self, area):
        gold = 5*area.level + random.randint(4*area.level, (8*area.level))
        print(f"You found a pouch of gold on the side of the trail containing {gold} coins!")
        c.player.gold += gold

class FindItem:
    def __init__(self):
        self.name = "FindItem"

    def __str__(self):
        return f"Finds a random item"
    
    def __call__(self, area):
        potential_items = []
        for item in p.items_list:
            if p.items_list[item].tier <= area.level and p.items_list[item].tier >= area.level-2:
                potential_items.append(item)
        chosen_item = random.choice(potential_items)
        p.loot(p.items_list[chosen_item], 1)
        print(f"While exploring, you happened across a {chosen_item}!")


#########################################
#            INITIALIZATION             #
#########################################
