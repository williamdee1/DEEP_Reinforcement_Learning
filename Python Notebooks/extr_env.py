from adv_game import AdvGame
import numpy as np

extr_obs_space = 19
extr_actions_possible = 6
TRAINER_LST = ["Lorelei", "Bruno", "Agatha", "Lance", "Blue_grass", "Blue_fire", "Blue_water"]

class Extr_env:

    def __init__(self, game):
        self.game = game

    def move_turn(self, move, verbose):
        reward, done = self.game.move_turn(move, verbose)
        return self.get_observations(), reward, done

    def get_observations(self):

        trainer_mon = self.game.remaining_trainer_team[0]
        cpu_mon = self.game.remaining_cpu_team[0]

        # Trainer Stat Boost Stages:
        trainer_atk_stage_sc = (5 + trainer_mon.atk_stage) / 10
        trainer_def_stage_sc = (5 + trainer_mon.def_stage) / 10
        trainer_spe_stage_sc = (5 + trainer_mon.spe_stage) / 10

        # HP Percentages of the current trainer and cpu pokemon
        trainer_hp_scaled = round((trainer_mon.current_hp/ trainer_mon.initial_hp)*100)/100
        cpu_hp_scaled = round((cpu_mon.current_hp/ cpu_mon.initial_hp)*100)/100

        cpu_team_scaled = (6 - len(self.game.remaining_cpu_team)) / 6

        # CPU Pokemon Stats (Scaled to respective stat min/maxes taken from pokemon pool):
        #cpu_atk_scaled = (cpu_mon.initial_atk - 62) / (182 - 62)
        #cpu_def_scaled = (cpu_mon.initial_def - 53) / (204 - 53)
        #cpu_spe_scaled = (cpu_mon.initial_spe - 45) / (173 - 45)
        #cpu_spd_scaled = (cpu_mon.initial_spd - 46) / (170 - 46)

        # Categorical Values representing opposing trainer:
        lorelei, bruno, agatha, lance, blue_g, blue_f, blue_w = 0, 0, 0, 0, 0, 0, 0

        trainer_idx = self.game.cpu_team_idx
        if trainer_idx == 0:
            lorelei = 1
        elif trainer_idx == 1:
            bruno = 1
        elif trainer_idx == 2:
            agatha = 1
        elif trainer_idx == 3:
            lance = 1
        elif trainer_idx == 4:
            blue_g = 1
        elif trainer_idx == 5:
            blue_f = 1
        elif trainer_idx == 6:
            blue_w = 1

        # Potions available - maximum = 10
        # potions_avail = self.game.hp_potions_available / 10

        # Categorical values for the switchable pokemon:
        switch1_venu, switch2_venu, switch1_char, switch2_char, switch1_blas, switch2_blas = 0, 0, 0, 0, 0, 0

        try:
            switch1 = self.game.remaining_trainer_team[1].idx
            switch2 = self.game.remaining_trainer_team[2].idx
        except:
            pass

        try:
            if switch1 == 0:
                switch1_venu = 1
            elif switch1 == 1:
                switch1_char = 1
            elif switch1 == 2:
                switch1_blas = 1
            if switch2 == 0:
                switch2_venu = 1
            elif switch2 == 1:
                switch2_char = 1
            elif switch2 == 2:
                switch2_blas = 1
        except:
            pass

        # Returning an scaled array to convert to a tensor later
        obs = np.array([trainer_hp_scaled, cpu_hp_scaled,
                        lorelei, bruno, agatha, lance, blue_g, blue_f, blue_w,
                        trainer_atk_stage_sc, trainer_def_stage_sc, trainer_spe_stage_sc,
                        switch1_venu, switch2_venu, switch1_char, switch2_char, switch1_blas, switch2_blas,
                        cpu_team_scaled])

        return obs

    def reset(self):
        self.game.reset()

        obs = self.get_observations()

        return obs

    def return_ep_metrics(self):
        return self.game.get_metrics()