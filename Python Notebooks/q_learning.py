import numpy as np

class Q_learning:
    
    def __init__(self, policy, env, gamma, alpha, n):
        
        self.policy = policy
        self.gamma = gamma
        self.alpha = alpha
        
        self.row_size = env.row_size
        self.col_size = env.col_size

        self.coord_to_idx_state = env.coord_to_idx_state
        
        self.q_values = np.zeros( (self.row_size*self.col_size, n) )

        self.counter = np.zeros( (self.row_size*self.col_size, n) )
        
    def update_values(self, s, a, r, s_next, a_greedy):

        g = r + self.gamma * self.q_values[s_next, a_greedy]
        g_delta = g - self.q_values[s, a]
        
        self.q_values[s, a] += self.alpha * g_delta

    def display_values(self):
        value_matrix = np.zeros((self.row_size, self.col_size))

        for i in range(self.row_size):
            for j in range(self.col_size):

                state = self.coord_to_idx_state[i, j]
                
                value_matrix[i, j] = max(self.q_values[state])
                
        return value_matrix
