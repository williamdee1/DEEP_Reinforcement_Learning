from adv_game import AdvGame
import numpy as np

adv_obs_space = 4
adv_actions_possible = 5

class Adv_env:

    def __init__(self, game):
        self.game = game

    def move_turn(self, move, verbose):
        reward, done = self.game.move_turn(move, verbose)
        return self.get_observations(), reward, done

    def get_observations(self):

        trainer_mon = self.game.trainer_team[0]

        cpu_mon = self.game.remaining_cpu_team[0]

        # Trainer Attack Boost Stage
        trainer_atk_stage_sc = trainer_mon.atk_stage/6

        # HP Percentages of the current trainer and cpu pokemon
        trainer_hp_scaled = round((trainer_mon.current_hp/ trainer_mon.initial_hp)*100)/100
        cpu_hp_scaled = round((cpu_mon.current_hp/ cpu_mon.initial_hp)*100)/100

        cpu_team_scaled = (6 - len(self.game.remaining_cpu_team)) / 6

        # Returning an scaled array to convert to a tensor later
        obs = np.array([trainer_hp_scaled, cpu_hp_scaled,
                        cpu_team_scaled, trainer_atk_stage_sc])

        return obs

    def reset(self):
        self.game.reset()

        obs = self.get_observations()

        return obs

    def return_ep_metrics(self):
        return self.game.get_metrics()