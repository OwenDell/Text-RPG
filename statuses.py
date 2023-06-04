#########################################
#               IMPORTS                 #
#########################################

import random
import operator
import functions as f
import playerstats as p
import creatures as c

#########################################
#           GLOBAL VARIABLES            #
#########################################

player = c.player
moves_list = c.moves_list
specials_list = c.specials_list
statuses_list = {} #Statuses are the full status effect with its own systems for application, recovery, and recurring impacts. They use effects, which are the back-end functions that actually do things.
effects_list = {} #Empty dictionary of all effects waiting to be filled during initialization
operators = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul
}

#########################################
#               CLASSES                 #
#########################################

class Effect:
    def __init__(self, name, description, application, recurring, recovery, duration, antidote):
        self.name = name
        self.description = description
        self.application = application
        self.recurring = recurring
        self.recovery = recovery
        self.duration = duration
        self.antidote = antidote
        statuses_list[self.name] = self
    
    def __str__(self):
        return f"{self.name}: {self.description}. [{self.duration} turns remaining]"
    
    def recover(self, target, index):
        message = "Your" if target is player else f"The {target.name}'s"
        effects_list[self.recovery](target)
        print(f"{message} {self.name} effect has worn off.")
        del target.statuses[index]

    def apply(self, target, duration):
        message = "You've" if target is player else f"The {target.name} has"
        print(f"{message} received the status effect {self.name} for {duration} turns!")
        effects_list[self.application](target)
        target.statuses.append([self.name, duration])
        
    def __call__(self, target, index): 
        message = "Your" if target is player else f"The {target.name}'s"
        if target.statuses[index][1] < 1:
            self.recover(target, index)
        else:
            effects_list[self.recurring](target)
            print(f"{message} {self.name} effect has {target.statuses[index][1]} turns remaining.")
            self.duration -= 1

class Regenerate:
    def __init__(self, name, verb, amount, affect, operator):
        self.name = name
        self.verb = verb
        self.amount = amount
        self.affect = affect
        self.operator = operator
        effects_list[self.name] = self

    def __call__(self, target):
        message = "You've" if target is player else f"The {target.name} has"
        print(f"{message} been {self.verb}! {self.operator}{self.amount} {self.affect}")
        target.health = operators[self.operator](target.health, self.amount) if self.affect == "Health" else target.health
        p.mana = operators[self.operator](p.mana, self.amount) if self.affect == "Mana" else p.mana
        p.energy = operators[self.operator](p.energy, self.amount) if self.affect == "Energy" else p.energy

#########################################
#          BACK-END FUNCTIONS           #
#########################################



#########################################
#               STATUSES                #
#########################################



#########################################
#               EFFECTS                 #
#########################################



#########################################
#            INITIALIZATION             #
#########################################

