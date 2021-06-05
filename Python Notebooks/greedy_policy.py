import numpy as np

class Greedy_Policy():
   
    def __init__(self, epsilon, env):
        
        self.epsilon = epsilon
        self.env = env
    
    def __call__(self, state, q_values, possible_moves):
        index_action = np.argmax(q_values[state])

        return possible_moves[index_action]
