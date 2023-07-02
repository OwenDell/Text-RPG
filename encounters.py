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

class Enemy: #The player encounters a random enemy from the pool of potential enemies within their current area. Each enemy has an associated weight for how likely it is the player encounters them.
    def __init__(self):
        self.name = "FindEnemy"

    def __call__(self, area):
        enemy = f.weighted_random(area.local_enemies)
        print(enemy.intro, 3)
        b.fight(enemy)

class GoldPouch: #The player finds a pouch of gold, where the amount of gold within is a random value based on the level of the current area.
    def __init__(self):
        self.name = "GoldPouch"

    def __call__(self, area):
        gold = 5*area.level + random.randint(4*area.level, (8*area.level))
        print(f"You found a pouch of gold on the side of the trail containing {gold} coins!")
        player.gold += gold

class FindItem: #The player finds a random consumable item within the area. The items available to be found is based on the items tier, where the player can find items up to 2 tiers lower than their current areas level and up to 1 tier higher. Each item has an associated rarity for how likely it is to find that item.
    def __init__(self):
        self.name = "FindItem"

    def __call__(self, area):
        potential_items = []
        for item in p.items_list:
            if p.items_list[item].tier <= area.level+1 and p.items_list[item].tier >= area.level-2 and p.items_list[item].slot == "Consumables":
                potential_items.append([item, f.limit(p.items_list[item].lootweight-abs(p.items_list[item].tier-area.level), 10)])
        chosen_item = f.weighted_random(potential_items)
        print(f"While exploring, you happened across a {chosen_item}!", 0.7)
        p.loot(p.items_list[chosen_item], 1)

#########################################
#          HIGHWAY ENCOUNTERS           #
#########################################

highway_encounters_uneventful = [] #List of uneventful highway encounters, which are just simple ones where a line is printed and a simple consequence potentially plays out such as losing/gaining a small amount of HP, gold, or Energy
highway_encounters_event = [[FindItem(), 35], [GoldPouch(), 65]] #List of eventful highway encounters, which are ones you'd expect to find while exploring

class Uneventful:
    def __init__(self, text, energy=0, gold=0, health=0):
        self.text = text
        self.energy = energy
        self.gold = gold
        self.health = health
        highway_encounters_uneventful.append(self)

    def __call__(self, area):
        gold = self.gold*area.level + random.randint((self.gold-2)*area.level, (self.gold+2)*area.level) if self.gold != 0 else 0
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
HWE_U6 = Uneventful("While making your way through rocky terrain, you trip and sprain your ankle.", -5, 0, -5)
HWE_U7 = Uneventful("You arrive at an overturned cart on the side of the road... upon inspection you find a small coin purse.", 0, 3)
HWE_U8 = Uneventful("You arrive at an overturned cart on the side of the road... upon inspection you find a lockbox full of gold coins!", 0, 6)
HWE_U9 = Uneventful("You arrive at an overturned cart on the side of the road... upon inspection you can't gleam anything of value...")
HWE_U10 = Uneventful("You reach the end of your trail and have to continue off road for a while.", -10)
HWE_U11 = Uneventful("You walk along a forest trail while taking in the sound of chittering animals nearby.")
HWE_U12 = Uneventful("You walk along a gurgling creek while listening to small fish splash in the water.")
HWE_U13 = Uneventful("You hear a rustle of leaves from a nearby bush... but upon closer inspection it's just a bird that flies away.")
HWE_U14 = Uneventful("The bridge you were planning on using to cross a river turned out to be destroyed, you'll have to find another way around...", -5)
HWE_U15 = Uneventful("You meet a friendly farmer who agrees to let you ride on the back of his cart for a while until you split paths.", 10)
HWE_U16 = Uneventful("You try to climb up a boulder to get a good view of your surroundings, but you fall and bruise your knee.", -5, 0, -10)
HWE_U17 = Uneventful("You try to climb up a boulder to get a good view of your surroundings, and from your vantage point you spot a shortcut in the thicket.", 5)
HWE_U18 = Uneventful("On your travels you meet an old, friendly herbalist who gives you some yarrow to chew on.", 0, 0, 5)
HWE_U19 = Uneventful("Your journey takes you through a small clearing in the woods, with light shining through the treeline onto you.")
HWE_U20 = Uneventful("Your journey takes you to a small pond, where you briefly stop to catch your breath before carrying on.")