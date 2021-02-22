# import config
# import numpy as np
# import math
# from sklearn.cluster import KMeans

# class Pytheas:
#     def __init__(self, n_clusters=10):
#         self.name = 'pytheas'
#         self.n_clusters = n_clusters

#     def act(self, vp, bw, remain, vpoint, train):
#         agent_number = len(vp)
#         tile_number = 32
#         size_list =     config.config['video_size']
#         video_quality = config.config['video_quality']
#         size_level =    config.config['video_size_level']
#         cost_param =    config.config['cost_param_greedy']
#         size_number = size_level - 1
#         action_list = []

#         # data = np.array([(bw[i][0], vpoint[i][0], vpoint[i][1]) for i in range(agent_number)])
#         # data = np.array([(bw[i][0]) for i in range(agent_number)])
#         data = np.reshape(np.array(bw)[:,0], (-1, 1))

#         km = KMeans(n_clusters=self.n_clusters, max_iter=300, n_init=10).fit(data)
#         label = km.fit_predict(data)

#         bw_list = [[] for i in range(self.n_clusters)]
#         for i in range(agent_number):
#             bw_list[label[i]].append(data[i][0])

#         for i in range(self.n_clusters):
#             bw_list[i] = np.mean(bw_list[i])

#         bw_avg = [bw_list[label[i]] for i in range(agent_number)]

#         # print(bw)
#         # print(label)
#         # print(bw_avg)

#         for i in range(agent_number):
#             visible_tile_number = sum(vp[i][0])
#             for k, size in enumerate(reversed(size_list)):
#                 if visible_tile_number * size + (tile_number - visible_tile_number) * size_list[0]<= bw_avg[i]:
#                     action_list.append(size_number - k)
#                     break
#                 elif k == size_number:
#                     action_list.append(size_number - k)

#         return action_list

import math
# import matplotlib.pyplot as plt
import random
import config

class Pytheas():
    def __init__(self, arm_number, agent_number, bandit_number=6, train=True):
        self.name = 'pytheas'
        self.train = train
        self.agent_number = agent_number
        self.bandit_number = bandit_number
        self.arm_number = arm_number
        self.bandit = [bandit(arm_number) for i in range(self.bandit_number)]
        self.class_table = [0.28, 0.42, 0.56, 0.70, 0.84]
        self.action_table = [1, 2, 3, 3, 3]

    def act(self, vp, bw, remain):
        if self.train:
            bandit_index = self.get_bandit_index(bw)
            action = [self.bandit[bandit_index[i]].get_action() for i in range(self.agent_number)]
        else:
            action = []
            for b in bw:
                index = len(self.class_table) - 1
                for i, data in enumerate(self.class_table):
                    if b[0] < data:
                        index = i
                        break
                action.append(self.action_table[index])
        return action


    def get_bandit_index(self, bw):
        bandit_index = []
        for b in bw:
            index = self.bandit_number - 1
            for i, data in enumerate(self.class_table):
                if b[0] < data:
                    index = i
                    break
            bandit_index.append(index)
        return bandit_index

    def set_reward(self, action, reward, bw):
        if self.train:
            assert len(reward) == self.agent_number
            assert len(action) == self.agent_number
            bandit_index = self.get_bandit_index(bw)
            for i in range(len(reward)):
                self.bandit[bandit_index[i]].set_reward(action[i], reward[i])

    def save(self):
        if self.train:
            total_times = 0
            for bandit in self.bandit:
                total_times += bandit.total_times
            filename = "./log/ucb1/ucb1_{}_{}_{}_{}_{}_{}_{}".format(config.config['delay_param'],
                                                                     config.config['cost_param'],
                                                                     config.config['diff_param'],
                                                                     self.arm_number,
                                                                     self.agent_number,
                                                                     self.bandit_number,
                                                                     total_times)
            with open(filename, 'w') as f:
                for i, bandit in enumerate(self.bandit):
                    f.write("bandit:{}\n".format(i))
                    f.write("total_times:{}\n".format(bandit.total_times))
                    f.write("action_times: ")
                    for j in range(self.arm_number):
                        f.write("{}, ".format(bandit.action_times[j]))
                    f.write('\n')
                    f.write("avg_reward: ")
                    for j in range(self.arm_number):
                        f.write("{}, ".format(bandit.avg_reward[j]))
                    f.write('\n')

    def load(self, total_times):
        filename = "./log/ucb1/ucb1_{}_{}_{}_{}_{}_{}_{}".format(config.config['delay_param'],
                                                                 config.config['cost_param'],
                                                                 config.config['diff_param'],
                                                                 self.arm_number,
                                                                 self.agent_number,
                                                                 self.bandit_number,
                                                                 total_times)
        with open(filename, 'r') as f:
            for i in range(self.bandit_number):
                bandit = f.readline()
                assert bandit.startswith("bandit:")
                bandit_index = int(bandit[7:])
                assert bandit_index == i

                total_times = f.readline()
                assert total_times.startswith("total_times:")
                total_times = total_times[12:]

                action_times = f.readline()
                assert action_times.startswith("action_times:")
                action_times = action_times[14:-3].split(', ')

                avg_reward = f.readline()
                assert avg_reward.startswith("avg_reward:")
                avg_reward = avg_reward[12:-3].split(', ')

                self.bandit[i].action_times = list(map(int, action_times))
                self.bandit[i].avg_reward = list(map(float, avg_reward))
                self.bandit[i].total_times = int(total_times)



class bandit():
    def __init__(self, arm_number):
        self.arm_number = arm_number
        self.action_times = [0 for i in range(self.arm_number)]
        self.total_times = 0
        self.avg_reward = [0 for i in range(self.arm_number)]



    def get_action(self):
        if self.total_times < self.arm_number:
            action = self.total_times
            return action
        else:
            action = -1
            max_reward = 0
            for i in range(self.arm_number):
                if self.action_times[i] == 0:
                    action = i
                    break
                else:
                    reward = self.avg_reward[i] + math.sqrt(math.log(self.total_times)/self.action_times[i])
                    if reward > max_reward:
                        action = i
                        max_reward = reward
            return action

    def set_reward(self, action, reward):
        self.avg_reward[action] = (self.avg_reward[action]*self.action_times[action] + reward)\
                                 /(self.action_times[action] + 1)
        self.total_times += 1
        self.action_times[action] += 1

if __name__ == '__main__':
    u = UCB1(5, 20)
    u.load(20800)
    # best_action_times = 0
    # best_p_list = []
    # action_list = []
    # reward_list = [3, 1, 4, 3, 5]
    # for i in range(6000):
    #     action = u.get_action()
    #     if action == 4:
    #         best_action_times += 1
    #     best_p_list.append(best_action_times/(i+1))
    #     reward = reward_list[action] + random.random()*2
    #     action_list.append(reward/7)
    #     u.set_reward(action, reward)
    # plt.plot(best_p_list)
    # plt.plot(action_list)
    # plt.show()
