#########################################
#               IMPORTS                 #
#########################################

import math
import functions as f
import playerstats as p
import creatures as c

#########################################
#           GLOBAL VARIABLES            #
#########################################

areas = [] #a list of all areas that gets filled every time a new creature is initialized.
activities_list = {}
k_start = True

#########################################
#               CLASSES                 #
#########################################

class Area:
    def __init__(self, name, description, type, distance, access, activities, encounters, local_enemies, highway_enemies):
        self.name = name
        self.description = description
        self.type = type
        self.distance = distance
        self.access = access
        self.activities = activities
        self.encounters = encounters
        self.local_enemies = local_enemies
        self.highway_enemies = highway_enemies
        areas.append(self)

    def __str__(self):
        return f"{self.name} ({self.type}): {self.description}. [{abs(self.distance-p.position)}m away]"
    
    def find_encounter(self):
        f.weighted_random(self.encounters)(self)

#########################################
#              ACTIVITIES               #
#########################################
        
class Explore:
    def __init__(self):
        self.name = "Explore"
        global activities_list
        activities_list[self.name] = self

    def __str__(self):
        return f"{self.name}: Explore around in your current area to find treasure, foes, and special encounters."
    
    def __call__(self, area):
        print(area)

#########################################
#                 AREAS                 #
#########################################

chalgos = Area("Chalgos", "A small, peaceful town in the middle of the Galvynn Forest", "Settlement", 0, k_start, [], [], [], [])
galvynn_forest = Area("Galvynn Forest", "A dark, dense forest... venturing far from the trail is dangerous here...", "Field", 100, k_start, ["Explore"], [], [(c.goblin, 50)], [(c.dog, 20)])

#########################################
#            INITIALIZATION             #
#########################################

temp_globals = globals().copy() #initializes all the activities, which add themselves to a list of possible activities
for globals_object in temp_globals:
    try:
        globals()[globals_object]()
    except:
        pass