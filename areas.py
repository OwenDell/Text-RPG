#########################################
#               IMPORTS                 #
#########################################

import functions as f
import playerstats as p

#########################################
#           GLOBAL VARIABLES            #
#########################################

areas = [] #a list of all areas that gets filled every time a new creature is initialized.

#########################################
#               CLASSES                 #
#########################################

class Area:
    def __init__(self, name, description, tier, access, encounters, local_enemies):
        self.name = name
        self.description = description
        self.tier = tier
        self.access = access
        self.encounters = encounters
        self.local_enemies = local_enemies
        areas.append(self)

    def __str__(self):
        return f"Zone {self.tier}: {self.name}, {self.description}"
    
    def find_encounter(self):
        f.weighted_random(self.encounters)(self)
        
#########################################
#                 AREAS                 #
#########################################