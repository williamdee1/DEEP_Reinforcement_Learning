import pandas as pd


class Move:

    def __init__(self, name, moves_dict):
        self.name = name

        self.idx = moves_dict['Name'].index(self.name)

        # Getting move characteristics
        self.move_type = moves_dict['Type'][self.idx]
        self.move_cat = moves_dict['Cat'][self.idx]
        self.move_power = moves_dict['Power'][self.idx]
        self.move_acc = moves_dict['Accuracy'][self.idx]
        self.move_pp = moves_dict['PP'][self.idx]
        self.move_effect = moves_dict['Kind'][self.idx]

