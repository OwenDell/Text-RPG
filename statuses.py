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

print = f.print_override
sleep = f.sleep
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

class Status:
    def __init__(self, name, description, application_list, recurring_list, recovery_list, cured_list, cures):
        self.name = name
        self.description = description
        self.application_list = application_list
        self.recurring_list = recurring_list
        self.recovery_list = recovery_list
        self.cured_list = cured_list
        self.cures = cures
        self.duration = 0
        statuses_list[self.name] = self
    
    def __str__(self):
        return f"{self.name}: {self.description}. [{self.duration} turns remaining]"
    
    def recover(self, target, index):
        message = "Your" if target is player else f"The {target.name}'s"
        for recovery in self.recovery_list:
            effects_list[recovery](target)
        print(f"{message} {self.name} effect has worn off.", 0.7)
        del target.statuses[index]

    def apply(self, target, duration):
        message = "You've" if target is player else f"The {target.name} has"
        if duration == -1:
            print(f"{message} received the status effect {self.name} indefinitely.", 1)
            self.duration = "infinite"
            existed = False
            for i, eff in enumerate(target.statuses):
                if eff[0] == self.name:
                    existed = True
                    target.statuses[i][1] = duration
            if existed == False:
                target.statuses.append([self.name, duration])
        if duration < 1:
            for application in self.application_list:
                effects_list[application](target)
        else:
            self.duration = duration if target is player else self.duration
            print(f"{message} received the status effect {self.name} for {duration} turns!", 1)
            existed = False
            for i, eff in enumerate(target.statuses):
                if eff[0] == self.name:
                    existed = True
                    if target.statuses[i][1] < duration and not (self.duration == "infinite" and target is player):
                        target.statuses[i][1] = duration
            if existed == False:
                target.statuses.append([self.name, duration])
                for application in self.application_list:
                    effects_list[application](target)

    def cure(self, target, index):
        message = "You've" if target is player else f"The {target.name} has"
        print(f"{message} been cured of {self.name}!", 0.8)
        for cured in self.cured_list:
            effects_list[cured](target)
        del target.statuses[index]
    
    def __call__(self, target, index): 
        message = "Your" if target is player else f"The {target.name}'s"
        if target.statuses[index][1] == 0:
            self.recover(target, index)
        elif target.statuses[index][1] == -1:
            for recurring in self.recurring_list:
                effects_list[recurring](target)
        else:
            print(f"{message} {self.name} effect has {target.statuses[index][1]} turns remaining.", 0.8)
            for recurring in self.recurring_list:
                effects_list[recurring](target)
            target.statuses[index][1] -= 1
            self.duration = self.duration - 1 if target is player else self.duration

class Standard_Effect:
    def __init__(self, name, message_type, verb, amount, affect, operator):
        self.name = name
        self.message_type = message_type
        self.verb = verb
        self.amount = amount
        self.affect = affect
        self.operator = operator
        effects_list[self.name] = self

    def __call__(self, target):
        targeted = ("You've", "Your", "You") if target is player else (f"The {target.name} has", f"The {target.name}'s", f"The {target.name}")
        message = f"{targeted[0]} {self.verb}! {self.operator}{self.amount} {self.affect}." if self.message_type == 1 else \
            f"{targeted[0]} taken {self.amount} damage from the {self.verb} status effect!" if self.message_type == 2 else \
            f"{targeted[1]} {self.affect} {self.verb} by {self.amount}." if self.message_type == 3 else \
            f"{targeted[2]} {self.verb} {self.amount} {self.affect}." if self.message_type == 4 else \
            f"{targeted[1]} {self.affect} {self.verb}." if self.message_type == 5 else f"{targeted[0]} been affected by {self.name}."
        print(message, 0.7)
        target.health = operators[self.operator](target.health, self.amount) if self.affect == "Health" else target.health
        p.mana = operators[self.operator](p.mana, self.amount) if self.affect == "Mana" else p.mana
        p.energy = operators[self.operator](p.energy, self.amount) if self.affect == "Energy" else p.energy
        target.gold = operators[self.operator](target.gold, self.amount) if self.affect == "Gold" else target.gold
        p.effective_strength = operators[self.operator](p.effective_strength, self.amount) if self.affect == "Strength" else p.effective_strength
        p.effective_dexterity = operators[self.operator](p.effective_dexterity, self.amount) if self.affect == "Dexterity" else p.effective_dexterity
        p.effective_intelligence = operators[self.operator](p.effective_intelligence, self.amount) if self.affect == "Intelligence" else p.effective_intelligence
        p.speed = operators[self.operator](p.speed, self.amount) if self.affect == "Speed" else p.speed

class Apply_Cure:
    def __init__(self, name):
        self.name = name
        effects_list[self.name] = self

    def __call__(self, target):
        target.cures_list[self.name] = True

#Future effect types could be things like weapon and armor enchantments, or delayed damage that only occurs after a certain number of turns if unattended to

#########################################
#          BACK-END FUNCTIONS           #
#########################################

def recur_statuses(target, exhaust=False):
    while True:
        for index, status in enumerate(target.statuses):
            statuses_list[status[0]](target, index)
        if len(target.statuses) == 0 or not exhaust:
            break

def cure_check(target, cure_all=False):
    for index, ailment in enumerate(target.statuses):
        for possible_cure in statuses_list[ailment[0]].cures:
            if target.cures_list[possible_cure] == True or cure_all == True:
                statuses_list[ailment[0]].cure(target, index)
    for cure_item in target.cures_list:
        target.cures_list[cure_item] = False

#########################################
#               STATUSES                #
#########################################

exhaustion = Status("Exhaustion", "You're completely out of Energy and have worse stats as a result", ["-1 Strength", "-1 Dexterity", "-1 Intelligence", "-50 Speed"], [], ["+1 Strength", "+1 Dexterity", "+1 Intelligence", "+50 Speed"], ["+1 Strength", "+1 Dexterity", "+1 Intelligence", "+50 Speed"], ["Saturated"])
lesser_poison = Status("Lesser Poison", "A minor poison that deals 10 damage per turn", [], ["Poison 1"], [], [], ["Lesser Antidote", "Cleanse"])
well_fed = Status("Well Fed", "Increases your Strength, Dexterity, and Intelligence by 1", ["+1 Strength", "+1 Dexterity", "+1 Intelligence"], [], ["-1 Strength", "-1 Dexterity", "-1 Intelligence"], ["-1 Strength", "-1 Dexterity", "-1 Intelligence"], [])
minor_doom = Status("Minor Doom", "Your doom is imminent... you'll take 30 damage soon..", [], [], ["Doom 1"], [], ["Victory", "Cleanse"])
lesser_antidote = Status("Lesser Antidote", "Makes you immune to lesser poisons", ["Lesser Antidote"], ["Lesser Antidote"], [], [], [])
antidote = Status("Antidote", "Makes you immune to common poisons", ["Lesser Antidote", "Antidote"], ["Lesser Antidote", "Antidote"], [], [], [])
cleanse = Status("Cleanse", "Makes you immune to almost any ailment", ["Cleanse"], ["Cleanse"], [], [], [])

#########################################
#           STANDARD EFFECTS            #
#########################################

poison1 = Standard_Effect("Poison 1", 2, "poison", 10, "Health", "-")
doom1 = Standard_Effect("Doom 1", 2, "doom", 50, "Health", "-")
strength_up1 = Standard_Effect("+1 Strength", 3, "increased", 1, "Strength", "+")
strength_down1 = Standard_Effect("-1 Strength", 3, "decreased", 1, "Strength", "-")
dexterity_up1 = Standard_Effect("+1 Dexterity", 3, "increased", 1, "Dexterity", "+")
dexterity_down1 = Standard_Effect("-1 Dexterity", 3, "decreased", 1, "Dexterity", "-")
intelligence_up1 = Standard_Effect("+1 Intelligence", 3, "increased", 1, "Intelligence", "+")
intelligence_down1 = Standard_Effect("-1 Intelligence", 3, "decreased", 1, "Intelligence", "-")
speed_up50 = Standard_Effect("+50 Speed", 3, "increased", 50, "Speed", "+")
speed_down50 = Standard_Effect("-50 Speed", 3, "decreased", 50, "Speed", "-")

#########################################
#                CURES                  #
#########################################

cleanse = Apply_Cure("Cleanse")
antidote1 = Apply_Cure("Lesser Antidote")
antidote2 = Apply_Cure("Antidote")

#########################################
#            INITIALIZATION             #
#########################################