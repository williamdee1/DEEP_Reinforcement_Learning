from extr_env import *
from extr_game import ExtrGame
from adv_env import *
from adv_game import AdvGame


def create_extr_env():
    types_file = 'type_advs.csv'
    moves_file = 'ExtrEnvData/selected_moves.csv'
    poke_file = 'ExtrEnvData/selected_poke_data.csv'
    trainer_file = 'ExtrEnvData/selected_trainers.csv'
    cpu_damage_enabled = True
    cpu_all_moves = True
    game = ExtrGame("Ash_starters", poke_file, trainer_file,
                moves_file, types_file, cpu_damage_enabled, cpu_all_moves)

    return Extr_env(game)

def create_adv_env():
    types_file = 'type_advs.csv'
    moves_file = 'AdvEnvData/selected_moves.csv'
    poke_file = 'AdvEnvData/selected_poke_data.csv'
    trainer_file = 'AdvEnvData/selected_trainers.csv'
    cpu_damage_enabled = True
    cpu_all_moves = False
    game = AdvGame("Ash", "Elite_four", poke_file, trainer_file,
                moves_file, types_file, cpu_damage_enabled, cpu_all_moves)

    return Adv_env(game)