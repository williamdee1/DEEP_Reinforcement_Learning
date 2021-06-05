from a3c_funcs import *
from a3c_net_2_layer import A3CNet
from a3c_net_1_layer import Net
import torch.multiprocessing as mp
from a3c_adam import SharedAdam
import os
from extr_env import *
from adv_env import *
import threading
import csv
from env_create import *
import matplotlib.pyplot as plt
os.environ["OMP_NUM_THREADS"] = "1"

# Global Values Dictating Static Parameters:
UPDATE_GLOBAL_ITER = 50
GAMMA = 0.9
LEARN_RATE = 0.00001
# Setting a target average reward and max. episodes as early stopping criteria:
MAX_EP = 500000
TARGET_AV_REW = 490

# Choose which environment to load - Extreme or Advanced and the associated action/observation spaces:
ENV_CHOICE = 'Advanced'
# Choose which neural net to load - 1 layer Net (128 hidden max) or 2 layer A3CNet (512 hidden max)
NET_CHOICE = A3CNet

if ENV_CHOICE == 'Extreme':
    GLOBAL_ENV = create_extr_env()
    obs_num = extr_obs_space
    act_num = extr_actions_possible

elif ENV_CHOICE == 'Advanced':
    GLOBAL_ENV = create_adv_env()
    obs_num = adv_obs_space
    act_num = adv_actions_possible


class Worker(mp.Process):
    save_lock = threading.Lock()
    def __init__(self, gnet, opt, global_ep, global_ep_r, g_best_score, res_queue, name):
        super(Worker, self).__init__()
        self.name = 'w%02i' % name
        self.g_ep, self.g_ep_r, self.g_best_score, self.res_queue = global_ep, global_ep_r, g_best_score, res_queue
        self.gnet, self.opt = gnet, opt
        self.lnet = NET_CHOICE(obs_num, act_num)  # local network
        self.env = GLOBAL_ENV
        self.save_dir = "Models"

    def run(self):
        total_step = 1
        while self.g_ep.value < MAX_EP:
            obs = self.env.reset()
            obs_list, act_list, rew_list = [], [], []
            ep_r = 0.
            turn_counter = 0
            while True:
                a = self.lnet.choose_action(conv_np(obs[None, :]))
                move_pool = self.env.game.remaining_trainer_team[0].moves
                action = move_pool[a]
                obs_nxt, r, done = self.env.move_turn(action, False)
                if done:
                    r = -1
                ep_r += r
                obs_list.append(obs)
                act_list.append(a)
                rew_list.append(r)

                # Update global net on done or at specified interval:
                if total_step % UPDATE_GLOBAL_ITER == 0 or done:
                    # Sync with Global Neural Net
                    communicate(self.opt, self.lnet, self.gnet, done, obs_nxt, obs_list, act_list, rew_list, GAMMA)
                    # Resetting lists to zero:
                    obs_list, act_list, rew_list = [], [], []

                    # If done, record results and save model if it's the best score so far:
                    if done:
                        if ENV_CHOICE == 'Extreme':
                            record_extr(self.g_ep, self.g_ep_r, self.g_best_score, ep_r, self.res_queue, self.name, turn_counter,
                                   self.env.game.trainers_beaten, self.env.game.switches_made)
                            #if ep_r >= self.g_best_score.value:
                                #with Worker.save_lock:
                                    #print("Saving best model to {}, "
                                     #     "Episode Score: {}".format(self.save_dir, ep_r))
                                    #torch.save(self.gnet.state_dict(), 'Models/extreme_env_model.pt')
                        elif ENV_CHOICE == 'Advanced':
                            record_adv(self.g_ep, self.g_ep_r, self.g_best_score, ep_r, self.res_queue, self.name,
                                   turn_counter,
                                   self.env.game.hp_potions_used, self.env.game.beaten_E4)
                            #if ep_r >= self.g_best_score.value:
                                #with Worker.save_lock:
                                    #print("Saving best model to {}, "
                                    #      "Episode Score: {}".format(self.save_dir, ep_r))
                                    #torch.save(self.gnet.state_dict(), 'Models/advanced_env_model.pt')

                        break
                obs = obs_nxt
                total_step += 1
                turn_counter += 1

            # Breaking loop if the average global reward is above a set threshold:
            if self.g_ep_r.value >= TARGET_AV_REW:
                break

        self.res_queue.put(None)


if __name__ == "__main__":
    gnet = NET_CHOICE(obs_num, act_num)  # global network
    gnet.share_memory()  # share the global parameters in multiprocessing
    opt = SharedAdam(gnet.parameters(), lr=LEARN_RATE, betas=(0.92, 0.999))  # global optimizer
    global_ep, global_ep_r, g_best_score, res_queue = mp.Value('i', 0), mp.Value('d', 0.), mp.Value('d', 0), mp.Queue()
    save_dir = "Figures"

    # Parallel training - specifying number of workers equal to CPU thread count:
    workers = [Worker(gnet, opt, global_ep, global_ep_r, g_best_score, res_queue, i) for i in range(mp.cpu_count())]

    [w.start() for w in workers]
    res = []  # record episode reward to plot
    while True:
        r = res_queue.get()
        if r is not None:
            res.append(r)
        else:
            break
    [w.join() for w in workers]

    # Writing results to csv:
    #with open('Results/results.csv', 'w') as myfile:
        #wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        #wr.writerow(res)

    plt.plot(res)
    plt.ylabel('Moving Average Episode Reward')
    plt.xlabel('Episodes')
    #plt.savefig(os.path.join(save_dir, 'Moving Average Chart.png'))
    plt.show()
