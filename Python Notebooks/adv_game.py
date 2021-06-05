from trainer import Trainer
from damage import *
from ai import *
import pandas as pd

BEAT_ELITE_R = 0
KNOCK_OUT_R = 0
TURN_LIMIT = 500
HP_POTION_LIMIT = 10

class AdvGame:

    def __init__(self, trainer, cpu, poke_file, trainer_file, moves_file, types_file,
                 cpu_damage_enabled, cpu_all_moves):
        self.poke_dict = pd.read_csv(poke_file).to_dict(orient='list')
        self.trainer_dict = pd.read_csv(trainer_file).to_dict(orient='list')
        self.moves_dict = pd.read_csv(moves_file).to_dict(orient='list')
        self.types = pd.read_csv(types_file)
        self.cpu_damage_enabled = cpu_damage_enabled
        self.cpu_all_moves = cpu_all_moves

        # Generating the trainer's team - Pikachu:
        self.trainer = trainer
        self.trainer_team = Trainer(trainer, self.trainer_dict, self.poke_dict, self.moves_dict).team_list

        # Generating the opposing pokemon team (5 pokemon from the Elite 4):
        self.cpu = cpu
        self.og_cpu_team = Trainer(cpu, self.trainer_dict, self.poke_dict, self.moves_dict).team_list

        # Storing remaining trainer/cpu party members:
        self.remaining_trainer_team = Trainer(trainer, self.trainer_dict, self.poke_dict, self.moves_dict).team_list
        self.remaining_cpu_team = Trainer(cpu, self.trainer_dict, self.poke_dict, self.moves_dict).team_list

        # Keeping track of time:
        self.run_length = 0

        self.hp_potions_available = 3

        # Metrics for Evaluation:
        self.super_eff_moves = 0
        self.turn_max_boost = 0
        self.hp_potions_used = 0
        self.total_reward = 0
        self.outcome = ""
        self.beaten_E4 = 0

    def move_turn(self, move, verbose):
        # List to store episode print outs:
        verbose_list = []

        trainer_mon = self.trainer_team[0]
        cpu_mon = self.remaining_cpu_team[0]

        verbose_list.append("Trainer uses %s" % move.name)

        # Checks if the CPU has all it's moves available, if so chooses according decisions in ai.py:
        if self.cpu_all_moves:
            cpu_move = ai_choose_move(cpu_mon, trainer_mon, self.types)
            verbose_list.append("CPU uses %s" % (cpu_move.name))

        else:
            # The CPU will always choose their current pokemon's first move
            cpu_move = cpu_mon.moves[0]
            verbose_list.append("CPU uses %s" % (cpu_move.name))

        # Receiving positive reward for each move taken:
        reward = 1

        # Establishing metrics:
        super_eff = False
        atk_boost_curr = trainer_mon.atk_stage

        # CALCULATING TRAINER DAMAGE/ HEALING BASED ON MOVE TYPE #
        if move.move_cat != 'Status':

            # Calculate damage dealt to opposing pokemon by the attacking move
            damage_dealt, super_eff = calc_damage(trainer_mon, cpu_mon, move, self.types)
            verbose_list.append("Trainer deals %s damage" % (damage_dealt))

            # Accuracy Calculation - Does the move hit?
            trainer_move_hits = random.random() < (move.move_acc/100)

            # Apply that damage to the cpu pokemon if the move hits
            if trainer_move_hits:
                cpu_mon.take_damage(damage_dealt)
            else:
                verbose_list.append("Trainer move missed due to accuracy")

        else:
            # Apply status move effect:
            sme = status_move_effect(trainer_mon, cpu_mon, move, self.hp_potions_available)

            if sme == 'copy_move':
                copied_move = cpu_move
                verbose_list.append("Trainer Mirrors: %s " % copied_move.name)
                damage_dealt, super_eff = calc_damage(trainer_mon, cpu_mon, copied_move, self.types)
                verbose_list.append("Trainer deals = %s damage" % (damage_dealt))

                # Apply that damage to the cpu pokemon
                cpu_mon.take_damage(damage_dealt)

            elif sme == 'atk+':
                # For the first time attack boost becomes 5, record the turn
                if atk_boost_curr == 4:
                    self.turn_max_boost = self.run_length

            elif sme == 'hp_max':
                self.hp_potions_used += 1
                # Removing potion available to use
                self.hp_potions_available -= 1
                verbose_list.append("Potion Used - %s remaining" % self.hp_potions_available)

        # Updating super effective count metric:
        if super_eff == True:
            self.super_eff_moves += 1
            
        # CALCULATING CPU DAMAGE #
        if self.cpu_damage_enabled:
            cpu_damage_dealt, _ = calc_damage(cpu_mon, trainer_mon, cpu_move, self.types)
            verbose_list.append("CPU deals %s damage" % (cpu_damage_dealt))
            # Apply that damage to the trainer's pokemon only if the CPU pokemon is still alive:
            if cpu_mon.check_fainted() == False:

                # Accuracy Calculation - Does the move hit?
                cpu_move_hits = random.random() < (cpu_move.move_acc / 100)

                # Apply that damage to the cpu pokemon if the move hits
                if cpu_move_hits:
                    trainer_mon.take_damage(cpu_damage_dealt)
                else:
                    verbose_list.append("CPU move missed due to accuracy")

        # Termination Condition:
        done = False

        # Update turn counter:
        self.run_length += 1

        if self.run_length == TURN_LIMIT:
            self.outcome = "limit reached"
            done = True


        # Check whether the CPU pokemon faints (hp < 0):
        verbose_list.append("CPU Mon Current HP = %s " % cpu_mon.current_hp)
        verbose_list.append("Trainer Mon Current HP = %s" % trainer_mon.current_hp)
        if cpu_mon.check_fainted() == True:
            # Remove CPU pokemon from it's trainers list:
            if len(self.remaining_cpu_team) > 1:
                self.remaining_cpu_team.pop(0)
                verbose_list.append("Next Opposing Pokemon is: %s " % self.remaining_cpu_team[0].name)

            else:

                self.outcome = "victory"
                self.remaining_cpu_team = Trainer(self.cpu, self.trainer_dict, self.poke_dict,
                                                  self.moves_dict).team_list
                self.beaten_E4 += 1
                self.hp_potions_available += 3


        # End if trainer's pokemon have all fainted:
        if trainer_mon.check_fainted() == True:
            self.outcome = "defeat"
            done = True
            verbose_list.append("Trainer's Pokemon has blacked out...")

        if done:
            verbose_list.append("~~~~~~~~~~ EPISODE ENDS ~~~~~~~~~~")
        else:
            verbose_list.append("~~~~~~~~~~~ NEXT TURN ~~~~~~~~~~~")

        # If verbose is True, print out what happened during the episode:
        if verbose:
            for item in verbose_list:
                print(item)

        # Add reward for this turn to the total reward
        self.total_reward += reward

        return reward, done

    def reset(self):
        # Resetting metrics
        self.run_length = 0
        self.super_eff_moves = 0
        self.turn_max_boost = 0
        self.hp_potions_used = 0
        self.total_reward = 0
        self.outcome = ""
        self.hp_potions_available = 3
        self.beaten_E4 = 0

        # Resetting players teams:
        self.remaining_cpu_team = Trainer(self.cpu, self.trainer_dict, self.poke_dict, self.moves_dict).team_list
        self.trainer_team = Trainer(self.trainer, self.trainer_dict, self.poke_dict, self.moves_dict).team_list

    def get_metrics(self):
        run_len = self.run_length
        super_eff_moves = self.super_eff_moves
        turn_max_boost_ach = self.turn_max_boost
        hp_potions = self.hp_potions_used
        total_reward = self.total_reward
        outcome = self.outcome

        return run_len, super_eff_moves, turn_max_boost_ach, hp_potions, total_reward, outcome