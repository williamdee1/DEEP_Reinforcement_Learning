from damage import type_effect
from moves import Move
import random
import numpy as np

def ai_choose_move(ai_pokemon, trainer_pokemon, types):
    # Four Possible Moves::
    first = ai_pokemon.moves[0]
    second = ai_pokemon.moves[1]
    third = ai_pokemon.moves[2]
    fourth = ai_pokemon.moves[3]

    ai_move_pool = [first, second, third, fourth]
    ai_move_cats = [first.move_cat, second.move_cat, third.move_cat, fourth.move_cat]
    ai_move_pwr = [first.move_power, second.move_power, third.move_power, fourth.move_power]

    # Starting selection bias is equal between moves:
    move_bias = [10, 10, 10, 10]

    # Check 1: Prefer the move with the highest power:
    highest_pwr_idx = np.argmax(ai_move_pwr)
    move_bias[highest_pwr_idx] -= 1

    # Check 2: At random, 10% chance to prefer to use a status move:
    use_status = random.random() <= 0.1

    if use_status:
        for i in range(4):
            if ai_move_cats[i] == 'Status':
                move_bias[i] -= 1
    else:
        for i in range(4):
            if ai_move_cats[i] == 'Status':
                move_bias[i] += 1

    # Check 3: Checks moves effectiveness, prefers super-effective, penalises less effective moves
    type_eff_moves = [type_effect(trainer_pokemon, first, types), type_effect(trainer_pokemon, second, types),
                      type_effect(trainer_pokemon, third, types), type_effect(trainer_pokemon, fourth, types)]

    for i in range(4):
        if type_eff_moves[i] > 1.0:
            move_bias[i] -= 2
        elif type_eff_moves[i] < 1.0:
            move_bias[i] += 2

    # print(move_bias)

    # Choosing Option with Lowest Bias Score
    min_score_idx = np.argmin(move_bias)
    move_chosen = ai_move_pool[min_score_idx]
    #print("CPU Move Chosen %s" % move_chosen.name)

    return move_chosen