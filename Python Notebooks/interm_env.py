from game import Game
import numpy as np

health_buckets_trainer = 11
health_buckets_cpu = 11
trainer_stat_boost_levels = 6

class Interm_env:

    def __init__(self, game):
        self.game = game

        # Env rows equal to stat boosts pikachu can receive * amount of pokemon remaining on cpu team (5 to 0)
        self.row_size = (trainer_stat_boost_levels * len(self.game.og_cpu_team))
        # Columns equal to the health bucket possibilities of both the trainer and the cpu's pokemon:
        self.col_size = health_buckets_trainer * health_buckets_cpu

        # Allocating Indexes and State Numbers:
        self.coord_to_idx_state = np.arange(0, self.row_size * self.col_size).reshape(self.row_size, self.col_size)
        
        # Starting position will always be the top left of the env, where cpu has all 5 mons at full health and
        # Pikachu has no stat boosts
        self.position_trainer = [0, 0]


    def move_turn(self, move, verbose):
        reward, done = self.game.move_turn(move, verbose)
        return self.calculate_position(), reward, done

    def calculate_position(self):

        trainer_mon = self.game.trainer_team[0]

        # Return current attack stat boost of trainer pokemon (for row state idx):
        atk_boost = trainer_mon.atk_stage

        # Fainted CPU_mons (also for row state idx):
        lost_cpu_mons = len(self.game.og_cpu_team) - len(self.game.remaining_cpu_team)


        if len(self.game.remaining_cpu_team) > 0:
            cpu_mon = self.game.remaining_cpu_team[0]
            
            # Return the current health range of the cpu pokemon and trainer(to calc column state idx):
            cpu_health_range = cpu_mon.current_hp / cpu_mon.initial_hp
            cpu_mat_pos_HR = int(np.ceil(cpu_health_range * 10))

            trainer_health_range = trainer_mon.current_hp / trainer_mon.initial_hp
            trainer_mat_pos_HR = int(np.ceil(trainer_health_range * 10))

            # Calculate next position of the trainer:
            self.position_trainer = [atk_boost + (lost_cpu_mons * trainer_stat_boost_levels),
                                 (health_buckets_trainer - trainer_mat_pos_HR - 1) +
                                 ((health_buckets_cpu - cpu_mat_pos_HR -1) * health_buckets_cpu)]
        else:
            self.position_trainer = [
                atk_boost + (lost_cpu_mons * trainer_stat_boost_levels),
                0]

        # Setting state to return
        state = self.coord_to_idx_state[self.position_trainer[0], self.position_trainer[1]]

        return state

    def reset(self):
        self.game.reset()

        # Resetting trainer's position
        self.position_trainer = [0, 0]

        state = self.coord_to_idx_state[self.position_trainer[0], self.position_trainer[1]]

        return state

    def return_ep_metrics(self):
        return self.game.get_metrics()
