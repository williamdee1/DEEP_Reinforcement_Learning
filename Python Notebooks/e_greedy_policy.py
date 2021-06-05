import numpy as np
import random

class E_Greedy_Policy():
    
    def __init__(self, epsilon, decay, env):
        
        self.epsilon = epsilon
        self.epsilon_start = epsilon
        self.decay = decay
        self.env = env
                
    def __call__(self, state, q_values, possible_moves):
        is_greedy = random.random() > self.epsilon
        
        if is_greedy :
            # we select greedy action
            index_action = np.argmax(q_values[state])
            return possible_moves[index_action]
        
        else:
            # we sample a random action
            return random.choice(possible_moves)
        
    def update_epsilon(self):
        
        self.epsilon = self.epsilon*self.decay
        
    def reset(self):
        self.epsilon = self.epsilon_start
