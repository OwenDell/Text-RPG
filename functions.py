#########################################
#               IMPORTS                 #
#########################################

import random
import time

#########################################
#           GLOBAL VARIABLES            #
#########################################

printing = True
sleeping = True
sleepmultiplier = 1
_print = print

#########################################
#          BACK-END FUNCTIONS           #
#########################################

def weighted_random(choices): #takes list of lists that each contain 2 values; a possible choice and its associated chance of being selected. It then goes through this list and generates a random value from 0-the sum of all possible choices. If the random value falls within the given choices chance range then it is chosen, if not it's removed from the list of possible choices and it moves to the next possible choice.
    possible_choices = choices.copy()
    for chance in choices:
        if chance[1] >= random.randint(0, sum([possible_choices[i][1] for i in range(len(possible_choices))])):
            return chance[0]
        possible_choices.remove(chance)
        
def capitalize(string): #splits a string into a list of separate words, and formats every word so the first letter is capitalized and every other letter is lowercase. Useful for handling player inputs
    string = string.split()
    for index, word in enumerate(string):
        string[index] = word[0].upper() + word[1:].lower()
    return " ".join(string)

def limit(inputs, maxes, mins=0): #takes 1 or more values for the inputs, maxes, and mins (can be either lists or single variables); goes through every value in inputs and sets them to either the corresponding min or max if it goes outside their range.
    inputs = [inputs] if not isinstance(inputs, list) else inputs
    maxes = [maxes] * len(inputs) if not isinstance(maxes, list) else maxes
    mins = [mins] * len(inputs) if not isinstance(mins, list) else mins
    for index, value in enumerate(inputs):
        inputs[index] = maxes[index] if value > maxes[index] else inputs[index]
        inputs[index] = mins[index] if value < mins[index] else inputs[index]
    inputs = inputs[0] if len(inputs) == 1 else inputs
    return inputs

def basic_attack(move, user, target, message=f"the attacker attacked"): #used for both creature and player attacks that don't have any special functions to them, and simply do damage.
    target.health -= move.damage
    print(f"{message}, dealing {move.damage} damage!")

def print_override(string, sleeptime=0): #replacement for the default print function that adds a check to see if 'printing' is enabled, can be very convenient at times when you want functions to run in the background without them spewing out all their associated text.
    if printing == True:
        print(string)
        if sleeping == True:
            time.sleep(sleeptime*sleepmultiplier)
            
def disable_sleep():
    global sleeping
    sleeping = False
    
def sleep(sleeptime):
    if sleeping == True:
        time.sleep(sleeptime*sleepmultiplier)

def header(string="", sleeptime=0): #this is used to print title bars to separate large portions of text such as when printing long vertical lists, used for aesthetic appeal
    braces = "[]" if len(string) > 0 else "--"
    side_dashes = ["-"] * (24-round(len(string)/2))
    print_override("".join(side_dashes) + braces[0] + string + braces[1] + "".join(side_dashes), sleeptime)
