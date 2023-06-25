#########################################
#               IMPORTS                 #
#########################################

import functions as f
import playerstats as p
import creatures as c
import areas as a
import encounters as e
import battle as b
import statuses as s
import npc as n

#########################################
#           GLOBAL VARIABLES            #
#########################################

print = f.print_override
sleep = f.sleep
encyclopedia = f.encyclopedia
player = c.player

#########################################
#          BACK-END FUNCTIONS           #
#########################################

def check_encyclopedia(subject=False, category=False):
    if not category:
        f.header("Encyclopedia", 0.5)
        for e_category in encyclopedia:
            print(e_category, 0.2)
        f.header("", 0.5)
        category = f.capitalize(input("What category of the encyclopedia do you want to view? "))
        sleep(0.5)
    if category in encyclopedia:
        if len(encyclopedia[category]) < 1:
            f.header(f"Encyclopedia ({category})", 0.5)
            print(f"You don't have any entries for {category}. Collect more entries for this category by encountering {category} out in the world. You only need to see something for it to be added to the encyclopedia.", 0.3)
            f.header("", 0.5)
        else:
            if not subject:
                f.header(f"Encyclopedia ({category})", 0.5)
                for e_subject in encyclopedia[category]:
                    print(e_subject, 0.2)
                f.header("", 0.5)
                subject = f.capitalize(input(f"What subject of {category} do you want to view? "))
                sleep(0.5)
            if subject in encyclopedia[category]:
                sub = encyclopedia[category][subject]
                f.header(f"Encyclopedia ({subject})", 0.5)
                if category == "Enemies":
                    print(f"\nLevel: {sub.level}", 0.3)
                    print(f"Health: {sub.maxHP}", 0.3)
                    print(f"Gold: ~{sub.gold}", 0.3)
                    print(f"XP: {sub.XP}", 0.3)
                    print(f"Evasion: {sub.evasion}", 0.3)
                    print(f"\nMoves:", 0.3)
                    for move in range(len(sub.moves)):
                        _move = c.moves_list[sub.moves[move][0]]
                        accuracy_desc =  f" | {_move.accuracy}% Accuracy" if _move.accuracy != -1 else ""
                        if _move.name in encyclopedia["Moves"]:
                            print(f"{_move.name}: {_move.description} that deals {_move.damage} {_move.damagetype} damage. [{_move.critchance}% Critical Chance{accuracy_desc}]", 0.3)
                        else:
                            print("?????????", 0.3)
                    print(f"\nReceived Damage Multipliers:", 0.3)
                    for dmg in sub.damage_resistances:
                        print(f"{dmg}: {sub.damage_resistances[dmg]*100}%", 0.3)
                elif category == "Weapons":
                    print(f"\n{sub}\n", 0.3)
                    print(f"Equipment Slot: {f.capitalize(sub.slot)}", 0.3)
                    print(f"Tier: {sub.tier}", 0.3)
                    print(f"# in Inventory: {sub.quantity}", 0.3)
                    print(f"Estimated Value: {sub.value}", 0.3)
                    print(f"Rarity: {abs(11-sub.lootweight)}", 0.3)
                    print(f"Accuracy Bonus: {sub.accuracy}%", 0.3)
                    print(f"Crit Chance Bonus: {sub.critchance}%", 0.3)
                    print(f"Crit Damage Multiplier: {sub.critmultiplier*100}%", 0.3)
                    print(f"\nDamage Types:\n", 0.3)
                    for dmg in sub.damages:
                        operator = "+" if (sub.damages[dmg]*player.damage_affinities[dmg])-sub.damages[dmg] >= 0 else ""
                        print(f"{dmg}: {sub.damages[dmg]} ({operator}{round((sub.damages[dmg]*player.damage_affinities[dmg])-sub.damages[dmg], 1)})", 0.3)
                    if len(sub.buffs) > 0:
                        print(f"\nBuffs:\n", 0.3)
                        for buff in sub.buffs:
                            operator = "+" if buff[1] >= 0 else ""
                            print(f"{s.buffs_list[buff[0]].name}: {s.buffs_list[buff[0]].description} [{operator}{buff[1]}]", 0.3)
                    print(f"\nWeapon Moves:\n", 0.3)
                    for move in sub.moves:
                        print(c.moves_list[move], 0.3)
                elif category == "Armor":
                    print(f"\n{sub}\n", 0.3)
                    print(f"Equipment Slot: {f.capitalize(sub.slot)}", 0.3)
                    print(f"Tier: {sub.tier}", 0.3)
                    print(f"# in Inventory: {sub.quantity}", 0.3)
                    print(f"Estimated Value: {sub.value}", 0.3)
                    print(f"Rarity: {abs(11-sub.lootweight)}", 0.3)
                    print(f"\nDamage Resistances:\n", 0.3)
                    for resistance in sub.resistances:
                        operator = "+" if sub.resistances[resistance] >= 0 else ""
                        print(f"{resistance}: {operator}{round(sub.resistances[resistance]*100, 1)}%", 0.3)
                    if len(sub.buffs) > 0:
                        print(f"\nBuffs:\n", 0.3)
                        for buff in sub.buffs:
                            operator = "+" if buff[1] >= 0 else ""
                            print(f"{s.buffs_list[buff[0]].name}: {s.buffs_list[buff[0]].description} [{operator}{buff[1]}]", 0.3)
                elif category == "Items":
                    print(f"\n{sub.description}\n", 0.3)
                    print(f"Type: {sub.slot}", 0.3)
                    print(f"Tier: {sub.tier}", 0.3)
                    print(f"# in Inventory: {sub.quantity}", 0.3)
                    print(f"Estimated Value: {sub.value}", 0.3)
                    if sub.accuracy != -1:
                        print(f"Accuracy: {sub.accuracy}%", 0.3)
                    print(f"Rarity: {abs(11-sub.lootweight)}", 0.3)
                elif category == "Moves":
                    if sub.name == "Options" or sub.name == "Encyclopedia" or sub.name == "Flee" or sub.name == "Use":
                        print(f"\n{sub}", 0.3)
                    else:
                        print(f"\n{sub.description}\n", 0.3)
                        print(f"Learned: {str(sub.learned)}", 0.3)
                        print(f"Associated Weapon: {sub.associated_weapon.name}", 0.3)
                        print(f"Damage: {sub.damage} (+{sub.bonusdamage} with weapon)", 0.3)
                        print(f"Damage Type: {sub.damagetype}", 0.3)
                        accuracy = f"{sub.accuracy}%" if sub.accuracy != -1 else "Guaranteed"
                        print(f"Accuracy: {accuracy}", 0.3)
                        print(f"Crit Chance: {sub.critchance}%", 0.3)
                        print(f"Mana Cost: {sub.mana}", 0.3)
                        print(f"Energy Cost: {sub.energy}", 0.3)
                elif category == "Characters":
                    print(f"\n{sub.description}\n", 0.3)
                    print(f"Type: {sub.type}", 0.3)
                    print(f"Relation: {sub.relation}", 0.3)
                    print(f"Quests: {sub.quests}", 0.3)
                    print(f"\nLocation(s):\n", 0.3)
                    for location in sub.locations:
                        if location in encyclopedia["Areas"]:
                            print(a.areas[location], 0.3)
                        else:
                            print("?????????", 0.3)
                elif category == "Areas":
                    print(f"\n{sub.description}\n", 0.3)
                    print(f"Type: {sub.type}", 0.3)
                    print(f"Level: {sub.level}", 0.3)
                    print(f"Access: {str(sub.access)}", 0.3)
                    print(f"Location: {sub.distance} ({abs(sub.distance-p.position)}m away)", 0.3)
                    print(f"\nActivities:\n", 0.3)
                    for activity in sub.activities:
                        print(activity, 0.3)
                    if len(sub.local_enemies) > 0:
                        print(f"\nLocal Enemies:\n", 0.3)
                        for enemy in sub.local_enemies:
                            if enemy[0].name in encyclopedia["Enemies"]:
                                print(enemy[0], 0.3)
                            else:
                                print("?????????", 0.3)
                elif category == "Stats":
                    print("Work in progress", 0.3)
                elif category == "Mechanics":
                    print("Work in progress", 0.3)
                elif category == "Tutorials":
                    print("Work in progress", 0.3)
                print("")
                f.header("", 0.5)
            else:
                print(f"Invalid response, {subject} either unrecognized or locked encyclopedia subject.", 1)
                subject = False
    else:
        print(f"Invalid response, your response must be the name of a listed encyclopedia category.", 1)
        category = False

f.check_encyclopedia = check_encyclopedia