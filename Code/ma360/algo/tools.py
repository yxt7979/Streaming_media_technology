import numpy as np
import config
import logging
import tensorflow as tf
import os
from sklearn.cluster import KMeans



class Color:
    INFO = '\033[1;34m{}\033[0m'
    WARNING = '\033[1;33m{}\033[0m'
    ERROR = '\033[1;31m{}\033[0m'

class EpisodesBufferEntry:
    """Entry for episode buffer"""
    def __init__(self):
        self.views = []
        self.features = []
        self.actions = []
        self.rewards = []
        self.probs = []

    def append(self, view, feature, action, reward, prob):

        self.views.append(view.copy())
        self.features.append(feature.copy())
        self.actions.append(action)
        self.rewards.append(reward)
        self.probs.append(prob)

        
class EpisodesBuffer:
    """Replay buffer to store a whole episode for all agents
       one entry for one agent
    """
    def __init__(self):
        self.buffer = {}

    def push(self, **kwargs):

        views = kwargs['view']
        features = kwargs['feature']

        actions = kwargs['action']
        rewards = kwargs['reward']
        probs = kwargs['prob']
        buffer = self.buffer

        for i in range(len(actions)):
            entry = buffer.get(i)
            if entry is None:
                entry = EpisodesBufferEntry()
                buffer[i] = entry
            entry.append(views[i], features[i], actions[i], rewards[i], probs[i])

    def reset(self):
        """ clear replay buffer """
        self.buffer = {}

    def episodes(self):
        """ get episodes """
        return self.buffer.values()


class Runner:
    def __init__(self, sess, env, agent_number, models, log_dir, model_dir, train=False, concat = False, multi_cache = False, save_every = 50, tau=0.01, print_every=20):
        self.env = env
        self.agent_number = agent_number

        self.log_dir = log_dir
        self.model_dir = model_dir
        self.tau = tau
        self.print_every = print_every
        self.train = train
        self.action_number = self.env.get_action_space()
        self.iteration = 0
        self.total_ave_rewards = 0
        self.start_up_delay = config.config['start_up_delay']
        self.video_size_level = config.config['video_size_level']
        self.video_size = config.config['video_size']


        self.concat = concat
        self.save_every = save_every
        self.multi_cache = multi_cache
        if self.multi_cache:
            self.cache_number = 5
            self.export_bw = 20
        print ('runner-multi_cache', multi_cache)


        if self.train:

            self.target_model = models[0]
            self.update_model = models[1]

            assert isinstance(sess, tf.Session)
            assert self.target_model.name_scope != self.update_model.name_scope
            self.sess = sess

            self.train_writer = tf.summary.FileWriter(
                self.log_dir + '-target' + '_' + 
                str(config.config['delay_param']) + '_' + 
                str(config.config['cost_param']) + '_' +\
                str(config.config['diff_param']) + '_' + 
                str(config.config['model_info']), 
                sess.graph)

            target_vars = self.target_model.vars
            update_vars = self.update_model.vars

            self.sp_op = [tf.assign(target_vars[i], (1. - self.tau) * update_vars[i] + tau * target_vars[i])
                                for i in range(len(target_vars))]

            if not os.path.exists(self.model_dir):
                os.makedirs(self.model_dir)
        else:
            self.model = models

    def run(self, iteration, erp = False, summary = False):

        self.iteration = iteration

        sum_rewards, ave_rewards  = self.playback(erp)

        if self.train:
            logging.info('iteration = {0}'.format(iteration))
        else:
            logging.info("iteration:{0}, sum_rewards:{1}, ave_rewards:{2} ".format(iteration, sum_rewards, ave_rewards))

        if self.train:
            # print(Color.INFO.format('\n[INFO] Begin Update ...'))
            self.sess.run(self.sp_op)  
            # print(Color.INFO.format('[INFO] Self-play Updated!\n'))
            # print(Color.INFO.format('[INFO] Saving model ...'))
            if self.iteration % self.save_every == 0:
                self.target_model.save(
                    self.model_dir + '-target' + '_' + 
                    str(config.config['delay_param']) + '_' + 
                    str(config.config['cost_param']) + '_' +
                    str(config.config['diff_param']) + 
                    str(config.config['model_info']) + 
                    str(self.agent_number), iteration)

                self.target_model.save(
                    self.model_dir + '-update' + '_' + 
                    str(config.config['delay_param']) + '_' + 
                    str(config.config['cost_param']) + '_' +
                    str(config.config['diff_param']) + 
                    str(config.config['model_info']) + 
                    str(self.agent_number), iteration)

        else:
            self.total_ave_rewards += ave_rewards
            print('total_ave_rewards = ', self.total_ave_rewards / (self.iteration + 1))


    def playback(self, erp = False):
        step_ct = 0
        self.env.reset_env(self.iteration)
        max_steps = self.env.get_max_steps()

        #----------------------define paras-----------------------
        reward = [0 for i in range(self.agent_number)]
        action = [0 for i in range(self.agent_number)]

        #----------------------define paras-----------------------

        former_act_prob = [np.zeros((1, self.action_number))]

        print("\n\n[*] ROUND #{0} --------".format(self.iteration))

        sum_rewards = []
        ave_rewards = []


        # while step_ct < max_steps:

        while step_ct < max_steps - 6:
            pass
            #----------------------mfac-----------------------
            if self.train and self.concat:
                view, feature = self.env.get_state(step_ct)
                action = self.target_model.act(view, feature, True)

            elif self.train == False and self.concat:
                if self.multi_cache:
                    vp, bw, remain, vpoint, remaining_part = self.env.get_state(step_ct)
                    action, bw_resize, _label = self.multi_cache_calcu_action_mfac(vp, bw, remain, vpoint, action, reward, remaining_part)
                else:
                    view, feature = self.env.get_state(step_ct)
                    action = self.model.act(view, feature, False)

            #----------------------pytheas-----------------------
            elif self.model.name == 'pytheas':
                vp, bw, remain, vpoint = self.env.get_state(step_ct)
                if self.multi_cache:
                    action, bw_resize, _label = self.multi_cache_calcu_action(vp, bw, remain, vpoint)
                else:
                    action = self.model.act(vp, bw, remain, False)

            #----------------------erp,tile,greedy-----------------------
            else:
                vp, bw, remain, vpoint = self.env.get_state(step_ct)
                if self.multi_cache:
                    action, bw_resize, _label = self.multi_cache_calcu_action_baseline(vp, bw, remain, vpoint)
                else:
                    action = self.model.act(vp, bw, remain, False)


            if self.multi_cache:
                reward = self.env.take_action_multi_cache(action, erp, bw_resize, self.cache_number, _label)
            else:
                reward = self.env.take_action(action, erp)

            sum_reward = np.mean(np.array(reward))

            # --------------global-action---------------
            former_act_prob = np.mean(list(map(lambda x: np.eye(self.action_number)[x], action)), axis=0, keepdims=True)  #byx-add
            former_act_prob = np.tile(former_act_prob, (self.agent_number, 1))
           
            # --------------near-action----------------
            # near_action = []
            # former_act_prob = np.zeros((self.agent_number, self.action_number))
            # for i in range(self.agent_number):
            #     near_action = [action[j] for j in min_distance_list[i]]
            #     former_act_prob[i] = (np.mean(list(map(lambda x: np.eye(self.action_number)[x], near_action)), axis=0, keepdims=True))

            if self.concat and step_ct > self.start_up_delay and self.train:
                buffer = {'view':view, 'feature':feature, 'action': action, 'reward': reward, 'prob': former_act_prob}
                if self.train:
                    self.update_model.flush_buffer(**buffer)

            if not self.train: 
                sum_reward = sum(reward)
                ave_reward = sum_reward / len(action)
                sum_rewards.append(sum_reward)
                ave_rewards.append(ave_reward)

            if not self.train and step_ct % self.print_every == 0:
                print("> step #{0}, sum_reward:{1}, ave_reward:{2}".format(step_ct, sum_reward, ave_reward))

            step_ct += 1

        if self.train:
            summary = self.update_model.train()
            self.train_writer.add_summary(summary, self.iteration)

        if not self.train:
            sum_rewards = sum(sum_rewards) / len(sum_rewards)
            ave_rewards = sum(ave_rewards) / len(ave_rewards)

        return sum_rewards, ave_rewards

    def  multi_cache_calcu_action(self, vp, bw, remain, vpoint):
   # ###### --------------multi-cache------------
        action = [0 for i in range(self.agent_number)]
        _bw = [b[0] for b in bw]
        total_bw = sum(_bw)

        # 聚类
        data = [(vpoint[i][0], vpoint[i][1], bw[i][0], 1) for i in range(0, 48)]  +\
               [(vpoint[i][0], vpoint[i][1], bw[i][0], 2) for i in range(48, 96)] +\
               [(vpoint[i][0], vpoint[i][1], bw[i][0], 3) for i in range(96, 144)]
        _label = KMeans(n_clusters=self.cache_number, max_iter=300, n_init=10).fit_predict(data)

        agent_list = [[[] for i in range(3)] for i in range(self.cache_number)]
        vp_cache   = [[[] for j in range(3)] for i in range(self.cache_number)]
        bw_cache   = [[[] for j in range(3)] for i in range(self.cache_number)]
        bw_resize  = [0 for i in range(self.agent_number)]

        # ----- 把每个用户id分别放到15个类里面，并且把对应的vp和bw放进去
        for i in range(self.agent_number):
            if i < 48:  #video-1
                agent_list[_label[i]][0].append(i)
                vp_cache[_label[i]][0].append(vp[i])
                bw_cache[_label[i]][0].append(bw[i])
            elif i >= 48 and i < 96:
                agent_list[_label[i]][1].append(i)
                vp_cache[_label[i]][1].append(vp[i])
                bw_cache[_label[i]][1].append(bw[i])
            else:
                agent_list[_label[i]][2].append(i)
                vp_cache[_label[i]][2].append(vp[i])
                bw_cache[_label[i]][2].append(bw[i])


        for cache_id in range(self.cache_number):
            for video_id in range(3):
                if len(vp_cache[cache_id][video_id])==0:
                    continue
                tot = np.sum(bw_cache[cache_id][video_id])
                for k,v in enumerate(bw_cache[cache_id][video_id]):
                    if tot > self.export_bw:
                        bw_cache[cache_id][video_id][k] = self.export_bw * bw_cache[cache_id][video_id][k] / tot
                    bw_resize[agent_list[cache_id][video_id][k]] = bw_cache[cache_id][video_id][k]
                action_cluster = self.model.act(vp_cache[cache_id][video_id], bw_cache[cache_id][video_id], remain, False)
                idx = 0
                for i in agent_list[cache_id][video_id]:
                    action[i] = action_cluster[idx]
                    idx+=1

        return action, bw_resize, _label

    def  multi_cache_calcu_action_baseline(self, vp, bw, remain, vpoint):
   # ###### --------------multi-cache------------
        action = [0 for i in range(self.agent_number)]
        _bw = [b[0] for b in bw]
        total_bw = sum(_bw)

        # 聚类
        data = [(vpoint[i][0], vpoint[i][1], bw[i][0], 1) for i in range(0, 48)]  +\
               [(vpoint[i][0], vpoint[i][1], bw[i][0], 2) for i in range(48, 96)] +\
               [(vpoint[i][0], vpoint[i][1], bw[i][0], 3) for i in range(96, 144)]

        np.random.seed(100)
        _label = np.random.choice(5, self.agent_number)

 
        agent_list = [[[] for i in range(3)] for i in range(self.cache_number)]
        vp_cache   = [[[] for j in range(3)] for i in range(self.cache_number)]
        bw_cache   = [[[] for j in range(3)] for i in range(self.cache_number)]
        bw_resize  = [0 for i in range(self.agent_number)]

        # ----- 把每个用户id分别放到15个类里面，并且把对应的vp和bw放进去
        for i in range(self.agent_number):
            if i < 48:  #video-1
                agent_list[_label[i]][0].append(i)
                vp_cache[_label[i]][0].append(vp[i])
                bw_cache[_label[i]][0].append(bw[i])
            elif i >= 48 and i < 96:
                agent_list[_label[i]][1].append(i)
                vp_cache[_label[i]][1].append(vp[i])
                bw_cache[_label[i]][1].append(bw[i])
            else:
                agent_list[_label[i]][2].append(i)
                vp_cache[_label[i]][2].append(vp[i])
                bw_cache[_label[i]][2].append(bw[i])


        for cache_id in range(self.cache_number):
            for video_id in range(3):
                if len(vp_cache[cache_id][video_id])==0:
                    continue
                tot = np.sum(bw_cache[cache_id][video_id])
                for k,v in enumerate(bw_cache[cache_id][video_id]):
                    if tot > self.export_bw:
                        bw_cache[cache_id][video_id][k] = self.export_bw * bw_cache[cache_id][video_id][k] / tot
                    bw_resize[agent_list[cache_id][video_id][k]] = bw_cache[cache_id][video_id][k]
                action_cluster = self.model.act(vp_cache[cache_id][video_id], bw_cache[cache_id][video_id], remain, False)
                idx = 0
                for i in agent_list[cache_id][video_id]:
                    action[i] = action_cluster[idx]
                    idx+=1

        return action, bw_resize, _label

    def cal_view_feature_multi_cache(self, vp, bw, remain, action, reward, remaining_part):


        total_tile_number = 32
        total_view_dim = total_tile_number + 1 + self.video_size_level
        total_feature_dim = 6 + self.video_size_level + 1 + total_tile_number + 1 + self.video_size_level
        agent_number_cache = len(bw)

        index = [list(map(int, list('{:06b}'.format(i)))) for i in range(agent_number_cache)]
        action_one_hot = np.eye(self.video_size_level)

        #---------global-------------

        view = np.zeros((agent_number_cache, 2, total_view_dim))
        feature = np.zeros((agent_number_cache, total_feature_dim))


        viewport_pre_global = np.mean(vp, axis = 0)
        bandwidth_pre_global = np.mean(bw)
        # print("viewport_pre_global",viewport_pre_global[0])
        # print("bandwidth_pre_global", bandwidth_pre_global)
        # visible_tiles = [sum(vp[j]) for j in range(agent_number_cache)]
        # remain_part_local = [[remain[i] / (visible_tiles[i] * rate + (total_tile_number - \
            # visible_tiles[i]) * self.video_size[0]) for rate in self.video_size] for i in range(agent_number_cache)]
        # print ("remain_part_local", remain)
        remain_part_global = np.mean(np.array(remain), axis = 0)
        # print ("remain_part_global", remain_part_global)

        for i in range(agent_number_cache):
            view[i][0][:total_tile_number] = vp[i][0]
            view[i][0][total_tile_number] = bw[i][0]

            view[i][0][total_tile_number+1:] = remain[i][0]
            view[i][1][:total_tile_number] = viewport_pre_global[0]
            view[i][1][total_tile_number] = bandwidth_pre_global
            view[i][1][total_tile_number+1:] = remain_part_global[0]

            feature[i][:6] = index[i]
            feature[i][6:6+self.video_size_level] = action_one_hot[action[i]]
            feature[i][6+self.video_size_level] = reward[i]
            feature[i][6+self.video_size_level + 1: 6+self.video_size_level + 1 +total_tile_number] = vp[i][0]
            feature[i][6+self.video_size_level + 1 +total_tile_number] = bw[i][0]
            feature[i][6+self.video_size_level + 2 +total_tile_number] = remaining_part[i]

        return view, feature


    def multi_cache_calcu_action_mfac(self, vp, bw, remain, vpoint, action, reward, remaining_part):

        action = [0 for i in range(self.agent_number)]
        _bw = [b[0] for b in bw]
        total_bw = sum(_bw)

        # 聚类
        data = [(vpoint[i][0], vpoint[i][1], bw[i][0], 1) for i in range(0, 48)]  +\
               [(vpoint[i][0], vpoint[i][1], bw[i][0], 2) for i in range(48, 96)] +\
               [(vpoint[i][0], vpoint[i][1], bw[i][0], 3) for i in range(96, 144)]
        _label = KMeans(n_clusters=self.cache_number, max_iter=300, n_init=10).fit_predict(data)

        agent_list = [[[] for i in range(3)] for i in range(self.cache_number)]
        vp_cache   = [[[] for j in range(3)] for i in range(self.cache_number)]
        bw_cache   = [[[] for j in range(3)] for i in range(self.cache_number)]
        re_cache   = [[[] for j in range(3)] for i in range(self.cache_number)]
        action_cache = [[[] for j in range(3)] for i in range(self.cache_number)]
        reward_cache   = [[[] for j in range(3)] for i in range(self.cache_number)]
        remaining_part_cache = [[[] for j in range(3)] for i in range(self.cache_number)]


        bw_resize  = [0 for i in range(self.agent_number)]

        # ----- 把每个用户id分别放到15个类里面，并且把对应的vp和bw放进去
        for i in range(self.agent_number):
            if i < 48:  #video-1
                agent_list[_label[i]][0].append(i)
                vp_cache[_label[i]][0].append(vp[i])
                bw_cache[_label[i]][0].append(bw[i])
                re_cache[_label[i]][0].append(remain[i])
                action_cache[_label[i]][0].append(action[i])
                reward_cache[_label[i]][0].append(reward[i])
                remaining_part_cache[_label[i]][0].append(remaining_part[i])

            elif i >= 48 and i < 96:
                agent_list[_label[i]][1].append(i)
                vp_cache[_label[i]][1].append(vp[i])
                bw_cache[_label[i]][1].append(bw[i])
                re_cache[_label[i]][1].append(remain[i])
                action_cache[_label[i]][1].append(action[i])
                reward_cache[_label[i]][1].append(reward[i])
                remaining_part_cache[_label[i]][1].append(remaining_part[i])


            else:
                agent_list[_label[i]][2].append(i)
                vp_cache[_label[i]][2].append(vp[i])
                bw_cache[_label[i]][2].append(bw[i])
                re_cache[_label[i]][2].append(remain[i])
                action_cache[_label[i]][2].append(action[i])
                reward_cache[_label[i]][2].append(reward[i])
                remaining_part_cache[_label[i]][2].append(remaining_part[i])

        for cache_id in range(self.cache_number):
            for video_id in range(3):
                if len(vp_cache[cache_id][video_id])==0:
                    continue
                tot = np.sum(bw_cache[cache_id][video_id])
                for k,v in enumerate(bw_cache[cache_id][video_id]):
                    if tot > self.export_bw:
                        bw_cache[cache_id][video_id][k] = self.export_bw * bw_cache[cache_id][video_id][k] / tot
                    bw_resize[agent_list[cache_id][video_id][k]] = bw_cache[cache_id][video_id][k]


                view, feature = self.cal_view_feature_multi_cache(vp_cache[cache_id][video_id], \
                    bw_cache[cache_id][video_id], re_cache[cache_id][video_id], action_cache[cache_id][video_id], \
                    reward_cache[cache_id][video_id], remaining_part_cache[cache_id][video_id])
                action_cluster = self.model.act(view, feature, False)
                idx = 0
                for i in agent_list[cache_id][video_id]:
                    action[i] = action_cluster[idx]
                    idx+=1

        return action, bw_resize, _label



