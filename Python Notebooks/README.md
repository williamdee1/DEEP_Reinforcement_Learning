##### ReadMe File #####

Packages Required:
- neat-python
- torch
- statistics
- matplotlib
- seaborn
- numpy
- pandas
- scikit-learn
- random
- os


~~~Explanation of Folders Included:
Data Folders - i.e. "AdvEnvData":
	- These include the pokemon level, moves and stats data used in each environment.
	- Each environment is different and has slightly different data.
Models:
	- Stored best models for A3C and NEAT for advanced and extreme environments.
Results:
	- Hyperparameter tuning results text files used to create charts in coursework.

~~~Explanation of Files Included:
a3c_adam:
	- The shared activation function of the A3C networks.
a3c_funcs:
	- Utility functions used by the A3C algorithm.
a3c_main:
	- The main and worker functions used to train A3C.
a3c_net_1/2_layer:
	- 1 and 2 layer neural network classes used for A3C.
adv/basic/extr/interm env:
	- The different environments used, each returns either obsevations or states.
adv/basic/extr/interm game:
	- The coded game files that run the main loop of each game.
ai:
	- When the CPU selects it's own moves in the extreme env, it uses this function to do so.
damage:
	- Calculates how the damage is applied in the game functions.
e_greedy/greedy_policy:
	- Both policies used in the Q-Learning tasks.
env_create:
	- Functions to create the advanced and extreme environments, used by a3c_main and neat_main
moves:
	- Function to assign moves, effects, accuracy to selected actions.
neat_config_adv/extr:
	- The config files for NEAT dictating the hyperparameters to be used.
neat_main:
	- The main function to run and train the NEAT algorithmn.
pokemon:
	- Function to generate Pokemon based on names and level specified.
q_learning:
	- Q-Learning algorithmn main function.
trainer:
	- Function to create trainers with specified types and number of Pokemon.
type_advs.csv:
	- A file based on the Pokemon game, determes the multiplier for super and less effective moves.
visualize:
	- A module needed to print out graphviz graphics for NEAT.

