import torch
import torch.nn as nn
import torch.nn.functional as F
from a3c_funcs import *

class A3CNet(nn.Module):
    def __init__(self, obs, actions):
        super(A3CNet, self).__init__()
        self.obs = obs
        self.acts = actions
        self.pi1 = nn.Linear(obs, 512)
        self.pi2 = nn.Linear(512, 256)
        self.p_out = nn.Linear(256, actions)
        self.v1 = nn.Linear(obs, 512)
        self.v2 = nn.Linear(512, 256)
        self.v_out = nn.Linear(256, 1)
        set_init([self.pi1, self.pi2, self.v1, self.v2])
        self.distribution = torch.distributions.Categorical

    def forward(self, x):
        pi1 = torch.tanh(self.pi1(x))
        pi2 = torch.tanh(self.pi2(pi1))
        policy = self.p_out(pi2)
        v1 = torch.tanh(self.v1(x))
        v2 = torch.tanh(self.v2(v1))
        values = self.v_out(v2)
        return policy, values

    def choose_action(self, obs):
        self.eval()
        policy, _ = self.forward(obs)
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
