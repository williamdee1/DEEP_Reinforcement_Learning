import pandas as pd
from math import floor
from moves import Move


class Pokemon:

    def __init__(self, name, level, poke_dict, moves_dict):
        self.name = name
        self.level = level

        self.idx = poke_dict['Name'].index(self.name)

        # Base Stats
        self.base_hp = poke_dict['HP'][self.idx]
        self.base_atk = poke_dict['Attack'][self.idx]
        self.base_def = poke_dict['Defense'][self.idx]
        self.base_spe = poke_dict['Special'][self.idx]
        self.base_spd = poke_dict['Speed'][self.idx]
        ivs = [8, 9, 8, 8, 8]

        # Stats After Levelling Accounted for:
        self.initial_hp = floor(((((self.base_hp + ivs[0]) * 2) * level) / 100) + level + 10)
        self.initial_atk = floor(((((self.base_atk + ivs[1]) * 2) * level) / 100) + 5)
        self.initial_def = floor(((((self.base_def + ivs[2]) * 2) * level) / 100) + 5)
        self.initial_spe = floor(((((self.base_spe + ivs[3]) * 2) * level) / 100) + 5)
        self.initial_spd = floor(((((self.base_spd + ivs[4]) * 2) * level) / 100) + 5)

        # Current stats, will be modified in main game loop:
        self.current_hp = self.initial_hp
        self.current_atk = self.initial_atk
        self.current_def = self.initial_def
        self.current_spe = self.initial_spe
        self.current_spd = self.initial_spd

        # Typing
        self.type_1 = poke_dict['Type_1'][self.idx]
        self.type_2 = poke_dict['Type_2'][self.idx]

        # Moveset
        self.moves = [
            Move(poke_dict['Move_1'][self.idx], moves_dict),
            Move(poke_dict['Move_2'][self.idx], moves_dict),
            Move(poke_dict['Move_3'][self.idx], moves_dict),
            Move(poke_dict['Move_4'][self.idx], moves_dict),
        ]

        # Move_5 does not exist in the basic environment so it should be skipped
        try:
            move_5 = Move(poke_dict['Move_5'][self.idx], moves_dict)
            self.moves.append(move_5)
        except KeyError:
            pass

        # 6 Moves only exist in Extr environment
        try:
            move_6 = Move(poke_dict['Move_6'][self.idx], moves_dict)
            self.moves.append(move_6)
        except KeyError:
            pass

        # Stage Stat Modifiers, init at zero
        self.atk_stage = 0
        self.def_stage = 0
        self.spe_stage = 0
        self.spd_stage = 0

        # Status Modifier, init at False
        self.poison = False
        self.paralyze = False
        self.sleep = False
        self.confuse = False
        self.burn = False

        # General check 're overall status, informs decision-making
        self.status = False

        # Counter tacking how long pokemon has had status:
        self.poison_counter = 0
        self.paralyze_counter = 0
        self.sleep_counter = 0
        self.confuse_counter = 0
        self.burn_counter = 0


    def check_fainted(self):
        if self.current_hp > 0:
            return False
        else:
            return True

    def take_damage(self, damage):
        self.current_hp -= damage

        # Ensure HP doesn't fall below 0:
        if self.current_hp < 0:
            self.current_hp = 0

    def apply_status(self, status):
        if status == 'poison':
            self.poison = True
        if status == 'paralyze':
            self.paralyze = True
        if status == 'sleep':
            self.sleep = True
        if status == 'confuse':
            self.confuse = True
        if status == 'burn':
            self.burn = True

        self.status = True

    def remove_status(self, status):
        self.status = False

    def alter_stat_stage(self, stat, change):
        if stat == 'atk':
            self.atk_stage += change
        if stat == 'def':
            self.def_stage += change
        if stat == 'spe':
            self.spe_stage += change
        if stat == 'spd':
            self.spd_stage += change

    def reset_stats(self):
        # Reset Stage Stat Modifiers to zero
        self.atk_stage = 0
        self.def_stage = 0
        self.spe_stage = 0
        self.spd_stage = 0