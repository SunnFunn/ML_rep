from app import batch_size
import numpy as np
import random
import torch

#Модель DDPG поиска оптимальной политики действия
class DDPG():
    def __init__(self,
                 policy_model,
                 policy_max_grad_norm,
                 policy_optimizer_fn,
                 policy_optimizer_lr,
                 policy_optim_scheduler,
                 value_model,
                 value_max_grad_norm,
                 value_optimizer_fn,
                 value_optimizer_lr,
                 value_optim_scheduler,
                 update_target_every_steps,
                 tau,
                 df):

        self.policy_model = policy_model
        self.policy_max_grad_norm = policy_max_grad_norm
        self.policy_optimizer_fn = policy_optimizer_fn
        self.policy_optimizer_lr = policy_optimizer_lr
        self.policy_optim_scheduler = policy_optim_scheduler

        self.value_model = value_model
        self.value_max_grad_norm = value_max_grad_norm
        self.value_optimizer_fn = value_optimizer_fn
        self.value_optimizer_lr = value_optimizer_lr
        self.value_optim_scheduler = value_optim_scheduler

        self.update_target_every_steps = update_target_every_steps
        self.tau = tau

        self.df = df

    def optimize_model(self, experiences):
        states, actions, rewards, next_states = experiences

        argmax_a_q_sp = self.target_policy_model(next_states)
        max_a_q_sp = self.target_value_model(next_states, argmax_a_q_sp)
        target_q_sa = rewards + self.gamma * max_a_q_sp
        q_sa = self.online_value_model(states, actions)
        td_error = q_sa - target_q_sa.detach()
        value_loss = td_error.pow(2).mul(0.5).mean()
        self.value_optimizer.zero_grad()
        value_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.online_value_model.parameters(),
                                       self.value_max_grad_norm)
        self.value_optimizer.step()

        argmax_a_q_s = self.online_policy_model(states)
        max_a_q_s = self.online_value_model(states, argmax_a_q_s)

        policy_loss = -max_a_q_s.mean()
        self.policy_optimizer.zero_grad()
        policy_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.online_policy_model.parameters(),
                                       self.policy_max_grad_norm)
        self.policy_optimizer.step()
        return policy_loss, value_loss

    def update_networks(self, tau=None):
        tau = self.tau if tau is None else tau
        for target, online in zip(self.target_value_model.parameters(),
                                  self.online_value_model.parameters()):
            target_ratio = (1.0 - tau) * target.data
            online_ratio = tau * online.data
            mixed_weights = target_ratio + online_ratio
            target.data.copy_(mixed_weights)

        for target, online in zip(self.target_policy_model.parameters(),
                                  self.online_policy_model.parameters()):
            target_ratio = (1.0 - tau) * target.data
            online_ratio = tau * online.data
            mixed_weights = target_ratio + online_ratio
            target.data.copy_(mixed_weights)

    def train(self, seed, gamma, max_episodes):

        self.seed = seed
        self.gamma = gamma
        torch.manual_seed(self.seed); np.random.seed(self.seed); random.seed(self.seed)

        self.episode_timestep = []
        self.p_loss = []
        self.v_loss = []

        self.target_value_model = self.value_model
        self.online_value_model = self.value_model
        self.target_policy_model = self.policy_model
        self.online_policy_model = self.policy_model

        self.value_optimizer = self.value_optimizer_fn(self.online_value_model,
                                                       self.value_optimizer_lr)
        self.value_scheduler = self.value_optim_scheduler(self.value_optimizer)
        self.policy_optimizer = self.policy_optimizer_fn(self.online_policy_model,
                                                         self.policy_optimizer_lr)
        self.policy_scheduler = self.policy_optim_scheduler(self.policy_optimizer)

        self.update_networks(tau=1.0)
        self.episode_timestep.append(0.0)

        for episode in range(max_episodes):
            self.episode_timestep[-1] += 1

            experiences = self.df.sample(batch_size)#, weights='weights')

            states = experiences[experiences.columns[1:9]].values
            actions = experiences[experiences.columns[9]].values.reshape(batch_size,1)
            rewards = experiences[experiences.columns[10]].values.reshape(batch_size,1)
            next_states = experiences[experiences.columns[11:]].values

            experiences = states, actions, rewards, next_states
            experiences = self.online_value_model.load(experiences)

            p_l, v_l = self.optimize_model(experiences)

            if episode % 5 == 0:
              self.policy_scheduler.step()
              self.value_scheduler.step()
              self.p_loss.append(p_l.item())
              self.v_loss.append(v_l.item())

            if np.sum(self.episode_timestep) % self.update_target_every_steps == 0:
                self.update_networks()