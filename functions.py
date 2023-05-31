#########################################
#               IMPORTS                 #
#########################################

import random
import playerstats as p

#########################################
#          BACK-END FUNCTIONS           #
#########################################

def weighted_random(choices):
    possible_choices = choices.copy()
    for chance in choices:
        if chance[1] >= random.randint(0, sum([possible_choices[i][1] for i in range(len(possible_choices))])):
            return chance[0]
        possible_choices.remove(chance)
