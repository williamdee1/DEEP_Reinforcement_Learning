import neat
import pickle
#import visualize
from extr_env import *
from env_create import create_extr_env, create_adv_env

# GLOBAL STATIC VARIABLES
GEN = 0
# Creating either extreme or advanced environment and associated configs using imported functions
# N.B Line 46 must be changed manually
ENV_CHOICE = 'Extreme'

if ENV_CHOICE == 'Extreme':
    GLOBAL_ENV = create_extr_env()
    CONFIG_ENV = 'neat_config_extr.txt'

elif ENV_CHOICE == 'Advanced':
    GLOBAL_ENV = create_adv_env()
    CONFIG_ENV = 'neat_config_adv.txt'

# Controls how many generations to run if stopping criteria in config file not met
GEN_LIMIT = 200

def evaluation(genomes, config):
    global GEN
    GEN += 1 # keeps track of the generation number

    nets = [] # need to keep track of the neural networks that control each trainer
    ge = [] # to keep track of genomes
    trainers = []
    environs = []
    observations = []
    obs = GLOBAL_ENV.reset()

    # genome is a tuple which has the genome ID as well as the genome object
    for _, g in genomes:
        # Source: https://neat-python.readthedocs.io/en/latest/_modules/nn/feed_forward.html
        # Create "receives a genome and returns its phenotype." ( a neural network )
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        # UNSURE IF NEEDED!!
        trainers.append('Ash')
        # Initialize the starting genome fitness
        g.fitness = 0
        ge.append(g)
        # Creating separate environments for each trainer:
        environs.append(create_extr_env())
        # Appending starting observations and 0 scores for all:
        observations.append(obs)

    best_gen_score = 0
    run = True

    while run:

        for i, trainer in enumerate(trainers):
            ob = observations[i]
            a_probs = nets[i].activate(ob)
            a_idx = np.argmax(a_probs)
            move_pool = environs[i].game.remaining_trainer_team[0].moves
            action = move_pool[a_idx]
            ob_nxt, r, done = environs[i].move_turn(action, False)

            # Trainer receives a small amount of "fitness" equal to the reward received
            ge[i].fitness += r

            # Updating Best Score
            if ge[i].fitness > best_gen_score:
                best_gen_score = ge[i].fitness

            # If done, remove the trainer/ associated genome/net/obs from the list
            if done:
                trainers.pop(i)
                nets.pop(i)
                ge.pop(i)
                environs.pop(i)
                observations.pop(i)

            else:
                observations[i] = ob_nxt

            if len(trainers) == 0:
                # If there are no more trainers left, end the run:
                run = False

            # Saving net if score is above and threshold and best so far:

    print("Best Generation %s Score is %s" % (GEN-1, best_gen_score))


def main():
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        CONFIG_ENV)

    # Using NEAT package tools to store information:
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Returning/ saving the best trainer from the generations (set by n)
    winner = p.run(evaluation, n=GEN_LIMIT)
    #pickle.dump(winner, open('Models/extr_test.pkl', 'wb'))

    # Using NEAT functions to print out information:
    #visualize.plot_stats(stats)
    #visualize.plot_species(stats)
    #visualize.draw_net(config, winner, view=False, filename="Figures/NEAT_neural_net.png")

if __name__ == "__main__":
    main()