from torch import nn
import torch
import numpy as np


def conv_np(np_array, dtype=np.float32):
    if np_array.dtype != dtype:
        np_array = np_array.astype(dtype)
    return torch.from_numpy(np_array)

def communicate(opt, lnet, gnet, done, obs_nxt, obs_list, act_list, rew_list, gamma):
    if done:
        v_obs = 0.               # terminal
    else:
        v_obs = lnet.forward(conv_np(obs_nxt[None, :]))[-1].data.numpy()[0, 0]

    disc_value_list = []
    for r in rew_list[::-1]:    # reverse buffer r
        v_obs = r + gamma * v_obs
        disc_value_list.append(v_obs)
    disc_value_list.reverse()

    loss = lnet.loss_func(
        conv_np(np.vstack(obs_list)),
        conv_np(np.array(act_list), dtype=np.int64) if act_list[0].dtype == np.int64 else conv_np(np.vstack(act_list)),
        conv_np(np.array(disc_value_list)[:, None]))

    # calculate local gradients and push local parameters to global
    opt.zero_grad()
    loss.backward()
    for lp, gp in zip(lnet.parameters(), gnet.parameters()):
        gp._grad = lp.grad
    opt.step()

    # pull global parameters
    lnet.load_state_dict(gnet.state_dict())


def record_extr(global_ep, global_ep_r, g_best_score, ep_r, res_queue, name,
           turn_counter, trainers_beaten, switches_made):
    with global_ep.get_lock():
        global_ep.value += 1
    with global_ep_r.get_lock():
        if global_ep_r.value == 0.:
            global_ep_r.value = ep_r
        else:
            global_ep_r.value = global_ep_r.value * 0.999 + ep_r * 0.001
    res_queue.put(global_ep_r.value)
    with g_best_score.get_lock():
        if ep_r > g_best_score.value:
            g_best_score.value = ep_r
    print(
        name,
        "Ep:", global_ep.value,
        "| Ep_r: %.0f" % global_ep_r.value,
        "| Turns Taken: %s" % turn_counter,
        "| Trainers Beaten: %s times" % trainers_beaten,
        "| Switches Made: %s" % switches_made,
        "| Best Score So Far: %s" % g_best_score.value
    )

def record_adv(global_ep, global_ep_r, g_best_score, ep_r, res_queue, name, turn_counter, hp_potions, e4_beaten):
    with global_ep.get_lock():
        global_ep.value += 1
    with global_ep_r.get_lock():
        if global_ep_r.value == 0.:
            global_ep_r.value = ep_r
        else:
            global_ep_r.value = global_ep_r.value * 0.999 + ep_r * 0.001
    res_queue.put(global_ep_r.value)
    with g_best_score.get_lock():
        if ep_r > g_best_score.value:
            g_best_score.value = ep_r
    print(
        name,
        "Ep:", global_ep.value,
        "| Ep_r: %.0f" % global_ep_r.value,
        "| Turns Taken: %s" % turn_counter,
        "| Potions Used: %s" % hp_potions,
        "| Elite 4 Beaten: %s times" % e4_beaten,
        "| Best Score So Far: %s" % g_best_score.value
    )


def set_init(layers):
    for layer in layers:
        nn.init.normal_(layer.weight, mean=0., std=0.1)
        nn.init.constant_(layer.bias, 0.)