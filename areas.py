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

#########################################
#           GLOBAL VARIABLES            #
#########################################

print = f.print_override
sleep = f.sleep
player = c.player
areas = {} #a list of all areas that gets filled every time a new area is initialized.
activities_list = {}
k_start = True

#########################################
#          BACK-END FUNCTIONS           #
#########################################

def determine_area():
    for area in areas:
        if p.position >= areas[area].distance:
            p.current_area = areas[area]

#########################################
#               CLASSES                 #
#########################################

class Area:
    def __init__(self, name, description, exploring, type, level, distance, access, denialmessage, activities, encounters, local_enemies, highway_enemies):
        self.name = name
        self.description = description
        self.exploring = exploring
        self.type = type
        self.level = level
        self.distance = distance
        self.access = access
        self.denialmessage = denialmessage
        self.activities = activities
        self.encounters = encounters
        self.local_enemies = local_enemies
        self.highway_enemies = highway_enemies
        areas[self.name] = self

    def __str__(self):
        return f"{self.name} ({self.type}): {self.description}. [{abs(self.distance-p.position)}m away]"
    
    def find_encounter(self):
        f.weighted_random(self.encounters)(self)

    def travel(self):
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
            while (iteration%7 == 0 and abs(p.position-self.distance) > p.speed) and abs(distance_traveled) > 0:
                print(f"You've traveled {abs(distance_traveled)}/{abs(self.distance-startpoint)}m and have {player.health}/{player.maxHP} HP and {p.energy}/{p.maxEnergy} Energy, do you want to continue onwards?", 1.5)
                response = f.capitalize(input("Enter 'Y' or 'N' to continue onwards, or 'Use' if you'd like to use an item: "))
                sleep(0.5)
                if response == "N":
                    p.position = startpoint
                    determine_area()
                    print(f"The journey proved too difficult for you, so you turned back to {p.current_area.name}...", 3)
                    break
                elif response == "Y":
                    print(f"You push onwards towards {self.name}, with {abs(self.distance-p.position)}m left to go.", 3)
                    break
                elif response == "Use":
                    c.moves_list["Use"](player, player)
                    sleep(0.3)
                else:
                    print("Invalid response, please enter either 'Y', 'N', or 'Use'.", 0.8)
                    pass
            if response == "N":
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
        if response != "N":
            p.position = self.distance
            determine_area()
            print(f"You've arrived at {self.name}.", 1)

#########################################
#              ACTIVITIES               #
#########################################
        
class a_Explore:
    def __init__(self):
        self.name = "Explore"
        global activities_list
        activities_list[self.name] = self

    def __str__(self):
        return f"{self.name}: Explore around in your current area to find treasure, foes, and special encounters."
    
    def __call__(self, area):
        if p.energy > 10:
            p.energy -= 10
            print(area.exploring)
            sleep(3)
            area.find_encounter()
            sleep(0.5)
        else:
            print("You don't have enough energy to do that!")

#########################################
#                 AREAS                 #
#########################################

chalgos = Area("Chalgos", "A small, peaceful town in the middle of the Gavlynn Forest", "", "Settlement", 1, 0, k_start, "The guards are barring you from entering the town.", [], [], [], [[c.goblin, 100]])
gavlynn_forest = Area("Gavlynn Forest", "A dark, dense forest... venturing far from the trail is dangerous here...", "You begin venturing off the beaten path and into the dense foliage...", "Field", 1, 300, k_start, "You're not yet ready to venture outside the safety of the town.", ["Explore"], [[e.Enemy(), 55], [e.GoldPouch(), 20], [e.FindItem(), 25]], [[c.goblin, 50], [c.wolf, 30], [c.skeleton_archer, 20], [c.elusive_ghost, 10]], [[c.wolf, 50], [c.goblin, 20], [c.bandit, 80]])
farlands = Area("Farlands", "A very far away place", "You begin venturing off the beaten path and into the dense foliage...", "Field", 1, 1700, k_start, "You're not yet ready to venture outside the safety of the town.", ["Explore"], [[e.Enemy(), 55], [e.GoldPouch(), 20], [e.FindItem(), 25]], [[c.goblin, 50], [c.wolf, 30], [c.skeleton_archer, 20], [c.elusive_ghost, 10]], [[c.wwe_champ, 50], [c.elusive_ghost, 20]])

#########################################
#            INITIALIZATION             #
#########################################

temp_globals = globals().copy() #initializes all the activities, which add themselves to a list of possible activities
for globals_object in temp_globals:
    if globals_object[:2] == "a_":
        globals()[globals_object]()
