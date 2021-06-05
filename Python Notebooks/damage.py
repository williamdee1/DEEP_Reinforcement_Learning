import random
import numpy as np
from pokemon import Pokemon
from moves import Move

def calc_damage(att_pokemon, def_pokemon, move, types):
    # Calculating Modifiers
    # ----------------------#

    # Stage Stat Modifiers - Altering Stats Based on Prior Effects
    # ---------------------------------------------------------------#
    stages = [-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6]
    stage_mult = [0.25, 0.28, 0.33, 0.4, 0.5, 0.66, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
    for a, b in zip(stages, stage_mult):
        if att_pokemon.atk_stage == a:
            att_pokemon.current_atk = att_pokemon.current_atk * b
        if att_pokemon.spe_stage == a:
            att_pokemon.current_spe = att_pokemon.current_spe * b
        if att_pokemon.spd_stage == a:
            att_pokemon.current_spd = att_pokemon.current_spd * b
        if def_pokemon.def_stage == a:
            def_pokemon.current_def = def_pokemon.current_def * b

    # Critical Hit Modifier:
    # -----------------------#
    higher_crit_moves = ['Razor Leaf', 'Slash']

    if move not in higher_crit_moves:
        crit_chance = att_pokemon.current_spd / 512
    else:
        crit_chance = att_pokemon.current_spd / 64

    crit_or_not = np.random.choice([1, 0], 1, p=[crit_chance, 1 - crit_chance])

    if crit_or_not[0] == 1:
        crit_mod = ((2 * att_pokemon.level) + 5) / (att_pokemon.level + 5)
        #print("It's a critical hit!")
    else:
        crit_mod = 1.0

    # Random Multiplier #
    # -------------------#
    rand_mod = random.randint(217, 255) / 255

    # Same-Type Attack Damage Modifier:
    # ----------------------------------#
    if (move.move_type == att_pokemon.type_1) | (move.move_type == att_pokemon.type_2):
        stab_mod = 1.5
    else:
        stab_mod = 1.0

    # Type-Effectiveness Multiplier
    # ------------------------------#
    effect_mod = type_effect(def_pokemon, move, types)

    # Calculating whether it was a super-effective move:
    if effect_mod > 1.0:
        super_eff = True
    else:
        super_eff = False

    # Burn Modifier
    # ------------------#
    if (att_pokemon.burn == True) & (move.move_cat == 'Physical'):
        burn_mod = 0.5
    else:
        burn_mod = 1.0

    # Total Modifier
    # ------------------#
    total_damage_modifier = crit_mod * rand_mod * stab_mod * effect_mod * burn_mod

    # Calculating Attack Power with Modifiers
    # -----------------------------------------#

    # Chooses attack stat if move type is physical, otherwise uses the special stat:
    if move.move_cat == 'Physical':
        attack_stat = att_pokemon.current_atk
    else:
        attack_stat = att_pokemon.current_spe

    # Total Damage Dealt
    # ------------------#
    if move.move_power > 0:
        damage_dealt = round(((((((2 * att_pokemon.level) / 5) + 2) * move.move_power *
                      (attack_stat / def_pokemon.current_def)) / 50) + 2) * total_damage_modifier)
    else:
        damage_dealt = 0

    # Resetting Attack Stat
    # ------------------#
    att_pokemon.current_atk = att_pokemon.initial_atk

    return damage_dealt, super_eff


def type_effect(def_pokemon, move, types):
    effect_mod_1 = 1.0
    effect_mod_2 = 1.0

    # Altering Effectiveness modifier if the defending pokemon is weak/ strong against chosen move:
    for c, d, e in zip(types.mov_type.to_list(), types.def_type.to_list(), types.multiplier.to_list()):
        if (move.move_type == c) & (def_pokemon.type_1 == d):
            effect_mod_1 = e
        if (move.move_type == c) & (def_pokemon.type_2 == d):
            effect_mod_2 = e

    effect_mod = effect_mod_1 * effect_mod_2

    return effect_mod

def status_move_effect(att_pokemon, def_pokemon, move, potions_available):
    # Effects targeting opposing pokemon
    if move.move_effect == 'atk-':
        if def_pokemon.atk_stage > -5:
            def_pokemon.atk_stage += -1
    elif move.move_effect == 'def-':
        if def_pokemon.def_stage > -5:
            def_pokemon.def_stage += -1
    elif move.move_effect == 'def--':
        if def_pokemon.def_stage > -5:
            def_pokemon.def_stage += -2

    # Effects on users pokemon
    elif move.move_effect == 'atk+':
        if att_pokemon.atk_stage < 5:
            att_pokemon.atk_stage += 1
        return 'atk+'
    elif move.move_effect == 'spe+':
        if att_pokemon.spe_stage < 5:
            att_pokemon.spe_stage += 1
        return 'spe+'
    elif move.move_effect == 'spd+':
        if att_pokemon.spd_stage < 5:
            att_pokemon.spd_stage += 1
    elif move.move_effect == 'def+':
        if att_pokemon.def_stage < 5:
            att_pokemon.def_stage += 1
        return 'def+'
    elif move.move_effect == 'def++':
        if att_pokemon.def_stage < 5:
            att_pokemon.def_stage += 2
    elif move.move_effect == 'hp_50':
        if att_pokemon.current_hp < att_pokemon.initial_hp - 50:
            att_pokemon.current_hp += 50
        else:
            att_pokemon.current_hp = att_pokemon.initial_hp
        return 'hp_50'

    # Rest puts the pokemon to sleep and recovers full hp
    elif move.move_effect == 'hp_mx_slp':
        att_pokemon.current_hp = att_pokemon.initial_hp
        att_pokemon.apply_status('sleep')

    # Counts Full Restore as a status effect, restoring full health
    elif move.move_effect == 'hp_max':
        if potions_available > 0:
            att_pokemon.current_hp = att_pokemon.initial_hp
            return 'hp_max'
        else:
            pass

    # Status Effects
    elif move.move_effect == 'confuse':
        # Checks if already confused, if True, doesn't work:
        if def_pokemon.confuse == False:
            def_pokemon.apply_status('confuse')

    elif move.move_effect == 'para':
        # Checks if already confused, if True, doesn't work:
        if def_pokemon.paralyze == False:
            def_pokemon.apply_status('para')

    elif move.move_effect == 'sleep':
        # Checks if already confused, if True, doesn't work:
        if def_pokemon.sleep == False:
            def_pokemon.apply_status('sleep')

    elif move.move_effect == 'poison':
        # Checks if already confused, if True, doesn't work:
        if def_pokemon.poison == False:
            def_pokemon.apply_status('poison')

    # Mirror Move copies the opponents move and goes last
    elif move.move_effect == 'mirror':
        return 'copy_move'

    # Switch Returns a command to switch:
    elif move.move_effect == 'switch1':
        return 'switch1'
    elif move.move_effect == 'switch2':
        return 'switch2'

def status_impact(att_pokemon, moves_dict):
    # Setting what happens if the pokemon has a status effect already:
    # Trigger chance to recover from status, 20% chance to recover
    recover_chance = np.random.choice(5,1, p=[0.2, 0.2, 0.2, 0.2, 0.2]).sum()

    if att_pokemon.confuse == True:
        # 50% chance the pokemon is too confused to act
        too_confused = np.random.choice(2,1, p=[0.5, 0.5]).sum()

        # Check on whether recovers after action (20% chance):
        if recover_chance == 0:
            att_pokemon.confuse = False
            att_pokemon.confuse_counter = 0
        else:
            att_pokemon.confuse_counter += 1
            # When counter reaches 5 turns, recover automatically
            if att_pokemon.confuse_counter == 5:
                att_pokemon.confuse = False
                att_pokemon.confuse_counter = 0

        if too_confused == 0:
            # Pokemon damages itself equal to a tackle attack
            confused_dmg, _ = calc_damage(att_pokemon, att_pokemon, Move('Tackle', moves_dict))
            att_pokemon.take_damage(confused_dmg)
            return 'skip_turn'

    if att_pokemon.paralyze == True:
        # 25% chance the pokemon is too paralyzed to act
        too_paralyzed = np.random.choice(4,1, p=[0.25, 0.25, 0.25, 0.25]).sum()

        if recover_chance == 0:
            att_pokemon.paralyze = False
            att_pokemon.para_counter = 0

        else:
            att_pokemon.paralyze_counter += 1
            # When counter reaches 5 turns, recover automatically
            if att_pokemon.paralyze_counter == 5:
                att_pokemon.paralyze = False
                att_pokemon.paralyze_counter = 0

        if too_paralyzed == 0:
            return 'skip_turn'


    if att_pokemon.poison == True:
        # Poison does damage every turn:
        poison_dmg = (1/16) * (att_pokemon.initial_hp)
        att_pokemon.take_damage(poison_dmg)


    if att_pokemon.sleep == True:

        if recover_chance == 0:
            att_pokemon.sleep = False
            print("%s woke up!" % (att_pokemon.name))
            att_pokemon.sleep_counter = 0

        else:
            att_pokemon.sleep_counter += 1
            print("%s is fast asleep!" % (att_pokemon.name))
            # When counter reaches 5 turns, recover automatically
            if att_pokemon.sleep_counter == 7:
                att_pokemon.sleep = False
                att_pokemon.sleep_counter = 0

            return 'skip_turn'

