import torch
import torch.nn as nn
import torch.nn.functional as F
from a3c_funcs import *


class Net(nn.Module):
    def __init__(self, obs, actions):
        super(Net, self).__init__()
        self.obs = obs
        self.actions = actions
        self.pi1 = nn.Linear(obs, 128)
        self.pi2 = nn.Linear(128, actions)
        self.v1 = nn.Linear(obs, 128)
        self.v2 = nn.Linear(128, 1)
        set_init([self.pi1, self.pi2, self.v1, self.v2])
        self.distribution = torch.distributions.Categorical

    def forward(self, x):
        pi1 = torch.tanh(self.pi1(x))
        policy = self.pi2(pi1)
        v1 = torch.tanh(self.v1(x))
        values = self.v2(v1)
        return policy, values

    def choose_action(self, s):
        self.eval()
        policy, _ = self.forward(s)
        prob = F.softmax(policy, dim=1).data
        cat_prob = self.distribution(prob)
        return cat_prob.sample().numpy()[0]

    def loss_func(self, obs, a, v_t):
        self.train()
        policy, values = self.forward(obs)
        advantage = v_t - values
        critic_loss = advantage.pow(2)

        probs = F.softmax(policy, dim=1)
        cat_probs = self.distribution(probs)
        exp_v = cat_probs.log_prob(a) * advantage.detach().squeeze()
        actor_loss = -exp_v
        total_loss = (critic_loss + actor_loss).mean()
        return total_loss