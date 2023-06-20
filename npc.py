#########################################
#               IMPORTS                 #
#########################################

import random
import time
from inspect import signature
import functions as f
import playerstats as p
import creatures as c
import encounters as e
import battle as b
import statuses as s

#########################################
#           GLOBAL VARIABLES            #
#########################################

print = f.print_override
sleep = f.sleep
player = c.player
items_list = p.items_list
consumables_list = p.consumables_list
equipment_list = p.equipment_list
weapons_list = p.weapons_list
armor_list = p.armor_list
keyitems_list = p.keyitems_list
materials_list = p.materials_list
spell_list = p.spell_list
specials_list = c.specials_list
npc_list = {}
shopkeeper_list = {}

#########################################
#               CLASSES                 #
#########################################

class Shopkeeper:
    def __init__(self, name, description, relation, quests, locations, highway_locations, interactions, intros, dialogue, shop_categories, shop_tiers, shop_whitelist, shop_blacklist):
        self.name = name #The NPC's name
        self.description = description #The NPC's description.
        self.relation = relation #Tracks the players relation with this NPC. Can go from -100 to 100, and will affect things like shop prices, available quests, what intro is played when meeting them, and what items are available for sale with them.
        self.quests = quests #List of all available non-storyline quests this NPC has for the player, storyline related quests will be given through the dialogue section.
        self.locations = locations #Locations where this NPC will be accessible. If in a village this means they can be directly spoken to here, and if in Fields they must be randomly encountered there to talk to them.
        self.highway_locations = highway_locations #Same as locations, but just while travelling on highways. Should probably only be used for wandering merchants and the like.
        self.interactions = interactions #A list of special interactions the player can do with this NPC.
        self.intros = intros #Dictionary of intro lines that this NPC will say start with when you first start talking to them. The key of the dictionary is the minimum relation for the NPC to play that intro, so the NPC will speak to the player differently based on how friendly they are with them. Every NPC must also have a dictionary entry of "Meet" that plays if it's the player first time ever talking to this NPC
        self.dialogue = dialogue #List of lists of dialogue this NPC has for the player, uses the dialogue_track variable to determine which dialogue group to play.
        self.dialogue_track = -1 #This tracks what line of section of dialogue the player should be on so it knows which one to play when the player talks to this NPC again. It will start as -1 before the player has met this NPC, which will be used to determine if the first time introduction line should be played or a standard intro line
        self.type = "Shopkeeper"
        npc_list[self.name] = self
        shopkeeper_list[self.name] = self
        self.shop_inventory = {
            "Consumables": {},
            "Weapons": {},
            "Armor": {},
            "Key Items": {},
            "Materials": {}
        }
        for item in items_list:
            if ((items_list[item].slot in shop_categories and items_list[item].tier in shop_tiers) and items_list[item].name not in shop_blacklist) or items_list[item].name in shop_whitelist:
                if item in consumables_list:
                    self.shop_inventory["Consumables"][item] = items_list[item]
                if item in weapons_list:
                    self.shop_inventory["Weapons"][item] = items_list[item]
                if item in armor_list:
                    self.shop_inventory["Armor"][item] = items_list[item]
                if item in keyitems_list:
                    self.shop_inventory["Key Items"][item] = items_list[item]
                if item in materials_list:
                    self.shop_inventory["Materials"][item] = items_list[item]

    def __str__(self):
        return f"{self.name}: {self.description} [Reputation: {self.relation}]"
    
    def buy(self):
        while True:
            f.header(f"{self.name}'s Shop", 0.5)
            for category in self.shop_inventory:
                if len(self.shop_inventory[category]) >= 1:
                    print(category, 0.2)
            f.header("", 0.5)
            response = f.capitalize(input("Enter a shop category, or 'Exit' to leave the shop: "))
            sleep(0.5)
            if response == "Exit":
                break
            elif response in self.shop_inventory and len(self.shop_inventory[response]) >= 1:
                while True:
                    f.header(response, 0.5)
                    for item in self.shop_inventory[response]:
                        print(f"{items_list[item].name}: {items_list[item].description}. [{f.limit(round(items_list[item].value+(items_list[item].value*(0.2-(self.relation*0.002)))), round(items_list[item].value*1.5), items_list[item].value)} Gold]", 0.2)
                    f.header("", 0.5)
                    response2 = f.capitalize(input("Enter the name of the item you'd like to purchase, or 'Exit' to return to the main shop menu: "))
                    sleep(0.5)
                    if response2 == "Exit":
                        break
                    elif response2 in self.shop_inventory[response]:
                        try:
                            amount = 1 if response != "Consumables" and response != "Materials" else int(input(f"How many {response2}'s would you like to purchase? "))
                            sleep(0.5)
                            cost = f.limit(round(items_list[response2].value+(items_list[response2].value*(0.2-(self.relation*0.002)))), round(items_list[response2].value*1.5), items_list[response2].value)*amount
                            if player.gold >= cost:
                                player.gold -= cost
                                items_list[response2].quantity += amount
                                print(f"You bought {amount} {response2}(s) for {cost} gold.", 1)
                            else:
                                print(f"You don't have enough gold to buy {amount} {response2}(s), you're missing {cost-player.gold} gold!", 1.5)
                        except:
                            print("Invalid response, your response must be a whole number.", 1)
                    else:
                        print("Invalid response, your response must be the name of a listed shop item, or 'Exit' to return to the main shop menu.", 1)
            else:
                print("Invalid response, your response must be the name of a listed shop category, or 'Exit' to leave the shop.", 1)

    def sell(self):
        while True:
            p.inventory_check(0.15)
            response = f.capitalize(input("Enter either the name of the item you want to sell, or 'Exit' to leave the shop: "))
            sleep(0.5)
            if response == "Exit":
                break
            elif response in items_list:
                cost = f.limit(round(items_list[response].value-(items_list[response].value*(0.2-(self.relation*0.002)))), items_list[response].value, round(items_list[response].value*0.5))
                print(f"You can sell up to {items_list[response].quantity} {response}(s) for {cost} gold each.", 0.8)
                try:
                    response2 = int(input(f"How many {response}'s do you want to sell? "))
                    sleep(0.5)
                    if response2 <= items_list[response].quantity:
                        items_list[response].quantity -= response2
                        player.gold += cost*response2
                        print(f"You sold {response2} {response}(s) for {cost*response2} gold.", 1)
                    else:
                        print(f"You don't own that many {response}'s, you only have {items_list[response].quantity}!", 1)
                except:
                    print("Invalid response, your response must be a whole number.", 1)
            else:
                print("Invalid response, your response must be the name of an owned item, or 'Exit' to leave the shop.", 1)
    
#########################################
#          BACK-END FUNCTIONS           #
#########################################

def converse(npc):
    npc = npc_list[npc]
    if npc.dialogue_track == -1:
        print(f"{npc.name}: {npc.intros['Meet']}", 3)
        npc.dialogue_track = 0
    else:
        chosen_relation = -100
        for intro in npc.intros:
            if intro != "Meet":
                if intro > chosen_relation and intro <= npc.relation:
                    chosen_relation = intro
        print(f"{npc.name}: {npc.intros[chosen_relation]}", 3)
    while True:
        f.header(npc.name, 0.5)
        for interaction in npc.interactions:
            print(interaction, 0.2)
        f.header("", 0.5)
        response = f.capitalize(input(f"What do you want to do with {npc.name}? "))
        sleep(0.5)
        if response == "Exit":
            break
        elif response in npc.interactions:
            if response == "Buy":
                npc.buy()
            elif response == "Sell":
                npc.sell()
            elif response == "Quests":
                f.header("Available Quests", 0.5)
                for quest in npc.quests:
                    print(quest, 0.3)
                f.header("", 1)
            elif response == "Talk":
                print("")
                for line in npc.dialogue[npc.dialogue_track]:
                    print(f"{npc.name}: {line}", 4)
                print("")
                npc.dialogue_track = f.limit(npc.dialogue_track+1, len(npc.dialogue)-1)
        else:
            print("Invalid response, your response must be one of the listed options, or enter 'Exit' to leave.", 1)

#########################################
#              SHOPKEEPERS              #
#########################################

Andre = Shopkeeper("Andre", "An old, grizzled blacksmith who's forged weapons and armor for many a naive adventurer.", 0, [], ["Chalgos"], [], ["Talk", "Quests", "Buy", "Sell", "Exit"], \
                   {"Meet": "Hmph... what are you, nother novice adventurer set on rushing to their deaths? Well if that's what you want, I may as well try to help you last as long as possible...", -100: "Bold of you to show your face around here... do your business quick and go.", -40: "Hm... What do you want...", -5: "Ah, you're back... honestly I'm somewhat surprised.", 20: f"Welcome back {p.player_name}, what can I do for ya?", 60: f"Well, if it isn't {p.player_name}! How can I be of service?"}, \
                   [["Bah, don't bother trying to convince me otherwise, I've seen plenty of your kind before... and they always end up the same way...", "But, I can't say I don't understand the desire to venture out into the great unknown and try to make a name for yourself.", "I considered it once... but fate had other plans in mind for me."], ["I'll try my best to equip you well enough that you at least have a chance out there.", "... Hopefully my wares will serve you better than it did the rest..."], ["I suppose I may as well try and impart some words of wisdom on you if you insist on this.", "If you want any hope of making it out there then you'd better listen close.", "First off, you'd best pay attention to the damage types of your weapons. Every weapon does different amounts of the various damage types, and enemies will be more resistant or weak to different ones.", "For example, slashing attacks won't do much against heavily armored foes, but there's little their armor can do against a solid blunt attack."]], \
                   ["Mainhand", "Offhand", "Both", "Special", "Helmet", "Armor", "Leggings", "Gloves", "Boots"], [0, 1, 2], [], [])

Malbras = Shopkeeper("Malbras", "The kind owner of the only tavern in Chalgos. He'll sell basic supplies and food necessary for adventuring.", 10, [], ["Chalgos"], [], ["Talk", "Quests", "Buy", "Sell", "Exit"], \
                    {"Meet": f"Hey there, you must be {p.player_name}, my name's Malbras, make yourself comfortable!", -100: "The only reason you can even show your face in here is because I can't afford a guard...", -60: "You're lucky I'm so lenient towards paying customers...", -10: "What'll it be today?", 30: f"Hey there {p.player_name}, what're ya lookin for today?", 60: f"Welcome in {p.player_name}! Make yourself right at home!"}, \
                    [["I'm the proud owner of this here fine tavern, we offer a variety of nutritious meals and even a few potions to get you back on your feet if need be.", "If there's anything you need just say the word and I'll have it right up for you! ... If you've got the money that is."]], \
                    ["Consumables"], [1, 2], ["Hearty Stew", "Lesser Antidote", "Uppercut Scroll"], ["Throwing Knife"])