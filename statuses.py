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
buffs_list = {} #Buffs are similar to statuses however they have unlimited duration and are tied to equipment. Buffs are gained by equipping equipment with buffs, and they are then lost when that piece of equipment is uneqipped.
effects_list = {} #Empty dictionary of all effects waiting to be filled during initialization.
operators = { #Used with the standard effects class for modularity purposes.
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul
}

#########################################
#               CLASSES                 #
#########################################

class Status: #Class for statuses, which are what control effects. Statuses do most of the logic and front-end parts of the system, whereas effects are what actually happens to the target. Multiple effects will usually be associated with a status.
    def __init__(self, name, description, application_list, recurring_list, recovery_list, cured_list, cures):
        self.name = name #name of the status.
        self.description = description #description of the status.
        self.application_list = application_list #List of effects that will occur when this status is first applied.
        self.recurring_list = recurring_list #List of effects that will occur every turn.
        self.recovery_list = recovery_list #List of effects that will occur when the status duration ends.
        self.cured_list = cured_list #List of effects that will occur when the target is cured of the status prematurely, mostly used for reverting any stat changes back to original.
        self.cures = cures #List of possible cures that would cure the target of this status if triggered.
        self.duration = 0 #The number of turns remaining on this status effect, only used for informing the player the remaining number of turns. The actual duration used for computational purposes is tied to each instance of the status in the creatures statuses list.
        statuses_list[self.name] = self
    
    def __str__(self):
        return f"{self.name}: {self.description}. [{self.duration} turns remaining]"
    
    def recover(self, target, index): #Called when the duration of the status reaches 0. Applies any recovery effects
        message = "Your" if target is player else f"The {target.name}'s"
        for recovery in self.recovery_list:
            effects_list[recovery[0]](target, recovery)
        print(f"{message} {self.name} effect has worn off.", 0.7)
        del target.statuses[index]

    def apply(self, target, duration): #Called when the status is first applied to a creature. If the duration is -1 then it applies indefinitely, and will only go away with a cure. If the target already has this status effect, it just renews the duration. Applies any application effects
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
                effects_list[application[0]](target, application)
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
                    effects_list[application[0]](target, application)

    def cure(self, target, index): #Called when one of the cure conditions is met for this status. Applies any cure effects.
        message = "You've" if target is player else f"The {target.name} has"
        print(f"{message} been cured of {self.name}!", 0.8)
        for cured in self.cured_list:
            effects_list[cured[0]](target, cured)
        del target.statuses[index]
    
    def __call__(self, target, index): #Called every turn that the target has this status. Applies any recurring effects and checks if the status's duration has expired.
        message = "Your" if target is player else f"The {target.name}'s"
        if target.statuses[index][1] == 0:
            self.recover(target, index)
        elif target.statuses[index][1] == -1:
            for recurring in self.recurring_list:
                effects_list[recurring[0]](target, recurring)
        else:
            print(f"{message} {self.name} effect has {target.statuses[index][1]} turns remaining.", 0.8)
            for recurring in self.recurring_list:
                effects_list[recurring[0]](target, recurring)
            target.statuses[index][1] -= 1
            self.duration = self.duration - 1 if target is player else self.duration

class Buff: #Class for buffs, which are much more simplified than statuses as they can only affect the player, never have a duration, and will always either increase or decrease set values by the same amount.
    def __init__(self, name, description, effect):
        self.name = name
        self.description = description
        self.effect = effect
        self.total = 0
        statuses_list[self.name] = self
        buffs_list[self.name] = self

    def __str__(self):
        operator = "+" if self.total >= 0 else ""
        return f"{self.name}: {self.description} [{operator}{self.total}]"
    
    def __call__(*args):
        pass
    
    def add(self, amount):
        self.total += amount
        if self.name not in player.statuses:
            player.statuses.append([self.name, -1])
        if "Affinity" in self.name:
            effects_list["Affinity"](player, [self.effect, amount, "+"])
        elif "Resistance" in self.name:
            effects_list["Resistance"](player, [self.effect, amount, "+"])
        else:
            effects_list[self.effect](player, ["", amount, "+"])

    def remove(self, amount):
        self.total -= amount
        if self.total == 0:
            for index, status in enumerate(player.statuses):
                if status[0] == self.name:
                    del player.statuses[index]
        if "Affinity" in self.name:
            effects_list["Affinity"](player, [self.effect, amount, "-"])
        elif "Resistance" in self.name:
            effects_list["Resistance"](player, [self.effect, amount, "-"])
        else:
            effects_list[self.effect](player, ["", amount, "-"])

class Standard_Effect: #Class for basic, formulaic effects while still being extremely modular.
    def __init__(self, name, message_type, verb, affect):
        self.name = name #name of the effect.
        self.message_type = message_type #The message format that is selected to be printed when this effect occurs. There are multiple possible message formats for modularity sake.
        self.verb = verb #The operating verb that is used in constructing the message that is printed when this effect occurs.
        self.affect = affect #Used for determining what this effect affects. Will usually be health, energy, or a stat.
        effects_list[self.name] = self

    def __call__(self, target, effect):
        amount = effect[1]
        operator = effect[2]
        verb_num = 0 if operator == "+" else 1
        targeted = ("You've", "Your", "You") if target is player else (f"The {target.name} has", f"The {target.name}'s", f"The {target.name}")
        message = f"{targeted[0]} {self.verb[verb_num]}! {operator}{amount} {self.affect}." if self.message_type == 1 else \
            f"{targeted[0]} taken {amount} damage from the {self.verb[verb_num]} status effect!" if self.message_type == 2 else \
            f"{targeted[1]} {self.affect} {self.verb[verb_num]} by {amount}." if self.message_type == 3 else \
            f"{targeted[2]} {self.verb[verb_num]} {amount} {self.affect}." if self.message_type == 4 else \
            f"{targeted[1]} {self.affect} {self.verb[verb_num]}." if self.message_type == 5 else f"{targeted[0]} been affected by {self.name}."
        print(message, 0.7)
        target.health = operators[operator](target.health, amount) if self.affect == "Health" else target.health
        p.mana = operators[operator](p.mana, amount) if self.affect == "Mana" else p.mana
        p.energy = operators[operator](p.energy, amount) if self.affect == "Energy" else p.energy
        player.gold = operators[operator](player.gold, amount) if self.affect == "Gold" else player.gold
        p.effective_vitality = operators[operator](p.effective_vitality, amount) if self.affect == "Vitality" else p.effective_vitality
        p.effective_strength = operators[operator](p.effective_strength, amount) if self.affect == "Strength" else p.effective_strength
        p.effective_dexterity = operators[operator](p.effective_dexterity, amount) if self.affect == "Dexterity" else p.effective_dexterity
        p.effective_intelligence = operators[operator](p.effective_intelligence, amount) if self.affect == "Intelligence" else p.effective_intelligence
        p.effective_faith = operators[operator](p.effective_faith, amount) if self.affect == "Faith" else p.effective_faith
        p.speed = operators[operator](p.speed, amount) if self.affect == "Speed" else p.speed
        p.xp_gain_multiplier = operators[operator](p.xp_gain_multiplier, amount) if self.affect == "XP Gain" else p.xp_gain_multiplier
        if self.affect == "Affinity":
            player.damage_affinities[effect[0]] += amount
        if self.affect == "Resistance":
            player.damage_resistances[effect[0]] += amount

class Apply_Cure: #Simple class for cure effects, necessary for consumable items that apply a cure such as an antidote.
    def __init__(self, name):
        self.name = name
        effects_list[self.name] = self

    def __call__(self, target, effect):
        target.cures_list[self.name] = True

#Future effect types could be things like weapon and armor enchantments, or delayed damage that only occurs after a certain number of turns if unattended to

#########################################
#          BACK-END FUNCTIONS           #
#########################################

def recur_statuses(target, exhaust=False): #command used to call every status the target has once, triggering their recurring effects. If exhaust is True then it will instantly run out every status the target has until they've recovered from all of them, which is a safe way of removing statuses from enemies after battle quickly so that the recovery effects can occur, which is usually where any changed stats would revert back to normal.
    while True:
        for index, status in enumerate(target.statuses):
            statuses_list[status[0]](target, index)
        if len(target.statuses) == 0 or not exhaust:
            break

def cure_check(target, cure_all=False): #checks if any of the cure conditions are met for any of the targets statuses, and cures them if so.
    for index, ailment in enumerate(target.statuses):
        if ailment[0] not in buffs_list:
            for possible_cure in statuses_list[ailment[0]].cures:
                if target.cures_list[possible_cure] == True or cure_all == True:
                    statuses_list[ailment[0]].cure(target, index)
    for cure_item in target.cures_list:
        target.cures_list[cure_item] = False

#########################################
#               STATUSES                #
#########################################

exhaustion = Status("Exhaustion", "You're completely out of Energy and have worse stats as a result", [["Strength", 1, "-"], ["Dexterity", 1, "-"], ["Vitality", 1, "-"], ["Speed", 50, "-"]], [], [["Strength", 1, "+"], ["Dexterity", 1, "+"], ["Vitality", 1, "+"], ["Speed", 50, "+"]], [["Strength", 1, "+"], ["Dexterity", 1, "+"], ["Vitality", 1, "+"], ["Speed", 50, "+"]], ["Saturated"])
lesser_poison = Status("Lesser Poison", "A minor poison that deals 10 damage per turn", [], [["Poison", 10, "-"]], [], [], ["Lesser Antidote", "Cleanse"])
well_fed = Status("Well Fed", "Increases your Strength, Dexterity, and Vitality by 1", [["Strength", 1, "+"], ["Dexterity", 1, "+"], ["Vitality", 1, "+"]], [], [["Strength", 1, "-"], ["Dexterity", 1, "-"], ["Vitality", 1, "-"]], [["Strength", 1, "-"], ["Dexterity", 1, "-"], ["Vitality", 1, "-"]], [])
minor_doom = Status("Minor Doom", "Your doom is imminent... you'll take 30 damage soon..", [], [], [["Doom", 30, "-"]], [], ["Victory", "Cleanse"])
lesser_antidote = Status("Lesser Antidote", "Makes you immune to lesser poisons", [["Lesser Antidote", 0, "+"]], [["Lesser Antidote", 0, "+"]], [], [], [])
antidote = Status("Antidote", "Makes you immune to common poisons", [["Lesser Antidote", 0, "+"], ["Antidote", 0, "+"]], [["Lesser Antidote", 0, "+"], ["Antidote", 0, "+"]], [], [], [])
cleanse = Status("Cleanse", "Makes you immune to almost any ailment", [["Cleanse", 0, "+"]], [["Cleanse", 0, "+"]], [], [], [])

#########################################
#                BUFFS                  #
#########################################

buff_fire_affinity = Buff("Fire Affinity", "Raises your Fire type damage multiplier", "Fire")
buff_fire_resistance = Buff("Fire Resistance", "Raises your resistance to Fire type damage", "Fire")
buff_Vitality = Buff("Vitality", "Raises your Vitality", "Vitality")
buff_Strength = Buff("Strength", "Raises your Strength", "Strength")
buff_Dexterity = Buff("Dexterity", "Raises your Dexterity", "Dexterity")
buff_Intelligence = Buff("Intelligence", "Raises your Intelligence", "Intelligence")
buff_Faith = Buff("Faith", "Raises your Faith", "Faith")
buff_Speed = Buff("Speed", "Raises your Speed", "Speed")
buff_XP_gain = Buff("XP Gain", "Raises your XP gain multiplier", "XP Gain")

#########################################
#           STANDARD EFFECTS            #
#########################################

poison = Standard_Effect("Poison", 2, ["poison", "poison"], "Health")
doom = Standard_Effect("Doom", 2, ["doom", "doom"], "Health")
vitality = Standard_Effect("Vitality", 3, ["increased", "decreased"], "Vitality")
strength = Standard_Effect("Strength", 3, ["increased", "decreased"], "Strength")
dexterity = Standard_Effect("Dexterity", 3, ["increased", "decreased"], "Dexterity")
intelligence = Standard_Effect("Intelligence", 3, ["increased", "decreased"], "Intelligence")
faith = Standard_Effect("Faith", 3, ["increased", "decreased"], "Faith")
speed = Standard_Effect("Speed", 3, ["increased", "decreased"], "Speed")
affinity = Standard_Effect("Affinity", 3, ["increased", "decreased"], "Affinity")
resistance = Standard_Effect("Resistance", 3, ["increased", "decreased"], "Resistance")
xp_gain = Standard_Effect("XP Gain", 3, ["increased", "decreased"], "XP Gain")

#########################################
#                CURES                  #
#########################################

cleanse = Apply_Cure("Cleanse")
antidote1 = Apply_Cure("Lesser Antidote")
antidote2 = Apply_Cure("Antidote")

#########################################
#            INITIALIZATION             #
#########################################