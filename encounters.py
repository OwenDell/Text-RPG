#########################################
#               IMPORTS                 #
#########################################

import math
import random
import functions as f
import playerstats as p
import creatures as c
import battle as b
import statuses as s

#########################################
#           GLOBAL VARIABLES            #
#########################################

print = f.print_override
sleep = f.sleep
player = c.player

#########################################
#              ENCOUNTERS               #
#########################################

class Enemy:
    def __init__(self):
        self.name = "FindEnemy"

    def __call__(self, area):
        enemy = f.weighted_random(area.local_enemies)
        print(enemy.intro, 3)
        b.fight(enemy)

class GoldPouch:
    def __init__(self):
        self.name = "GoldPouch"

    def __call__(self, area):
        gold = 5*area.level + random.randint(4*area.level, (8*area.level))
        print(f"You found a pouch of gold on the side of the trail containing {gold} coins!")
        player.gold += gold

class FindItem:
    def __init__(self):
        self.name = "FindItem"

    def __call__(self, area):
        potential_items = []
        for item in p.items_list:
            if p.items_list[item].tier <= area.level and p.items_list[item].tier >= area.level-2:
                potential_items.append(item)
        chosen_item = random.choice(potential_items)
        print(f"While exploring, you happened across a {chosen_item}!", 0.7)
        p.loot(p.items_list[chosen_item], 1)

#########################################
#          HIGHWAY ENCOUNTERS           #
#########################################

highway_encounters_uneventful = []
highway_encounters_event = [[FindItem(), 35], [GoldPouch(), 65]]

class Uneventful:
    def __init__(self, text, energy=0, gold=0, health=0):
        self.text = text
        self.energy = energy
        self.gold = gold
        self.health = health
        highway_encounters_uneventful.append(self)

    def __call__(self, area):
        gold = self.gold*area.level + random.randint((self.gold-2)*area.level, (self.gold+2)*area.level)
        p.energy += self.energy
        player.gold += gold
        player.health += self.health
        print(self.text, 0.7)
        operator = "+" if self.energy > 0 else ""
        if self.energy != 0:
            print(f"{operator}{self.energy} Energy", 0.3)
        operator = "+" if self.gold > 0 else ""
        if self.gold != 0:
            print(f"{operator}{gold} Gold", 0.3)
        operator = "+" if self.health > 0 else ""
        if self.health != 0:
            print(f"{operator}{self.health} Health", 0.3)

#########################################
#     HIGHWAY UNEVENTFUL ENCOUNTERS     #
#########################################

HWE_U1 = Uneventful("You walk along a dirt trail and appreciate the nice weather.")
HWE_U2 = Uneventful("You arrive at a shallow river and must ford across it.", -5)
HWE_U3 = Uneventful("Along your travels you take note of an interesting looking boulder in the distance.")
HWE_U4 = Uneventful("You get to a cobblestone road and appreciate the easier travel.", 5)
HWE_U5 = Uneventful("You briefly stop to rest under a fruiting apple tree and enjoy a delicious apple.", 10)
HWE_U6 = Uneventful("While making your way through rocky terrain, you trip and sprain your ankle.", -10, 0, -5)
HWE_U7 = Uneventful("You arrive at an overturned cart on the side of the road... upon inspection you find a small coin purse.", 0, 3)
HWE_U8 = Uneventful("You arrive at an overturned cart on the side of the road... upon inspection you find a lockbox full of gold coins!", 0, 6)
HWE_U9 = Uneventful("You arrive at an overturned cart on the side of the road... upon inspection you can't gleam anything of value...")
HWE_U10 = Uneventful("You reach the end of your trail and have to continue off road for a while.", -10)
