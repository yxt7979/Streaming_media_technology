import numpy as np
import config
import math
import logging
import pickle
from tensorflow.contrib import rnn
import tensorflow as tf
from sklearn.linear_model import LinearRegression



class Environment:

    def __init__(self, all_bw_trace_full, all_vp_trace_full, all_vp_table, agent_number, vp_prediction, bw_prediction, random_seed_list, train = False, concat=False, multi_cache = False):

        # ----------------- init basic info -------------------- #
        self.train = train
        self.agent_number = agent_number
        self.video_size = config.config['video_size']
        self.video_quality = config.config['video_quality']
        self.video_size_level = config.config['video_size_level']
        self.total_tile_number = config.config['total_tile_number']
        self.delay_param = config.config['delay_param']
        self.cost_param = config.config['cost_param']
        self.diff_param = config.config['diff_param']
        self.vp_prediction = vp_prediction
        self.bw_prediction = bw_prediction
        self.total_bw_bias = 0
        self.total_vp_bias = 0
        self.vp_ref_number = config.config['vp_lr_ref_number']
        self.bw_ref_number = config.config['bw_lr_ref_number']
        self.nearest_k = config.config['nearest_k']
        self.min_distance_list = []
        self.concat = concat
        self.multi_cache = multi_cache
        print ('env-multi_cache', multi_cache)

        self.start_up_delay = config.config['start_up_delay']

        # ----------------- init vp prediction params -------------------- #
        if vp_prediction == 'lr':
            self.vp_model = LinearRegression()

        elif vp_prediction == 'lstm':
            self.g_vp = tf.Graph()
            self.sess_vp = tf.Session(graph = self.g_vp)
            with self.sess_vp.as_default():
                with self.g_vp.as_default():

                    self.lstm_vp_path = config.viewpoint_model['lstm_vp_path']
                    self.vp_lstm_hidden_size = config.viewpoint_model['lstm_hidden_size']
                    self.viewpoint_state = np.zeros([self.agent_number, 2 * self.vp_lstm_hidden_size])
                    self._create_lstm_vp_prediction_network()
                    self.sess_vp.run(tf.global_variables_initializer())
                    viewpoint_load_var_list = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES)
                    viewpoint_loader = tf.train.Saver(var_list=viewpoint_load_var_list)
                    viewpoint_loader.restore(self.sess_vp, self.lstm_vp_path)

        # ----------------- init bw prediction params -------------------- #
        if bw_prediction == 'lr':
            self.bw_model = LinearRegression()

        elif bw_prediction == 'lstm':
            self.g_bw = tf.Graph()
            self.sess_bw = tf.Session(graph = self.g_bw)
            with self.sess_bw.as_default():
                with self.g_bw.as_default():
                    self.lstm_bw_path = config.bandwidth_model['lstm_bw_path']
                    self.bw_lstm_hidden_size = config.bandwidth_model['lstm_hidden_size']
                    self.bandwidth_state = np.zeros([self.agent_number, 2 * self.bw_lstm_hidden_size])
                    self._create_lstm_bw_prediction_network()
                    self.sess_bw.run(tf.global_variables_initializer())
                    bandwidth_load_var_list = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES)
                    bandwidth_loader = tf.train.Saver(var_list=bandwidth_load_var_list)
                    bandwidth_loader.restore(self.sess_bw, self.lstm_bw_path)

        self.vp_prediction = vp_prediction
        self.bw_prediction = bw_prediction

        self.all_bw_trace_full = all_bw_trace_full
        self.all_vp_trace_full = all_vp_trace_full

        self.all_bw_trace = all_bw_trace_full  #(86,各自时长) ==> (20,秒数)
        self.all_vp_trace = all_vp_trace_full  #(48,9,秒数,2) ==> (20,秒数,2)
        self.all_vp_table = all_vp_table  #(181,91,32)

        self.system_step = 0
        self.last_reward_qoe = np.zeros(self.agent_number)
        self.remaining_part = np.zeros(self.agent_number)
        self.buffer_size = np.zeros(self.agent_number)
        self.stall_time = np.zeros(self.agent_number)
        self.skip_times = np.zeros(self.agent_number)
        self.bw_random_start_time = np.zeros(self.agent_number)     #(20)

        #----------------- define bandwidth and viewport -------------------- #
        self.bandwidth_batch = np.zeros((self.agent_number,self.bw_ref_number + 1))    #(20,3)
        self.viewpoint_batch = np.zeros((self.agent_number,self.vp_ref_number + 1,2))   #(20,4,2) (表示vp需要预测下下秒的)

        self.viewport = np.zeros((self.agent_number, self.total_tile_number)) #real value
        self.viewpoint = np.zeros((self.agent_number,2))
        self.bandwidth = np.zeros((self.agent_number))

        self.viewport_pre = np.zeros((self.agent_number, self.total_tile_number))
        self.viewpoint_pre = np.zeros((self.agent_number,2))
        self.bandwidth_pre = np.zeros((self.agent_number))

        # ----------------- random_pick_traces_and_start_time -------------------- #
        self.random_seed_list  = random_seed_list
        self.random_seed = self.random_seed_list[0]
        if self.train:
            self._random_pick_traces_and_start_time()
        else:
            self._test_pick_traces_and_start_time()

        # ----------------- define state, action, reward -------------------- #
        if self.concat:
            # #concat
            self.total_view_dim = self.total_tile_number + 1 + self.video_size_level
            self.total_feature_dim = 6 + self.video_size_level + 1 + self.total_tile_number + 1 + self.video_size_level

            self.view = np.zeros((self.agent_number, self.nearest_k+1, self.total_view_dim))
            self.feature = np.zeros((self.agent_number, self.total_feature_dim))

            self.id = [list(map(int, list('{:06b}'.format(i)))) for i in range(self.agent_number)]
            self.action_one_hot = np.eye(self.video_size_level)

        

        self.vp = [ None for _ in range(self.agent_number)]
        self.bw = [ None for _ in range(self.agent_number)]
        self.remain = [ None for _ in range(self.agent_number)]

        self.action = [ None for _ in range(self.agent_number)]
        self.reward = [ None for _ in range(self.agent_number)]
        self.dead_agent_index = []

        assert len(self.all_bw_trace) == len(self.all_vp_trace)

    def reset_env(self, iteration):
        self.system_step = 0
        self.last_reward_qoe = 0 
        self.last_viewport = np.zeros((self.agent_number, self.total_tile_number))
        self.remaining_part = np.zeros(self.agent_number)
        self.buffer_size = np.zeros(self.agent_number)
        self.stall_time = np.zeros(self.agent_number)
        self.skip_times = np.zeros(self.agent_number)
        self.bw_random_start_time = np.zeros(self.agent_number)     #(20)
        self.bandwidth_batch = np.zeros((self.agent_number,self.bw_ref_number + 1))    #(20,5)
        self.viewpoint_batch = np.zeros((self.agent_number,self.vp_ref_number + 1,2))   #(20,4,2) (表示vp需要预测下下秒的)
        self.total_bw_bias = 0
        self.total_vp_bias = 0
        self.last_reward = np.zeros(self.agent_number)
        self.reward_qoe = np.zeros(self.agent_number)
        self.action = np.zeros(self.agent_number)
        self.reward = np.zeros(self.agent_number)


        self.random_seed = self.random_seed_list[iteration]
        if self.train:
            self._random_pick_traces_and_start_time()
        else:
            self._test_pick_traces_and_start_time()

        if self.bw_prediction == 'lstm':
            self.bandwidth_state = np.zeros([self.agent_number, 2 * self.bw_lstm_hidden_size])
        if self.vp_prediction == 'lstm':
            self.viewpoint_state = np.zeros([self.agent_number, 2 * self.vp_lstm_hidden_size])

    def _random_pick_traces_and_start_time(self):
        np.random.seed(self.random_seed)
        bw_random_list = np.random.permutation(len(self.all_bw_trace_full))
        self.all_bw_trace = [self.all_bw_trace_full[i] for i in bw_random_list[:self.agent_number]]
        # print("bw_number = ", bw_random_list[:self.agent_number])

        np.random.seed(self.random_seed)
        self.bw_random_start_time = [np.random.randint(len(self.all_bw_trace_full[i])) for i in range(self.agent_number)]
        # print("bw_random_start_time = ", self.bw_random_start_time)

        np.random.seed(self.random_seed)
        video_index = np.random.randint(config.config['train_vp_number'])
        # print("video_index = ", video_index)

        np.random.seed(self.random_seed)
        vp_random_list = np.random.permutation(config.config['available_user_number'])
        self.all_vp_trace = [self.all_vp_trace_full[i][video_index] for i in vp_random_list[:self.agent_number]]


    def _test_pick_traces_and_start_time(self):
        np.random.seed(self.random_seed)
        bw_random_list = np.random.permutation(len(self.all_bw_trace_full))
        self.all_bw_trace = [self.all_bw_trace_full[i] for i in bw_random_list[:self.agent_number]]

        np.random.seed(self.random_seed)
        self.bw_random_start_time = [np.random.randint(len(self.all_bw_trace[i])) for i in range(self.agent_number)]

        np.random.seed(self.random_seed)
        vp_random_list = np.random.permutation(config.config['available_user_number'])

        if not self.multi_cache:
            self.all_vp_trace = [self.all_vp_trace_full[i][0] for i in vp_random_list[:self.agent_number]]  #zhd-delete
        else:
            self.all_vp_trace = [self.all_vp_trace_full[i][0] for i in vp_random_list[:48]]                      #zhd-add
            self.all_vp_trace = self.all_vp_trace + [self.all_vp_trace_full[i][1] for i in vp_random_list[:48]]  #zhd-add
            self.all_vp_trace = self.all_vp_trace + [self.all_vp_trace_full[i][2] for i in vp_random_list[:48]]  #zhd-add

    def _create_lstm_vp_prediction_network(self):
        self.vp_state = tf.placeholder(tf.float32, [self.agent_number, 2 * self.vp_lstm_hidden_size])
        self.vp_input = tf.placeholder(tf.float32, [self.agent_number, 2])
        with tf.name_scope("viewpoint_lstm") as scope:
            vp_lstm_cell = rnn.BasicLSTMCell(num_units = self.vp_lstm_hidden_size , state_is_tuple=False, name = 'rnn/viewpoint_lstm/basic_lstm_cell')
            vp_output, vp_state = vp_lstm_cell(self.vp_input, self.vp_state)
            vp_output = tf.layers.dense(inputs=vp_output, units=2, name='viewpoint/fc', reuse=tf.AUTO_REUSE)
        self.viewpoint_lstm_pre = vp_output
        self.viewpoint_lstm_state = vp_state
    
    def _create_lstm_bw_prediction_network(self):
        self.bw_state = tf.placeholder(tf.float32, [self.agent_number, 2 * self.bw_lstm_hidden_size])
        self.bw_input = tf.placeholder(tf.float32, [self.agent_number, 1])
        with tf.name_scope("bandwidth_lstm") as scope:
            bw_lstm_cell = rnn.BasicLSTMCell(num_units = self.bw_lstm_hidden_size, state_is_tuple=False, name = 'rnn/bandwidth_lstm/basic_lstm_cell')
            bw_output, bw_state = bw_lstm_cell(self.bw_input, self.bw_state)
            bw_output = tf.layers.dense(inputs=bw_output, units=1, name='bandwidth/fc', reuse=tf.AUTO_REUSE)
        self.bandwidth_lstm_pre = bw_output
        self.bandwidth_lstm_state = bw_state

    def _viewport_prediction_real(self):
        return (np.array(self.all_vp_trace))[:, self.system_step]

    def _viewport_prediction_last(self):
        vp = []
        for i in range(self.agent_number):
            vp.append([np.mean(self.viewpoint_batch[i,:self.vp_ref_number,0]),
                np.mean(self.viewpoint_batch[i,:self.vp_ref_number,1])])
        # add
        real_multi_step_vp = []
        for k in range(5):
            real_multi_step_vp.append((np.array(self.all_vp_trace))[:, self.system_step+k])

        multi_step_bias = []
        for k in range(5):
            # print(k)
            ratio = []
            for i in range(self.agent_number):
                _total_v = 0
                _overlay_v = 0
                for j in range(self.total_tile_number):
                    viewport = self._find_viewport_from_viewpoint(real_multi_step_vp[k]) 
                    viewport_pre = self._find_viewport_from_viewpoint(np.array(vp)) 
                    if viewport[i][j] == 1:
                        _total_v += 1
                        if viewport_pre[i][j] == 1:
                            _overlay_v += 1
                ratio.append(_overlay_v / _total_v)
            multi_step_bias.append(np.mean(ratio))
        logging.info('{}'.format(multi_step_bias))

        return np.array(vp)

    def _viewport_prediction_lr(self):
        alpha_res = []
        beta_res = []
        for i in range(self.agent_number):
            buf = 0
            time = [[self.system_step-buf-3], [self.system_step-buf-2], [self.system_step-buf-1]]

            self.vp_model.fit(time, self.viewpoint_batch[i,1:,0])
            alpha = self.vp_model.predict([[self.system_step]])

            self.vp_model.fit(time, self.viewpoint_batch[i,1:,1])
            beta =  self.vp_model.predict([[self.system_step]])
            if alpha[0] > 2 * math.pi:
                alpha = [2 * math.pi]
            elif alpha[0] < 0:
                alpha = [0]
            if beta[0] > math.pi:
                beta = [math.pi]
            elif beta[0] < 0:
                beta = [0]
            assert len(alpha) == 1 and len(beta) == 1
            assert alpha[0] >= 0 and alpha[0] <= 2 * math.pi
            assert beta[0] >= 0 and beta[0] <= math.pi
            alpha_res.append(alpha)
            beta_res.append(beta)


        #add-----------------
        # multi_step_vp = []
        # for k in range(5):
        #     buf = 0
        #     time = [[self.system_step-buf-3], [self.system_step-buf-2], [self.system_step-buf-1]]
        #     multi_alpha_res = []
        #     multi_beta_res = []
        #     for i in range(self.agent_number):
        #         self.vp_model.fit(time, self.viewpoint_batch[i,1:,0])
        #         alpha = self.vp_model.predict([[self.system_step+k]])

        #         self.vp_model.fit(time, self.viewpoint_batch[i,1:,1])
        #         beta =  self.vp_model.predict([[self.system_step+k]])
        #         if alpha[0] > 2 * math.pi:
        #             alpha = [2 * math.pi]
        #         elif alpha[0] < 0:
        #             alpha = [0]
        #         if beta[0] > math.pi:
        #             beta = [math.pi]
        #         elif beta[0] < 0:
        #             beta = [0]
        #         multi_alpha_res.append(alpha)
        #         multi_beta_res.append(beta)

        #     multi_step_vp.append(np.concatenate((alpha_res, beta_res), axis = 1))


        # real_multi_step_vp = []
        # for k in range(5):
        #     real_multi_step_vp.append((np.array(self.all_vp_trace))[:, self.system_step+k])

        # multi_step_bias = []
        # for k in range(5):
        #     print(k)
        #     ratio = []
        #     for i in range(self.agent_number):
        #         _total_v = 0
        #         _overlay_v = 0
        #         for j in range(self.total_tile_number):
        #             viewport = self._find_viewport_from_viewpoint(real_multi_step_vp[k]) 
        #             viewport_pre = self._find_viewport_from_viewpoint(multi_step_vp[k]) 
        #             if viewport[i][j] == 1:
        #                 _total_v += 1
        #                 if viewport_pre[i][j] == 1:
        #                     _overlay_v += 1
        #         ratio.append(_overlay_v/_total_v)
        #     multi_step_bias.append(np.mean(ratio))
        # logging.info('{}'.format(multi_step_bias))

        return np.concatenate((alpha_res, beta_res), axis = 1)

    def _viewport_prediction_lstm(self):
        with self.sess_vp.as_default():
            with self.sess_vp.graph.as_default():
                viewpoint_state = self.viewpoint_state
                vp = self.viewpoint

                viewpoint_pre, viewpoint_state =  self.sess_vp.run([self.viewpoint_lstm_pre, self.viewpoint_lstm_state], \
                    feed_dict={self.vp_state: viewpoint_state, self.vp_input: vp})
                self.viewpoint_pre = viewpoint_pre
                self.viewpoint_state = viewpoint_state


                # #----------------add------------------
                # multi_step_vp = [viewpoint_pre]   
                # multi_step_state = [viewpoint_state]
                # for i in range(4):
                #     viewpoint_pre, viewpoint_state =  self.sess_vp.run([self.viewpoint_lstm_pre, self.viewpoint_lstm_state], \
                #     feed_dict={self.vp_state: viewpoint_state, self.vp_input: vp})
                #     multi_step_vp.append(viewpoint_pre)
                #     multi_step_state.append(viewpoint_state)

                # print(self.system_step)
                # real_multi_step_vp = []
                # for k in range(5):
                #     real_multi_step_vp.append((np.array(self.all_vp_trace))[:, self.system_step+k])
        
                # multi_step_bias = []
                # for k in range(5):
                #     ratio = []
                #     for i in range(self.agent_number):
                #         _total_v = 0
                #         _overlay_v = 0
                #         for j in range(self.total_tile_number):
                #             viewport = self._find_viewport_from_viewpoint(real_multi_step_vp[k]) 
                #             viewport_pre = self._find_viewport_from_viewpoint(multi_step_vp[k]) 
                #             if viewport[i][j] == 1:
                #                 _total_v += 1
                #                 if viewport_pre[i][j] == 1:
                #                     _overlay_v += 1
                #         ratio.append(_overlay_v/_total_v)
                #     multi_step_bias.append(np.mean(ratio))
                # logging.info('{}'.format(multi_step_bias))

        return self.viewpoint_pre

    def _bandwidth_prediction_real(self):
        return np.array([self.all_bw_trace[i][(self.bw_random_start_time[i] + self.system_step) % len(self.all_bw_trace[i])] for i in range(self.agent_number)])

    def _bandwidth_prediction_last(self):
        bw = []
        for i in range(self.agent_number):
            bw.append(np.mean(self.bandwidth_batch[i, :self.bw_ref_number]))

        #add
        # real_multi_step_bw = []
        # for k in range(5):
        #     real_multi_step_bw.append([self.all_bw_trace[i][(self.bw_random_start_time[i] + self.system_step + k) % len(self.all_bw_trace[i])] for i in range(self.agent_number)])
        
        # multi_step_bias = []
        # for k in range(5):
        #     multi_step_bias.append(np.mean([1 - abs(real_multi_step_bw[k][i] - bw[i])/real_multi_step_bw[k][i] for i in range(self.agent_number)]))
        # logging.info('{}'.format(multi_step_bias))

        return bw

    def _bandwidth_prediction_lr(self):
        time = [[self.system_step-4], [self.system_step-3], [self.system_step-2], [self.system_step-1]]
        bw = []
        for i in range(self.agent_number):
            self.bw_model.fit(time, self.bandwidth_batch[i, :])
            bw.append(self.bw_model.predict([[self.system_step]]))
        bw = np.squeeze(np.array(bw))

        #----------add-------------------
        # bw_multi_step = []
        # for k in range(5):
        #     bw_users = []
        #     for i in range(self.agent_number):
        #         self.bw_model.fit(time, self.bandwidth_batch[i, :])
        #         bw_users.append(self.bw_model.predict([[self.system_step+k]]))
        #     # print("k, bw_users",k, bw_users)
        #     bw_multi_step.append(np.squeeze(bw_users))

        # # print("bw_multi_step", bw_multi_step)
        # real_multi_step_bw = []
        # for k in range(5):
        #     real_multi_step_bw.append([self.all_bw_trace[i][(self.bw_random_start_time[i] + self.system_step + k) % len(self.all_bw_trace[i])] for i in range(self.agent_number)])
        
        # # print("real_multi_step_bw", real_multi_step_bw)
        # multi_step_bias = []
        # for k in range(5):
        #     multi_step_bias.append(np.mean([1 - abs(real_multi_step_bw[k][i] - bw_multi_step[k][i])/real_multi_step_bw[k][i] for i in range(self.agent_number)]))
        # logging.info('{}'.format(multi_step_bias))

        return bw

    def _bandwidth_prediction_lstm(self):
        with self.sess_bw.as_default():
            with self.sess_bw.graph.as_default():
                bandwidth_state = self.bandwidth_state
                last_bandwidth_state = self.bandwidth_state
                bw = np.expand_dims(self.bandwidth, axis = 1)

                bandwidth_pre, bandwidth_state =  self.sess_bw.run([self.bandwidth_lstm_pre, self.bandwidth_lstm_state], \
                    feed_dict={self.bw_state: bandwidth_state, self.bw_input: bw})
                self.bandwidth_pre = np.squeeze(bandwidth_pre)
                self.bandwidth_state = bandwidth_state

                # ---------add------------------
                multi_step_bw = [np.squeeze(bandwidth_pre)]   
                multi_step_state = [bandwidth_state]
                for i in range(4):
                    bandwidth_pre, bandwidth_state =  self.sess_bw.run([self.bandwidth_lstm_pre, self.bandwidth_lstm_state], \
                    feed_dict={self.bw_state: bandwidth_state, self.bw_input: bandwidth_pre})
                    multi_step_bw.append(np.squeeze(bandwidth_pre))
                    multi_step_state.append(bandwidth_state)

                real_multi_step_bw = []
                for k in range(5):
                    real_multi_step_bw.append([self.all_bw_trace[i][(self.bw_random_start_time[i] + self.system_step + k) % len(self.all_bw_trace[i])] for i in range(self.agent_number)])
        
                multi_step_bias = []
                for k in range(5):
                    multi_step_bias.append(np.mean([1 - abs(real_multi_step_bw[k][i] - multi_step_bw[k][i])/real_multi_step_bw[k][i] for i in range(self.agent_number)]))
                logging.info('{}'.format(multi_step_bias))

                return self.bandwidth_pre

    def _update_batch(self): #real bandwidth and viewpoint to predict
        self.bandwidth_batch = np.roll(self.bandwidth_batch, -1, axis=1)
        self.viewpoint_batch = np.roll(self.viewpoint_batch, -1, axis=1)

        self.bandwidth_batch[:,-1] = self.bandwidth
        self.viewpoint_batch[:,-1] = self.viewpoint

    def _update_distance_mat(self):  #esti bandwidth and viewpoint 
        self.distance_mat = np.zeros((self.agent_number, self.agent_number))
        for i in range(self.agent_number):
            for j in range(0, i):
                alpha_i, beta_i = self.viewpoint_pre[i]
                alpha_j, beta_j = self.viewpoint_pre[j]
                self.distance_mat[j][i] = self.distance_mat[i][j] = 1 -(math.cos(beta_i) * math.cos(beta_j) + math.sin(beta_i) * math.sin(beta_j) * math.cos(alpha_i - alpha_j))

    def _find_tile_index_from_viewpoint(self):
        self.min_distance_list = [[] for i in range(self.agent_number)]
        tile_w = 1 / 8
        tile_h = 1 / 4
        central_index = [[] for i in range(self.total_tile_number)]
        for i in range(self.agent_number):
            alpha, beta = self.viewpoint_pre[i]
            alpha_idx = math.floor((alpha / (2 * math.pi))/ tile_w)
            beta_idx = math.floor((beta / math.pi)/ tile_h)
            central_index[int(beta_idx * 8 + alpha_idx)].append(i)

        # -----------1邻域------------------
        for i in range(self.total_tile_number):
            for j in central_index[i]:
                self.min_distance_list[j] = central_index[i]
        # -----------8邻域------------------
        # print (central_index)
        # print (self.min_distance_list)

    def get_state_space(self):

        if self.concat:
            #------------concat-global-nearest----------------------
            # view_space = (self.nearest_k+1, self.total_view_dim)
            # feature_space = (self.total_feature_dim,)

            # #------------concat-global-----------------------
            view_space = (2, self.total_view_dim)
            feature_space = (self.total_feature_dim,)

            # #------------concat-nearest-----------------------
            # view_space = (self.nearest_k, self.total_view_dim)
            # feature_space = (self.total_feature_dim,)

            return view_space, feature_space
        else:
            vp_space = (1, self.total_tile_number)  #(2,32)
            bw_space = (1,)  #(2,) 
            remain_space = (1, self.video_size_level) #(2,5)

            return vp_space, bw_space, remain_space

    def _update_state(self): #esti bandwidth and viewpoint 

        visible_tiles = [sum(self.viewport_pre[j]) for j in range(self.agent_number)]
        remain_part_local = [[self.remaining_part[i] / (visible_tiles[i] * rate + (self.total_tile_number - \
            visible_tiles[i]) * self.video_size[0]) for rate in self.video_size] for i in range(self.agent_number)]
        for i in range(self.agent_number):
            self.vp[i] = [self.viewport_pre[i]]
            self.bw[i] = [self.bandwidth_pre[i]]
            self.remain[i] = [remain_part_local[i]]

    def _update_view_feature(self):

        # if self.concat:
            # -----------concat-global and nearest----------------
            # self.view = np.zeros((self.agent_number, self.nearest_k+1, self.total_view_dim))
            # self.feature = np.zeros((self.agent_number, self.total_feature_dim))

            # self._update_distance_mat()
            # self._find_nearest_user_index()

            # viewport_pre_global = np.mean(self.viewport_pre, axis = 0)
            # bandwidth_pre_global = np.mean(self.bandwidth_pre, axis = 0)
            # visible_tiles = [sum(self.viewport_pre[j]) for j in range(self.agent_number)]
            # remain_part_local = [[self.remaining_part[i] / (visible_tiles[i] * rate + (self.total_tile_number - \
            #     visible_tiles[i]) * self.video_size[0]) for rate in self.video_size] for i in range(self.agent_number)]
            # remain_part_global = np.mean(np.array(remain_part_local), axis = 0)


            # for i in range(self.agent_number):
            #     for k, j in enumerate(self.min_distance_list[i]):
            #         self.view[i][k][:self.total_tile_number] = self.viewport_pre[j]
            #         self.view[i][k][self.total_tile_number] = self.bandwidth_pre[j]
            #         self.view[i][k][self.total_tile_number+1:] = remain_part_local[j]

            #     self.view[i][self.nearest_k][:self.total_tile_number] = viewport_pre_global
            #     self.view[i][self.nearest_k][self.total_tile_number] = bandwidth_pre_global
            #     self.view[i][self.nearest_k][self.total_tile_number+1:] = remain_part_global

            #     self.feature[i][:6] = self.id[i]
            #     self.feature[i][6:6+self.video_size_level] = self.action_one_hot[int(self.action[i])]
            #     self.feature[i][6+self.video_size_level] = self.reward[i]
            #     self.feature[i][6+self.video_size_level + 1: 6+self.video_size_level + 1 +self.total_tile_number] = self.viewport_pre[i]
            #     self.feature[i][6+self.video_size_level + 1 +self.total_tile_number] = self.bandwidth_pre[i]
            #     self.feature[i][6+self.video_size_level + 2 +self.total_tile_number] = self.remaining_part[i]
            
            # -----------concat nearest----------------

            # self.view = np.zeros((self.agent_number, self.nearest_k, self.total_view_dim))
            # self.feature = np.zeros((self.agent_number, self.total_feature_dim))
            # self._update_distance_mat()
            # self._find_nearest_user_index()

            # visible_tiles = [sum(self.viewport_pre[j]) for j in range(self.agent_number)]
            # remain_part_local = [[self.remaining_part[i] / (visible_tiles[i] * rate + (self.total_tile_number - \
            #     visible_tiles[i]) * self.video_size[0]) for rate in self.video_size] for i in range(self.agent_number)]


            # for i in range(self.agent_number):
            #     for k, j in enumerate(self.min_distance_list[i]):
            #         self.view[i][k][:self.total_tile_number] = self.viewport_pre[j]
            #         self.view[i][k][self.total_tile_number] = self.bandwidth_pre[j]
            #         self.view[i][k][self.total_tile_number+1:] = remain_part_local[j]

            #     self.feature[i][:6] = self.id[i]
            #     self.feature[i][6:6+self.video_size_level] = self.action_one_hot[int(self.action[i])]
            #     self.feature[i][6+self.video_size_level] = self.reward[i]
            #     self.feature[i][6+self.video_size_level + 1: 6+self.video_size_level + 1 +self.total_tile_number] = self.viewport_pre[i]
            #     self.feature[i][6+self.video_size_level + 1 +self.total_tile_number] = self.bandwidth_pre[i]
            #     self.feature[i][6+self.video_size_level + 2 +self.total_tile_number] = self.remaining_part[i]
                    

            # -----------concat global----------------

        self.view = np.zeros((self.agent_number, 2, self.total_view_dim))
        self.feature = np.zeros((self.agent_number, self.total_feature_dim))

        viewport_pre_global = np.mean(self.viewport_pre, axis = 0)
        bandwidth_pre_global = np.mean(self.bandwidth_pre, axis = 0)
        visible_tiles = [sum(self.viewport_pre[j]) for j in range(self.agent_number)]
        remain_part_local = [[self.remaining_part[i] / (visible_tiles[i] * rate + (self.total_tile_number - \
            visible_tiles[i]) * self.video_size[0]) for rate in self.video_size] for i in range(self.agent_number)]
        remain_part_global = np.mean(np.array(remain_part_local), axis = 0)

        for i in range(self.agent_number):
            self.view[i][0][:self.total_tile_number] = self.viewport_pre[i]
            self.view[i][0][self.total_tile_number] = self.bandwidth_pre[i]
            self.view[i][0][self.total_tile_number+1:] = remain_part_local[i]

            self.view[i][1][:self.total_tile_number] = viewport_pre_global
            self.view[i][1][self.total_tile_number] = bandwidth_pre_global
            self.view[i][1][self.total_tile_number+1:] = remain_part_global

            self.feature[i][:6] = self.id[i]
            self.feature[i][6:6+self.video_size_level] = self.action_one_hot[int(self.action[i])]
            self.feature[i][6+self.video_size_level] = self.reward[i]
            self.feature[i][6+self.video_size_level + 1: 6+self.video_size_level + 1 +self.total_tile_number] = self.viewport_pre[i]
            self.feature[i][6+self.video_size_level + 1 +self.total_tile_number] = self.bandwidth_pre[i]
            self.feature[i][6+self.video_size_level + 2 +self.total_tile_number] = self.remaining_part[i]
           
    def _find_nearest_user_index(self):
        self.min_distance_list = []
        for i in range(self.agent_number):
            self.min_distance_list.append(sorted(range(len(self.distance_mat[i])), key = lambda k : self.distance_mat[i][k])[:self.nearest_k])

    def _find_viewport_from_viewpoint(self, viewpoint):
        alpha, beta = viewpoint[:,0], viewpoint[:,1]
        alpha_index = [math.floor(alpha[i] * 180 / (2 * math.pi)) for i in range(self.agent_number)]
        beta_index = [math.floor(beta[i] * 90 / math.pi) for i in range(self.agent_number)]
        viewport = np.array([self.all_vp_table[alpha_index[i]][beta_index[i]] for i in range(self.agent_number)])
        return viewport

    def get_agent_number(self):
        return self.agent_number

    def get_max_steps(self):
        return len(self.all_vp_trace[0])

    def get_state(self, system_step):
        self.system_step = system_step
        self.dead_agent_index = []

        # ----------------- get esti viewpoint and bandwidth -------------------- #
        if self.system_step <= self.start_up_delay:
            self.bandwidth_pre = self._bandwidth_prediction_real()
            self.viewpoint_pre = self._viewport_prediction_real()
            self.viewport_pre = self._find_viewport_from_viewpoint(self.viewpoint_pre)
        else:
            if self.vp_prediction == 'real':
                self.viewpoint_pre = self._viewport_prediction_real()
            elif self.vp_prediction == 'lr':
                self.viewpoint_pre = self._viewport_prediction_lr()
            elif self.vp_prediction == 'lstm':
                self.viewpoint_pre = self._viewport_prediction_lstm()
            elif self.vp_prediction == 'last':
                self.viewpoint_pre = self._viewport_prediction_last()
            else:
                raise error

            self.viewport_pre = self._find_viewport_from_viewpoint(self.viewpoint_pre)

            if self.bw_prediction == 'real':
                self.bandwidth_pre = self._bandwidth_prediction_real()
            elif self.bw_prediction == 'lr':
                self.bandwidth_pre = self._bandwidth_prediction_lr()
            elif self.bw_prediction == 'lstm':
                self.bandwidth_pre = self._bandwidth_prediction_lstm()
            elif self.bw_prediction == 'last':
                self.bandwidth_pre = self._bandwidth_prediction_last()
            else:
                raise error

        #----------包含上一时刻的viewport--------------------------
        self.last_viewport = self.viewport

        # ----------------- get real viewpoint and bandwidth -------------------- #

        self.bandwidth = self._bandwidth_prediction_real()
        self.viewpoint = self._viewport_prediction_real()
        self.viewport = self._find_viewport_from_viewpoint(self.viewpoint)

        # ----------------- calcu bias -------------------- #
        # one_step_bw_bias = [abs(self.bandwidth[i] - self.bandwidth_pre[i])/self.bandwidth[i] for i in range(self.agent_number)]
        
        # # assert len(self.viewport) == 20
        # ratio = []
        # for i in range(len(self.viewport)):
        #     _total_v = 0
        #     _overlay_v = 0
        #     for j in range(len(self.viewport[i])):
        #         if self.viewport[i][j] == 1:
        #             _total_v += 1
        #             if self.viewport_pre[i][j] == 1:
        #                 _overlay_v += 1
        #     ratio.append(_overlay_v/_total_v)

        # logging.info("\n bw:{}, vp:{} \n".format(np.mean(one_step_bw_bias), np.mean(ratio)))

        #--------------------------
        # one_step_bw_bias = [abs(self.bandwidth[i] - self.bandwidth_pre[i]) for i in range(self.agent_number)]
        # one_step_vp_alpha_bias = [abs(self.viewpoint[i][0] - self.viewpoint_pre[i][0]) for i in range(self.agent_number)]
        # one_step_vp_beta_bias  = [abs(self.viewpoint[i][1] - self.viewpoint_pre[i][1]) for i in range(self.agent_number)]

        # self.total_bw_bias += sum(one_step_bw_bias)
        # self.total_vp_bias += sum(one_step_vp_alpha_bias) + sum(one_step_vp_beta_bias)

        # if self.system_step == self.get_max_steps() - 1:
            # print("avg_one_step_bias_bw = ", self.total_bw_bias / ((self.get_max_steps() - 1) * self.agent_number))
            # print("avg_one_step_bias_vp = ", self.total_vp_bias / ((self.get_max_steps() - 1) * self.agent_number))


        self._update_batch()

        if self.multi_cache and self.concat:
            self._update_state()
            return self.vp, self.bw, self.remain, self.viewpoint_pre, self.remaining_part

        if self.multi_cache or not self.concat:
            self._update_state()
            return self.vp, self.bw, self.remain, self.viewpoint_pre

        else:
            self._update_view_feature()
            return self.view, self.feature

    def get_action_space(self):
        return self.video_size_level

    def take_action(self, action, erp = False):

        self.action = action
        reward_qoe = np.zeros(self.agent_number)
        reward_delay = np.zeros(self.agent_number)
        reward_cost = np.zeros(self.agent_number)
        qoe_diff = np.zeros(self.agent_number)
        avg_reward_qoe = 0
        total_cost = 0

        tile_download_times = np.zeros((self.total_tile_number,self.video_size_level))
        esti_visible_tile_number = self.viewport_pre.sum(1)
        real_visible_tile_number = self.viewport.sum(1)

        # logging.info("\n system_step:{}, action:{}".format(self.system_step, action))
        for i in range(self.agent_number):
            if erp:
                total_chunk_size = self.total_tile_number * self.video_size[self.action[i]]
            else:
                total_chunk_size = (esti_visible_tile_number[i] * self.video_size[self.action[i]] + (self.total_tile_number - esti_visible_tile_number[i]) * self.video_size[0])

            throughput = self.bandwidth[i]
            abs_remaining_part = self.remaining_part[i] #担心浮点运算产生0.00001

            # logging.info("\n agent:{}, bandwidth:{}, buffer_size:{}, real_visible_tile_number:{}, esti_visible_tile_number:{}, \
            #      total_chunk_size:{}, remaining_part:{}, stall_time:{}, skip_times:{}".format(i, self.bandwidth[i], self.buffer_size[i], \
            #          real_visible_tile_number[i], esti_visible_tile_number[i], total_chunk_size, self.remaining_part[i],self.stall_time[i], self.skip_times[i]))
            # # ----------------- simulate the download process -------------------- #
            # 如果发现上一个片段剩下的尾巴在这个片段依旧没下载完，那么就把新的action抹去，下一个action再获取最新内容。
            if abs_remaining_part <= 0.00001 and self.buffer_size[i] <= 0.0001:
                if total_chunk_size <= throughput:
                    self.buffer_size[i] += 1
                    self.remaining_part[i] = 0
                elif total_chunk_size > throughput:
                    self.remaining_part[i] = total_chunk_size - throughput
            elif abs_remaining_part > 0.00001 and self.buffer_size[i] <= 0.0001:
                if abs_remaining_part + total_chunk_size <= throughput:
                    self.buffer_size[i] += 2
                    self.buffer_size[i] -= (1 - self.remaining_part[i] / throughput)
                    self.remaining_part[i] = 0
                elif abs_remaining_part <= throughput:
                    self.buffer_size[i] += 1
                    self.buffer_size[i] -= (1 - self.remaining_part[i] / throughput)
                    self.remaining_part[i] = self.remaining_part[i] + total_chunk_size - throughput
                else: 
                    self.remaining_part[i] = self.remaining_part[i] - throughput
                    self.dead_agent_index.append(i)
            elif abs_remaining_part <= 0.00001 and self.buffer_size[i] > 0.0001:
                if total_chunk_size <= throughput:
                    self.buffer_size[i] -= total_chunk_size / throughput
                    if self.buffer_size[i] < 0:
                        self.stall_time[i] += (-self.buffer_size[i])
                        self.buffer_size[i] = 0 
                    self.buffer_size[i] += 1
                    self.buffer_size[i] -= (1 - total_chunk_size / throughput)
                    self.remaining_part[i] = 0
                elif total_chunk_size > throughput:
                    self.buffer_size[i] -= 1
                    if self.buffer_size[i] < 0:
                        self.stall_time[i] += (-self.buffer_size[i])
                        self.buffer_size[i] = 0 
                    self.remaining_part[i] = total_chunk_size - throughput
            elif abs_remaining_part > 0.00001 and self.buffer_size[i] > 0.0001:
                if abs_remaining_part + total_chunk_size <= throughput:
                    self.buffer_size[i] -= self.remaining_part[i] / throughput
                    if self.buffer_size[i] < 0:
                        self.stall_time[i] += (-self.buffer_size[i])
                        self.buffer_size[i] = 0 
                    self.buffer_size[i] += 1
                    self.buffer_size[i] -= total_chunk_size / throughput
                    if self.buffer_size[i] < 0:
                        self.stall_time[i] += (-self.buffer_size[i])
                        self.buffer_size[i] = 0 
                    self.buffer_size[i] += 1
                    self.buffer_size[i] -= (1 - (self.remaining_part[i] + total_chunk_size) / throughput)
                    self.remaining_part[i] = 0

                elif abs_remaining_part <= throughput:
                    self.buffer_size[i] -= self.remaining_part[i] / throughput
                    if self.buffer_size[i] < 0:
                        self.stall_time[i] += (-self.buffer_size[i])
                        self.buffer_size[i] = 0 
                    self.buffer_size[i] += 1
                    self.buffer_size[i] -= (1 - self.remaining_part[i] / throughput)
                    self.remaining_part[i] = self.remaining_part[i] + total_chunk_size - throughput
                else:
                    self.buffer_size[i] -= 1
                    if self.buffer_size[i] < 0:
                        self.stall_time[i] += (-self.buffer_size[i])
                        self.buffer_size[i] = 0 
                    self.remaining_part[i] = self.remaining_part[i] - throughput
                    self.dead_agent_index.append(i)

            assert self.remaining_part[i] >= 0

            if i in self.dead_agent_index:
                self.reward[i] = 0  #表示产生任何action都没有reward
                reward_qoe[i] = 0
                self.skip_times[i] += 1
            else:
                reward_delay[i] = self.remaining_part[i] 

                # ----------quality-------------------
                if not erp:
                    total_viewport_quality = 0
                    for tile in range(self.total_tile_number):
                        if self.viewport[i][tile] == 1 and self.viewport_pre[i][tile] == 1:
                            total_viewport_quality += self.video_quality[action[i]]
                        elif self.viewport[i][tile] == 1 and self.viewport_pre[i][tile] == 0:
                            total_viewport_quality += self.video_quality[0]
                        if self.viewport_pre[i][tile] == 1:
                            tile_download_times[tile][action[i]] += 1
                        else:
                            tile_download_times[tile][0] += 1
                    # reward_qoe[i] = total_viewport_size / real_visible_tile_number[i]
                    reward_qoe[i] = total_viewport_quality / real_visible_tile_number[i]
                    avg_reward_qoe += reward_qoe[i]

                # ----------quality-------------------

        # logging.info("tile_download_times:{}".format(tile_download_times))
        # logging.info("viiewports:{}".format(self.viewport_pre))
        # logging.info("dead_agent_number:{}, esti_visible_tile_number:{}".format(len(self.dead_agent_index), esti_visible_tile_number))

        # -------------reward single ---------------------
        # if not erp:
        #     for i in range(self.agent_number):
        #         if i not in self.dead_agent_index:
        #             for tile in range(self.total_tile_number):
        #                 if self.viewport_pre[i][tile] == 1:
        #                     reward_cost[i] += self.video_size[action[i]] / tile_download_times[tile][action[i]]
        #                 else: #viewport_pre[i][tile] == 0
        #                     reward_cost[i] += self.video_size[0] / tile_download_times[tile][0]
        #             if self.system_step == 0:
        #                 self.reward[i] = reward_qoe[i] - self.delay_param * reward_delay[i] - self.cost_param * reward_cost[i]
        #             else:
        #                 qoe_diff[i] = abs(reward_qoe[i] - self.last_reward_qoe[i])
        #                 self.reward[i] = reward_qoe[i] - self.diff_param * qoe_diff[i] \
        #                 - self.delay_param * reward_delay[i] - self.cost_param * reward_cost[i]
        # else:
        #     rate_download_times = np.zeros(self.video_size_level)
        #     # if i not in self.dead_agent_index:
        #     for i in range(self.agent_number):
        #         if i not in self.dead_agent_index:
        #             rate_download_times[action[i]] += 1
        #     for i in range(self.agent_number):
        #         if i not in self.dead_agent_index:
        #             # reward_qoe[i] = self.video_size[action[i]] 
        #             reward_qoe[i] = self.video_quality[action[i]] 
        #             avg_reward_qoe += reward_qoe[i]
        #             # reward_qoe[i] = self.video_size[action[i]] * sum(self.viewport[i]) #byx-add
        #             reward_cost[i] = self.video_size[action[i]] * self.total_tile_number / rate_download_times[action[i]]
        #             if self.system_step == 0:
        #                 self.reward[i] = reward_qoe[i] - self.delay_param * reward_delay[i] - self.cost_param * reward_cost[i]
        #             else:
        #                 qoe_diff[i] = abs(reward_qoe[i] - self.last_reward_qoe[i])
        #                 self.reward[i] = reward_qoe[i] - self.diff_param * qoe_diff[i] - self.delay_param * reward_delay[i] - self.cost_param * reward_cost[i]
        # # -------------reward single ---------------------

        # # -------------reward total ---------------------

        _total_cost = 0
        if not erp:

            for tile in range(self.total_tile_number):
                for i in range(self.video_size_level):
                    if tile_download_times[tile][i] != 0:
                        _total_cost += self.video_size[i]

            for i in range(self.agent_number):
                if i not in self.dead_agent_index:
                    reward_cost[i] = _total_cost / (self.agent_number - len(self.dead_agent_index))
                    if self.system_step == 0:
                        self.reward[i] = reward_qoe[i] - self.delay_param * reward_delay[i] - self.cost_param * reward_cost[i]
                    else:
                        self.reward[i] = reward_qoe[i] - self.diff_param * abs(reward_qoe[i] - self.last_reward_qoe[i]) - self.delay_param * reward_delay[i] - self.cost_param * reward_cost[i]

        else:
            rate_download_times = np.zeros(self.video_size_level)
            for i in range(self.agent_number):
                if i not in self.dead_agent_index:
                    rate_download_times[action[i]] += 1
            for i in range(self.video_size_level):
                if rate_download_times[i] != 0:
                    _total_cost += self.video_size[i] * self.total_tile_number

            for i in range(self.agent_number):
                if i not in self.dead_agent_index:
                    reward_qoe[i] = self.video_quality[action[i]] 
                    avg_reward_qoe += reward_qoe[i]
                    reward_cost[i] = _total_cost / (self.agent_number - len(self.dead_agent_index))
                    if self.system_step == 0:
                        self.reward[i] = reward_qoe[i] - self.delay_param * reward_delay[i] - self.cost_param * reward_cost[i]
                    else:
                        self.reward[i] = reward_qoe[i] - self.diff_param * abs(reward_qoe[i] - self.last_reward_qoe[i]) - self.delay_param * reward_delay[i] - self.cost_param * reward_cost[i]

        self.last_reward_qoe = reward_qoe
        total_cost = sum(reward_cost)
        qoe_diff = np.round(qoe_diff, 6)
        # logging.info("\n qoe_diff:{}".format(qoe_diff))
        # logging.info("\n avg_reward_qoe:{}".format(avg_reward_qoe / self.agent_number))
        # logging.info("\n reward:{}, reward_qoe:{}, reward_delay:{}, reward_cost:{}, total_cost:{}".format(self.reward, reward_qoe, reward_delay, reward_cost, total_cost))
        self.reward = 10 * (self.reward - 0.5)
        return self.reward

    def take_action_multi_cache(self, action, erp = False, bw = [], cache_number = 5, group_index = []):  #默认是3个cache

        self.action = action
        reward_qoe = np.zeros(self.agent_number)
        reward_delay = np.zeros(self.agent_number)
        reward_cost = np.zeros(self.agent_number)
        qoe_diff = np.zeros(self.agent_number)
        avg_reward_qoe = 0
        total_cost = 0
        esti_visible_tile_number = self.viewport_pre.sum(1)
        real_visible_tile_number = self.viewport.sum(1)

        # add --------------------
        # bw 表示聚类之后每个人真实的带宽
        # cache_number表示cache的个数
        # group_index表示这个人属于第几个cache
        # agent_list是一个多维数组，第一维是cache个数，第二维是video index，第三维就是对应的用户编号
        agent_list = [[[]for i in range(3)] for i in range(cache_number)]

        for i in range(self.agent_number):
            if i < 48:  #video-1
                agent_list[group_index[i]][0].append(i)
            elif i >= 48 and i < 96:
                agent_list[group_index[i]][1].append(i)
            else:
                agent_list[group_index[i]][2].append(i)

        # logging.info("\n system_step:{}, action:{}".format(self.system_step, action))
        self.dead_agent_index = [[[]for i in range(3)] for i in range(cache_number)]
        _total_cost = np.zeros((cache_number,3))
        total_chunk_size = np.zeros((cache_number, 3))
        tile_download_times = np.zeros((cache_number, 3, self.total_tile_number,self.video_size_level))
        for cache_id in range(cache_number):
            for video_id in range(3):
                for i in agent_list[cache_id][video_id]:
                    if erp:
                        total_chunk_size[cache_id][video_id] = self.total_tile_number * self.video_size[self.action[i]]
                    else:
                        total_chunk_size[cache_id][video_id] = (esti_visible_tile_number[i] * self.video_size[self.action[i]] + (self.total_tile_number - esti_visible_tile_number[i]) * self.video_size[0])

                    throughput = bw[i][0]
                    abs_remaining_part = self.remaining_part[i] #担心浮点运算产生0.00001

                    # logging.info("\n agent:{}, bandwidth:{}, buffer_size:{}, real_visible_tile_number:{}, esti_visible_tile_number:{}, \
                    #      total_chunk_size[cache_id][video_id]:{}, remaining_part:{}, stall_time:{}, skip_times:{}".format(i, self.bandwidth[i], self.buffer_size[i], \
                    #          real_visible_tile_number[i], esti_visible_tile_number[i], total_chunk_size[cache_id][video_id], self.remaining_part[i],self.stall_time[i], self.skip_times[i]))
                    # # ----------------- simulate the download process -------------------- #
                    # 如果发现上一个片段剩下的尾巴在这个片段依旧没下载完，那么就把新的action抹去，下一个action再获取最新内容。
                    if abs_remaining_part <= 0.00001 and self.buffer_size[i] <= 0.0001:
                        if total_chunk_size[cache_id][video_id] <= throughput:
                            self.buffer_size[i] += 1
                            self.remaining_part[i] = 0
                        elif total_chunk_size[cache_id][video_id] > throughput:
                            self.remaining_part[i] = total_chunk_size[cache_id][video_id] - throughput
                    elif abs_remaining_part > 0.00001 and self.buffer_size[i] <= 0.0001:
                        if abs_remaining_part + total_chunk_size[cache_id][video_id] <= throughput:
                            self.buffer_size[i] += 2
                            self.buffer_size[i] -= (1 - self.remaining_part[i] / throughput)
                            self.remaining_part[i] = 0
                        elif abs_remaining_part <= throughput:
                            self.buffer_size[i] += 1
                            self.buffer_size[i] -= (1 - self.remaining_part[i] / throughput)
                            self.remaining_part[i] = self.remaining_part[i] + total_chunk_size[cache_id][video_id] - throughput
                        else: 
                            self.remaining_part[i] = self.remaining_part[i] - throughput
                            self.dead_agent_index[cache_id][video_id].append(i)
                    elif abs_remaining_part <= 0.00001 and self.buffer_size[i] > 0.0001:
                        if total_chunk_size[cache_id][video_id] <= throughput:
                            self.buffer_size[i] -= total_chunk_size[cache_id][video_id] / throughput
                            if self.buffer_size[i] < 0:
                                self.stall_time[i] += (-self.buffer_size[i])
                                self.buffer_size[i] = 0 
                            self.buffer_size[i] += 1
                            self.buffer_size[i] -= (1 - total_chunk_size[cache_id][video_id] / throughput)
                            self.remaining_part[i] = 0
                        elif total_chunk_size[cache_id][video_id] > throughput:
                            self.buffer_size[i] -= 1
                            if self.buffer_size[i] < 0:
                                self.stall_time[i] += (-self.buffer_size[i])
                                self.buffer_size[i] = 0 
                            self.remaining_part[i] = total_chunk_size[cache_id][video_id] - throughput
                    elif abs_remaining_part > 0.00001 and self.buffer_size[i] > 0.0001:
                        if abs_remaining_part + total_chunk_size[cache_id][video_id] <= throughput:
                            self.buffer_size[i] -= self.remaining_part[i] / throughput
                            if self.buffer_size[i] < 0:
                                self.stall_time[i] += (-self.buffer_size[i])
                                self.buffer_size[i] = 0 
                            self.buffer_size[i] += 1
                            self.buffer_size[i] -= total_chunk_size[cache_id][video_id] / throughput
                            if self.buffer_size[i] < 0:
                                self.stall_time[i] += (-self.buffer_size[i])
                                self.buffer_size[i] = 0 
                            self.buffer_size[i] += 1
                            self.buffer_size[i] -= (1 - (self.remaining_part[i] + total_chunk_size[cache_id][video_id]) / throughput)
                            self.remaining_part[i] = 0

                        elif abs_remaining_part <= throughput:
                            self.buffer_size[i] -= self.remaining_part[i] / throughput
                            if self.buffer_size[i] < 0:
                                self.stall_time[i] += (-self.buffer_size[i])
                                self.buffer_size[i] = 0 
                            self.buffer_size[i] += 1
                            self.buffer_size[i] -= (1 - self.remaining_part[i] / throughput)
                            self.remaining_part[i] = self.remaining_part[i] + total_chunk_size[cache_id][video_id] - throughput
                        else:
                            self.buffer_size[i] -= 1
                            if self.buffer_size[i] < 0:
                                self.stall_time[i] += (-self.buffer_size[i])
                                self.buffer_size[i] = 0 
                            self.remaining_part[i] = self.remaining_part[i] - throughput
                            self.dead_agent_index[cache_id][video_id].append(i)

                    assert self.remaining_part[i] >= 0

                    if i in self.dead_agent_index[cache_id][video_id]:
                        self.reward[i] = 0  #表示产生任何action都没有reward
                        reward_qoe[i] = 0
                        self.skip_times[i] += 1
                    else:
                        reward_delay[i] = self.remaining_part[i] 

                        # ----------quality-------------------
                        if not erp:
                            total_viewport_quality = 0
                            for tile in range(self.total_tile_number):
                                if self.viewport[i][tile] == 1 and self.viewport_pre[i][tile] == 1:
                                    total_viewport_quality += self.video_quality[action[i]]
                                elif self.viewport[i][tile] == 1 and self.viewport_pre[i][tile] == 0:
                                    total_viewport_quality += self.video_quality[0]
                                if self.viewport_pre[i][tile] == 1:
                                    tile_download_times[cache_id][video_id][tile][action[i]] += 1
                                else:
                                    tile_download_times[cache_id][video_id][tile][0] += 1
                            # reward_qoe[i] = total_viewport_size / real_visible_tile_number[i]
                            reward_qoe[i] = total_viewport_quality / real_visible_tile_number[i]
                            avg_reward_qoe += reward_qoe[i]

        # # -------------reward total ---------------------

                _total_cost[cache_id][video_id] = 0
                if not erp:
                    for tile in range(self.total_tile_number):
                        for i in range(self.video_size_level):
                            if tile_download_times[cache_id][video_id][tile][i] != 0:
                                _total_cost[cache_id][video_id] += self.video_size[i]

                    for i in agent_list[cache_id][video_id]:
                        if i not in self.dead_agent_index[cache_id][video_id]:
                            reward_cost[i] = _total_cost[cache_id][video_id] / (len(agent_list[cache_id][video_id]) - len(self.dead_agent_index[cache_id][video_id]))
                            if self.system_step == 0:
                                self.reward[i] = reward_qoe[i] - self.delay_param * reward_delay[i] - self.cost_param * reward_cost[i]
                            else:
                                self.reward[i] = reward_qoe[i] - self.diff_param * abs(reward_qoe[i] - self.last_reward_qoe[i]) - self.delay_param * reward_delay[i] - self.cost_param * reward_cost[i]

                else:
                    rate_download_times = np.zeros(self.video_size_level)
                    for i in agent_list[cache_id][video_id]:
                        if i not in self.dead_agent_index[cache_id][video_id]:
                            rate_download_times[action[i]] += 1
                    for i in range(self.video_size_level):
                        if rate_download_times[i] != 0:
                            _total_cost[cache_id][video_id] += self.video_size[i] * self.total_tile_number

                    for i in agent_list[cache_id][video_id]:
                        if i not in self.dead_agent_index[cache_id][video_id]:
                            reward_qoe[i] = self.video_quality[action[i]] 
                            avg_reward_qoe += reward_qoe[i]
                            reward_cost[i] = _total_cost[cache_id][video_id] / (len(agent_list[cache_id][video_id]) - len(self.dead_agent_index[cache_id][video_id]))
                            if self.system_step == 0:
                                self.reward[i] = reward_qoe[i] - self.delay_param * reward_delay[i] - self.cost_param * reward_cost[i]
                            else:
                                self.reward[i] = reward_qoe[i] - self.diff_param * abs(reward_qoe[i] - self.last_reward_qoe[i]) - self.delay_param * reward_delay[i] - self.cost_param * reward_cost[i]

        self.last_reward_qoe = reward_qoe
        # total_cost = sum(reward_cost)
        # qoe_diff = np.round(qoe_diff, 6)
        # logging.info("\n qoe_diff:{}".format(qoe_diff))
        # logging.info("\n avg_reward_qoe:{}".format(avg_reward_qoe / self.agent_number))
        # logging.info("\n reward:{}, reward_qoe:{}, reward_delay:{}, reward_cost:{}, total_cost:{}".format(self.reward, reward_qoe, reward_delay, reward_cost, total_cost))
        self.reward = 10 * (self.reward - 0.5)
        return self.reward

    def update_tile_user_index_table(self):
        self.tile_user_index_table = [[] for i in range(TILE_NUMBER)]

        for i in range(self.agent_number):
            index = (find_tile_index_from_viewpoint(i))
            self.tile_user_index_table[index].append(i) 

