from trainer import Trainer
from damage import *
from ai import *
import pandas as pd
import random

BEAT_ELITE_R = 0
KNOCK_OUT_R = 0
TURN_LIMIT = 500
TRAINER_LST = ["Lorelei", "Bruno", "Agatha", "Lance", "Blue_grass", "Blue_fire", "Blue_water"]
TRAINER_LIMIT = 20


class ExtrGame:

    def __init__(self, trainer, poke_file, trainer_file, moves_file, types_file,
                 cpu_damage_enabled, cpu_all_moves):
        self.poke_dict = pd.read_csv(poke_file).to_dict(orient='list')
        self.trainer_dict = pd.read_csv(trainer_file).to_dict(orient='list')
        self.moves_dict = pd.read_csv(moves_file).to_dict(orient='list')
        self.types = pd.read_csv(types_file)
        self.cpu_damage_enabled = cpu_damage_enabled
        self.cpu_all_moves = cpu_all_moves

        # Generating the trainer's team - Blastoise, Charizard and Venusaur:
        self.trainer = trainer
        self.trainer_team = Trainer(trainer, self.trainer_dict, self.poke_dict, self.moves_dict).team_list

        # Generating a random opposing pokemon team from Trainer List above:
        self.cpu_team_idx = random.randint(0, 6)
        cpu = TRAINER_LST[self.cpu_team_idx]
        self.og_cpu_team = Trainer(cpu, self.trainer_dict, self.poke_dict, self.moves_dict).team_list

        # Storing remaining trainer/cpu party members:
        self.remaining_trainer_team = Trainer(trainer, self.trainer_dict, self.poke_dict, self.moves_dict).team_list
        self.remaining_cpu_team = Trainer(cpu, self.trainer_dict, self.poke_dict, self.moves_dict).team_list

        # Keeping track of time:
        self.run_length = 0

        self.hp_potions_available = 3

        # Metrics for Evaluation:
        self.super_eff_moves = 0
        self.se_taken = 0
        self.turn_max_boost = 0
        self.hp_potions_used = 0
        self.total_reward = 0
        self.outcome = ""
        self.trainers_beaten = 0
        self.switches_made = 0
        self.trainer_timer = 0

    def move_turn(self, move, verbose):
        # List to store episode print outs:
        verbose_list = []

        trainer_mon = self.remaining_trainer_team[0]
        cpu_mon = self.remaining_cpu_team[0]

        verbose_list.append("Trainer's %s chooses %s" % (trainer_mon.name, move.name))

        # Checks if the CPU has all it's moves available, if so chooses according decisions in ai.py:
        if self.cpu_all_moves:
            cpu_move = ai_choose_move(cpu_mon, trainer_mon, self.types)
            verbose_list.append("CPU's %s chooses %s" % (cpu_mon.name, cpu_move.name))

        else:
            # The CPU will always choose their current pokemon's first move
            cpu_move = cpu_mon.moves[0]
            verbose_list.append("CPU's %s chooses %s" % (cpu_mon.name, cpu_move.name))

        # Receiving positive reward for each move taken:
        reward = 1

        # Establishing metrics:
        super_eff = False

        # CALCULATING TRAINER DAMAGE/ HEALING BASED ON MOVE TYPE #
        if move.move_cat != 'Status':

            # Calculate damage dealt to opposing pokemon by the attacking move
            damage_dealt, super_eff = calc_damage(trainer_mon, cpu_mon, move, self.types)

            # Accuracy Calculation - Does the move hit?
            trainer_move_hits = random.random() < (move.move_acc/100)

            # Apply that damage to the cpu pokemon if the move hits
            if trainer_move_hits:
                # Increasing the effect of a super effective move:
                if super_eff:
                    cpu_mon.take_damage(damage_dealt*8)
                    verbose_list.append("Trainer's %s deals %s super effective damage" % (trainer_mon.name, damage_dealt))
                else:
                    cpu_mon.take_damage(damage_dealt)
                    verbose_list.append("Trainer's %s deals %s damage" % (trainer_mon.name, damage_dealt))
            else:
                verbose_list.append("%s's move missed due to accuracy" % trainer_mon.name)

        else:
            # Apply status move effect:
            sme = status_move_effect(trainer_mon, cpu_mon, move, self.hp_potions_available)

            if sme == 'copy_move':
                copied_move = cpu_move
                verbose_list.append("Trainer Mirrors: %s " % copied_move.name)
                damage_dealt, super_eff = calc_damage(trainer_mon, cpu_mon, copied_move, self.types)
                verbose_list.append("Trainer's %s deals = %s damage" % (trainer_mon.name, damage_dealt))

                # Apply that damage to the cpu pokemon
                cpu_mon.take_damage(damage_dealt)

            elif sme == 'atk+':
                # For the first time attack boost becomes 5, record the turn
                if trainer_mon.atk_stage == 5:
                    self.turn_max_boost = self.run_length

            elif sme == 'hp_max':
                self.hp_potions_used += 1
                # Removing potion available to use
                self.hp_potions_available -= 1
                verbose_list.append("Potion Used - %s remaining" % self.hp_potions_available)

            elif sme == 'switch1':
                # Trainer switches to the next pokemon in the list if there is one:
                if len(self.remaining_trainer_team) > 1:
                    # First resetting pokemon's stats to zero:
                    trainer_mon.reset_stats()
                    # Removing first pokemon and switching to next pokemon in list
                    switched_mon = self.remaining_trainer_team.pop(0)
                    trainer_mon = self.remaining_trainer_team[0]
                    # Adding mon to back of trainer's team
                    self.remaining_trainer_team.append(switched_mon)
                    verbose_list.append("Trainer Switched out %s for %s" % (switched_mon.name,
                                                                            self.remaining_trainer_team[0].name))
                    self.switches_made += 1
                else:
                    verbose_list.append("Trainer attempted to switch, but had no other Pokemon!")

            elif sme == 'switch2':
                # Trainer switches to the second next pokemon in the list if there is one:
                if len(self.remaining_trainer_team) > 2:
                    # First resetting pokemon's stats to zero:
                    trainer_mon.reset_stats()
                    # Removing first and second Pokemon and switching to next pokemon in list
                    first_mon = self.remaining_trainer_team.pop(0)
                    second_mon = self.remaining_trainer_team.pop(0)
                    trainer_mon = self.remaining_trainer_team[0]
                    # Adding mon to back of trainer's team
                    self.remaining_trainer_team.extend([first_mon, second_mon])
                    verbose_list.append("Trainer Switched out %s for %s" % (first_mon.name,
                                                                            self.remaining_trainer_team[0].name))
                    self.switches_made += 1
                else:
                    verbose_list.append("Trainer attempted to switch, but they couldn't!")

        # Printing HP of CPU Pokemon after Trainer's attack:
        verbose_list.append("CPU's %s has %s HP left." % (cpu_mon.name, cpu_mon.current_hp))

        # Updating super effective count metric:
        if super_eff == True:
            self.super_eff_moves += 1
            
        # CALCULATING CPU DAMAGE #
        if cpu_move.move_cat != 'Status':
            if self.cpu_damage_enabled:
                cpu_damage_dealt, cpu_se = calc_damage(cpu_mon, trainer_mon, cpu_move, self.types)
                # Apply that damage to the trainer's pokemon only if the CPU pokemon is still alive:
                if cpu_mon.check_fainted() == False:

                    # Accuracy Calculation - Does the move hit?
                    cpu_move_hits = random.random() < (cpu_move.move_acc / 100)

                    # Apply that damage to the cpu pokemon if the move hits
                    if cpu_move_hits:
                        if cpu_se:
                            trainer_mon.take_damage(cpu_damage_dealt * 4)
                            verbose_list.append(
                                "CPU's %s deals %s super effective damage" % (cpu_mon.name, cpu_damage_dealt))
                            self.se_taken += 1
                        else:
                            trainer_mon.take_damage(cpu_damage_dealt)
                            verbose_list.append("CPU's %s deals %s damage" % (cpu_mon.name, cpu_damage_dealt))
                    else:
                        verbose_list.append("%s's move missed due to accuracy" % cpu_mon.name)

        else:
            # Apply status move effect (always has zero potions available):
            status_move_effect(cpu_mon, trainer_mon, cpu_move, 0)
            verbose_list.append("CPU's %s used a status move." % cpu_mon.name)

        # Printing HP of Trainer Pokemon after CPU's attack:
        verbose_list.append("Trainer's %s has %s HP left." % (trainer_mon.name, trainer_mon.current_hp))

        # Termination Condition:
        done = False

        # Update turn counter:
        self.run_length += 1
        self.trainer_timer += 1

        if self.run_length == TURN_LIMIT:
            self.outcome = "limit reached"
            done = True


        # Check whether the CPU pokemon faints (hp < 0):
        if cpu_mon.check_fainted() == True:
            # Remove CPU pokemon from it's trainers list:
            if len(self.remaining_cpu_team) > 1:
                self.remaining_cpu_team.pop(0)
                verbose_list.append("Next Opposing Pokemon is: %s " % self.remaining_cpu_team[0].name)
                #if self.hp_potions_available < 10:
                    #self.hp_potions_available += 1
            # Generate new random team:
            else:
                self.cpu_team_idx = random.randint(0, 6)
                cpu = TRAINER_LST[self.cpu_team_idx]
                self.remaining_cpu_team = Trainer(cpu, self.trainer_dict, self.poke_dict,
                                                  self.moves_dict).team_list
                self.trainers_beaten += 1
                #if self.hp_potions_available < 10:
                    #self.hp_potions_available += 3
                # Resetting trainer timer
                self.trainer_timer = 0
                # Restore Trainer's team to full health for next battle:
                self.remaining_trainer_team = Trainer(self.trainer, self.trainer_dict, self.poke_dict,
                                                      self.moves_dict).team_list
                verbose_list.append("Trainer beaten, next Trainer is: %s " % cpu)

        if self.trainer_timer == TRAINER_LIMIT:
            done = True
            verbose_list.append("Failed to beat opponent in time")

        # End if trainer's pokemon have all fainted:
        if trainer_mon.check_fainted() == True:
            if len(self.remaining_trainer_team) > 1:
                self.remaining_trainer_team.pop(0)
                verbose_list.append("%s fainted... " % trainer_mon.name)
                verbose_list.append("Next Trainer Pokemon is: %s " % self.remaining_trainer_team[0].name)
            else:
                self.outcome = "defeat"
                done = True
                verbose_list.append("All trainer's Pokemon have blacked out...")

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
        self.se_taken = 0
        self.turn_max_boost = 0
        self.hp_potions_used = 0
        self.total_reward = 0
        self.outcome = ""
        self.hp_potions_available = 3
        self.trainers_beaten = 0
        self.switches_made = 0
        self.trainer_timer = 0

        # Resetting players teams:
        self.cpu_team_idx = random.randint(0, 6)
        cpu = TRAINER_LST[self.cpu_team_idx]
        self.remaining_cpu_team = Trainer(cpu, self.trainer_dict, self.poke_dict, self.moves_dict).team_list
        self.remaining_trainer_team = Trainer(self.trainer, self.trainer_dict, self.poke_dict, self.moves_dict).team_list

    def get_metrics(self):
        #run_len = self.run_length
        super_eff_moves = self.super_eff_moves
        trainers_beaten = self.trainers_beaten
        #hp_potions = self.hp_potions_used
        total_reward = self.total_reward
        outcome = self.outcome
        switches_made = self.switches_made
        se_taken = self.se_taken

        return total_reward, super_eff_moves, se_taken, trainers_beaten, switches_made, outcome