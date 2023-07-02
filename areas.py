#########################################
#               IMPORTS                 #
#########################################

import math
import random
import functions as f
import playerstats as p
import creatures as c
import encounters as e
import battle as b
import statuses as s
import npc as n

#########################################
#           GLOBAL VARIABLES            #
#########################################

print = f.print_override
sleep = f.sleep
player = c.player
areas = {} #a dictionary of all areas that gets filled every time a new area is initialized.
activities_list = {} #a dictionary of all activities that can be performed by the player within areas. Available activities will vary between areas, so the player will need to travel to new ones to access new opportunities
k_start = True #the first area 'key'. Might start as False in the future if a tutorial is implemented which must be finished before enabling leaving the first area

#########################################
#          BACK-END FUNCTIONS           #
#########################################

def determine_area(): #used with the travel mechanic to determine what area the player should currently be in while traveling. Necessary for if the player travels past 1 or more areas to reach their destination at once, so the game knows what kind of area-specific highway encounters to use
    for area in areas:
        if p.position >= areas[area].distance:
            p.current_area = areas[area]

#########################################
#               CLASSES                 #
#########################################

class Area: #class for all areas
    def __init__(self, name, description, exploring, type, level, distance, access, denialmessage, activities, encounters, local_enemies, highway_enemies, wildlife):
        self.name = name #the name of the area
        self.description = description #the description of the area
        self.exploring = exploring #the text that is printed while the player uses the 'explore' command within this area. Different between areas just for flavor.
        self.type = type #The type of area. The three types are Settlement, Field, and Dungeon. Settlements are places where you usually won't be able to explore, and are sources of life and NPC's where the player can rest and restock. Fields are open areas the player can go out to to freely explore and perform various activities to gain loot, gold, and XP. Dungeons are areas with a gauntlet of rooms the player must try to get through all in one go that end with a bossfight and great rewards.
        self.level = level #The area's level is used to determine lootpools and just to give a sense of how difficult the area is.
        self.distance = distance #The area's distance in meters from the starting area of Chalgos whose distance is 0. Used to determine how long of a journey the player must undergo while travelling.
        self.access = access #The area key associated with the area which is used to determine when a player should have access to new areas. Area keys will all be stored as separate boolean variables that will change to True upon completely various tasks or meeting certain requirements.
        self.denialmessage = denialmessage #The message that's printed when a player tries to travel to an area they don't have access to. Can either clue the player in to what they need to do to gain access to the area or just provide flavor.
        self.activities = activities #List of all activities that can be performed within this area.
        self.encounters = encounters #List of possible encounters the player may find while exploring.
        self.local_enemies = local_enemies #List of local enemies the player may encounter when they trigger the find Enemy encounter
        self.highway_enemies = highway_enemies #List of highway enemies the player may encounter when they trigger the find Enemy encounter while travelling between areas. The pool of highway enemies currently in use is based on the player's current location which.
        self.wildlife = wildlife #List of possible animals to encounter when using the "Hunt" activity. These animals will usually be less of a threat than enemies encountered with the "Explore" command, and are hunted primarily for the resources they'll drop rather than for XP or Gold
        areas[self.name] = self
        if name == "Chalgos":
            f.encyclopedia["Areas"][self.name] = self

    def __str__(self):
        return f"{self.name} ({self.type}): {self.description}. [{abs(self.distance-p.position)}m away]"
    
    def find_encounter(self): #called when the player uses the explore command. Generates a random encounter from the pool of possible encounters, with associated weights for how likely each encounter is to be pulled.
        f.weighted_random(self.encounters)(self)

    def travel(self): #called when the player tries to travel between areas. Every loop the player loses 5 energy, travels their speed stat in meters closer to their target destination, and gets a random highway encounter. Most highway encounters will be uneventful.
        response = ""
        startpoint = p.position
        distance_traveled = 0
        iteration = 0
        while abs(startpoint-self.distance) > abs(distance_traveled):
            incrementor = p.speed if self.distance-startpoint >= 0 else -p.speed
            iteration += 1
            distance_traveled += incrementor
            p.energy -= 5
            p.position += incrementor
            determine_area()
            player.health, p.mana, p.energy = f.limit([player.health, p.mana, p.energy], [player.maxHP, p.maxMana, p.maxEnergy])
            b.hpcheck(player)
            while (iteration%7 == 0 and abs(p.position-self.distance) > p.speed) and abs(distance_traveled) > 0: #Every 7 loops, the player is told their current location, health, and energy so the player can determine if they should turn back, use items to replenish themselves, or push onwards.
                print(f"You've traveled {abs(distance_traveled)}/{abs(self.distance-startpoint)}m and have {player.health}/{player.maxHP} HP and {p.energy}/{p.maxEnergy} Energy, do you want to continue onwards?", 1.5)
                response = f.capitalize(input("Enter (1) 'Yes' or (2) 'No' to continue onwards, or (3) 'Use' if you'd like to use an item: "))
                sleep(0.5)
                if response == "No" or response == "2":
                    p.position = startpoint
                    determine_area()
                    print(f"The journey proved too difficult for you, so you turned back to {p.current_area.name}...", 3)
                    break
                elif response == "Y" or response == "1":
                    print(f"You push onwards towards {self.name}, with {abs(self.distance-p.position)}m left to go.", 3)
                    break
                elif response == "Use" or response == "3":
                    c.moves_list["Use"](player, player)
                    sleep(0.3)
                else:
                    print("Invalid response, please enter one of the provided options. (You can also respond with the corresponding number to quickly choose a response)", 0.8)
            if response == "N" or response == "2":
                break
            randomness = random.randint(0, 100)
            if randomness <= 70:
                random.choice(e.highway_encounters_uneventful)(p.current_area)
            elif randomness <= 90:
                f.weighted_random(e.highway_encounters_event)(p.current_area)
            else:
                enemy = f.weighted_random(p.current_area.highway_enemies)
                print(enemy.intro, 3)
                b.fight(enemy)
                print(f"After battling the {enemy.name}, you continue on your journey to {self.name}...")
            sleep(4)
        if response != "N" and response != "2":
            p.position = self.distance
            determine_area()
            print(f"You've arrived at {self.name}.", 1)
            f.encyclopedia["Areas"][self.name] = self

#########################################
#              ACTIVITIES               #
#########################################
        
class a_Explore: #pulls a random encounter from the current areas list of possible encounters. Uses 5 energy every time.
    def __init__(self):
        self.name = "Explore"
        global activities_list
        activities_list[self.name] = self

    def __str__(self):
        return f"{self.name}: Use 5 energy to explore around in your current area to find treasure, foes, and special encounters."
    
    def __call__(self, area):
        if p.energy >= 5:
            p.energy -= 5
            print(area.exploring)
            sleep(3)
            area.find_encounter()
            sleep(0.5)
        else:
            print("You don't have enough energy to do that!", 1)

class a_Shop: #lets the player visit any shopkeepers in the current area. The player is given a list of all shopkeepers in the area and is able to choose which one they want to visit.
    def __init__(self):
        self.name = "Shop"
        activities_list[self.name] = self

    def __str__(self):
        return f"{self.name}: Visit one of the shopkeepers in the area to buy or sell goods at."
    
    def __call__(self, area):
        f.header("Available Shopkeepers", 0.5)
        for shopkeeper in n.shopkeeper_list:
            if area.name in n.shopkeeper_list[shopkeeper].locations:
                print(n.shopkeeper_list[shopkeeper], 0.3)
        f.header("", 0.5)
        response = f.capitalize(input("What shopkeeper do you want to visit? "))
        sleep(0.5)
        if response in n.shopkeeper_list:
            print(f"You walk through the streets of {area.name} to get to {response}...", 2)
            n.converse(response)
        else:
            print("Invalid response, your response must be the name of a listed shopkeeper.", 1)
        print(f"You make your way back to the center of {area.name}...", 2)

class a_Rest: #Rest at the local inn. Fully restores mana and energy, as well as half the max HP. Costs gold relative to the players level.
    def __init__(self):
        self.name = "Rest"
        global activities_list
        activities_list[self.name] = self

    def __str__(self):
        return f"{self.name}: Pay {35+player.level*15} gold to rest at the local inn, fully restoring your Energy and Mana, as well as half your total HP."
    
    def __call__(self, area):
        print(f"Welcome to the inn of {area.name}, you can spend the night resting here, but it'll cost you {35+player.level*15} gold.", 2.5)
        if f.capitalize(input("Do you want to pay the gold to rest at the inn, (Y/N)? ")) == "Y":
            sleep(0.5)
            if player.gold >= 35+player.level*15:
                print(f"After paying the inn keeper {35+player.level*15} gold, you head up the room and soon fall asleep...", 5)
                p.mana = p.maxMana
                p.energy = p.maxEnergy
                player.health += player.maxHP/2
                player.gold -= 35+player.level*15
                print(f"You wake up feeling very refreshed, and head back out into town ready to start the day.", 2.5)
            else:
                print("You don't have enough gold to do that!", 1)
        else:
            sleep(0.5)
            print("You leave the inn dissatisfied with the exorbitant prices.", 1)

class a_Forage: #Go foraging in your current area in hopes of finding basic resources
    def __init__(self):
        self.name = "Forage"
        activities_list[self.name] = self

    def __str__(self):
        return f"{self.name}: Use 10 energy to go foraging in the wilderness of {p.current_area.name}, trying to find usable materials and goods."
    
    def __call__(self, area):
        if p.energy >= 10:
            p.energy -= 10
            print(area.exploring, 2)
            potential_items = []
            for item in p.items_list:
                if p.items_list[item].tier <= area.level+1 and p.items_list[item].tier >= area.level-2 and p.items_list[item].slot == "Miscellaneous":
                    potential_items.append([item, f.limit(p.items_list[item].lootweight, 10)])
            chosen_item = p.items_list[f.weighted_random(potential_items)]
            has_tool = False
            if len(chosen_item.val1) == 0:
                has_tool = True
            for required_tool in chosen_item.val1:
                if p.items_list[required_tool].quantity >= 1:
                    has_tool = True
            message = chosen_item.action + "." if has_tool else chosen_item.action + ", but you don't have the right tool to harvest it!"
            print(message, 1)
            if has_tool:
                amount = random.randint(chosen_item.val2, chosen_item.val3)
                chosen_item.quantity += amount
                print(f"+{amount} {chosen_item.name}", 0.5)
        else:
            print("You don't have enough energy to do that!", 1)

class a_Hunt: #Encounter a random wild animal whose level is similar to the level of the current area. Most animals should be fairly weak and prioritize escaping over doing damage, but some higher level ones may pose a more serious threat
    def __init__(self):
        self.name = "Hunt"
        activities_list[self.name] = self

    def __str__(self):
        return f"{self.name}: Use 10 energy to go hunting in the wilderness of {p.current_area.name}, in hopes of encountering a wild animal to hunt for its resources."
    
    def __call__(self, area):
        if p.energy >= 5:
            p.energy -= 5
            print(area.exploring, 2)
            enemy = f.weighted_random(area.wildlife)
            print(enemy.intro, 3)
            b.fight(enemy)
        else:
            print("You don't have enough energy to do that!", 1)

#########################################
#                 AREAS                 #
#########################################

chalgos = Area("Chalgos", "A small, peaceful town in the middle of the Gavlynn Forest", "", "Settlement", 1, 0, k_start, "The guards are barring you from entering the town.", ["Shop", "Rest"], [], [], [[c.goblin, 100], [c.bandit, 30]], [])
gavlynn_forest = Area("Gavlynn Forest", "A dark, dense forest... venturing far from the trail is dangerous here...", "You begin venturing off the beaten path and into the dense foliage...", "Field", 1, 300, k_start, "You're not yet ready to venture outside the safety of the town.", ["Explore", "Forage", "Hunt"], [[e.Enemy(), 55], [e.GoldPouch(), 20], [e.FindItem(), 25]], [[c.goblin, 50], [c.wolf, 30], [c.skeleton_archer, 20], [c.elusive_ghost, 10]], [[c.wolf, 50], [c.goblin, 20], [c.bandit, 80]], [[c.deer, 50], [c.rabbit, 80], [c.turkey, 70]])
farlands = Area("Farlands", "A very far away place", "You begin venturing off the beaten path and into the dense foliage...", "Field", 1, 1700, k_start, "You're not yet ready to venture outside the safety of the town.", ["Explore", "Forage", "Hunt"], [[e.Enemy(), 55], [e.GoldPouch(), 20], [e.FindItem(), 25]], [[c.goblin, 50], [c.wolf, 30], [c.skeleton_archer, 20], [c.elusive_ghost, 10]], [[c.wwe_champ, 50], [c.elusive_ghost, 20]], [[c.deer, 80], [c.rabbit, 60], [c.turkey, 30]])

#########################################
#            INITIALIZATION             #
#########################################

temp_globals = globals().copy() #initializes all the activities, which add themselves to a list of possible activities
for globals_object in temp_globals:
    if globals_object[:2] == "a_":
        globals()[globals_object]()
