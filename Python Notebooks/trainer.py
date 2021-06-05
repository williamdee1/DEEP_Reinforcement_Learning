import pandas as pd
from pokemon import Pokemon

class Trainer:

    def __init__(self, name, trainer_dict, poke_dict, moves_dict):
        self.name = name
        self.elite_four = ['Lorelei', 'Bruno', 'Agatha', 'Lance', 'Elite_four']

        self.idx = trainer_dict['Name'].index(self.name)

        # Loading Trainer Pokemon:
        # Return one pokemon only for Ash:
        if self.name == 'Ash':
            self.team_list = [
                Pokemon(
                    trainer_dict['Poke_1'][self.idx],
                    trainer_dict['Level_1'][self.idx],
                    poke_dict, moves_dict),
                ]

        elif self.name == 'Ash_starters':
            self.team_list = [
                Pokemon(
                    trainer_dict['Poke_1'][self.idx],
                    trainer_dict['Level_1'][self.idx],
                    poke_dict, moves_dict),
                Pokemon(
                    trainer_dict['Poke_2'][self.idx],
                    trainer_dict['Level_2'][self.idx],
                    poke_dict, moves_dict),
                Pokemon(
                    trainer_dict['Poke_3'][self.idx],
                    trainer_dict['Level_3'][self.idx],
                    poke_dict, moves_dict)
                ]

        else:
            self.team_list = [
                Pokemon(
                    trainer_dict['Poke_1'][self.idx],
                    trainer_dict['Level_1'][self.idx],
                    poke_dict, moves_dict),
                Pokemon(
                    trainer_dict['Poke_2'][self.idx],
                    trainer_dict['Level_2'][self.idx],
                    poke_dict, moves_dict),
                Pokemon(
                    trainer_dict['Poke_3'][self.idx],
                    trainer_dict['Level_3'][self.idx],
                    poke_dict, moves_dict),
                Pokemon(
                    trainer_dict['Poke_4'][self.idx],
                    trainer_dict['Level_4'][self.idx],
                    poke_dict, moves_dict),
                Pokemon(
                    trainer_dict['Poke_5'][self.idx],
                    trainer_dict['Level_5'][self.idx],
                    poke_dict, moves_dict),
                ]

        # The Elite Four only have 5 Pokemon, trainer has 6:
        if self.name != 'Ash' and self.name != 'Ash_starters' and self.name not in self.elite_four:
            self.team_list.append(
                Pokemon(
                    trainer_dict['Poke_6'][self.idx],
                    trainer_dict['Level_6'][self.idx],
                    poke_dict, moves_dict),
            )