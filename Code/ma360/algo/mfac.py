from . import tools
import numpy as np
import tensorflow as tf
import os
import logging

class MFAC:
    def __init__(self, sess, env, name, value_coef=0.1, ent_coef=0.08, gamma=0.95, batch_size=64, learning_rate=1e-4, seed = 318, hidden_size = [256, 256]):
        self.sess = sess
        self.env = env
        self.name = name
        self.action_number = env.get_action_space()       
        self.gamma = gamma
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.value_coef = value_coef  # coefficient of value in the total loss
        self.ent_coef = ent_coef  # coefficient of entropy in the total loss
        self.seed = seed

        self.view_space, self.feature_space = env.get_state_space()
        self.view_buf = np.empty((1,) + self.view_space)
        self.feature_buf = np.empty((1,) + self.feature_space)

        self.action_buf = np.empty(1, dtype=np.int32)
        self.reward_buf = np.empty(1, dtype=np.float32)

        self.replay_buffer = tools.EpisodesBuffer()
        self.hidden_size = hidden_size

        with tf.variable_scope(self.name):
            self.name_scope = tf.get_variable_scope().name
            self._create_network()
            self.model_vars = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, self.name_scope)
            self.saver = tf.train.Saver(self.model_vars, max_to_keep = 20)

    
    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope=self.name_scope)
    
    def flush_buffer(self, **kwargs):
        self.replay_buffer.push(**kwargs)

    def act(self, view, feature, train):
        action = self.sess.run(self.calc_action, {
            self.input_view: view,
            self.input_feature: feature,
            self.is_training: train,
            })
        return action.astype(np.int32).reshape((-1,))

    def _create_network(self):

        tf.set_random_seed(self.seed)

        is_training = tf.placeholder(tf.bool, name='is_training')  #add
        input_view = tf.placeholder(tf.float32, (None,) + self.view_space)
        input_feature = tf.placeholder(tf.float32, (None,) + self.feature_space)
        input_act_prob = tf.placeholder(tf.float32, (None, self.action_number))
        action = tf.placeholder(tf.int32, [None])
        reward = tf.placeholder(tf.float32, [None])

        hidden_size = self.hidden_size

        # ----------------------- dense ------------------------------------------------


        flatten_view = tf.reshape(input_view, [-1, np.prod([v.value for v in input_view.shape[1:]])])
        h_view = tf.layers.dense(flatten_view, units=hidden_size[0], activation=tf.nn.relu, kernel_initializer = tf.glorot_uniform_initializer())
        flatten_feature = tf.reshape(input_feature, [-1, np.prod([v.value for v in input_feature.shape[1:]])])
        h_feature = tf.layers.dense(flatten_feature, units=hidden_size[1], activation=tf.nn.relu, kernel_initializer = tf.glorot_uniform_initializer())

        concat_layer = tf.concat([h_view, h_feature], axis=1)
        dense = tf.layers.dense(concat_layer, units=hidden_size[0] * 2, activation=tf.nn.relu, kernel_initializer = tf.glorot_uniform_initializer())

        policy = tf.layers.dense(dense, units=self.action_number, activation=tf.nn.softmax, kernel_initializer = tf.glorot_uniform_initializer())
        policy = tf.clip_by_value(policy, 1e-10, 1-1e-10)

        self.policy = policy
        self.calc_action = tf.multinomial(tf.log(policy), 1)
        # for value obtain
        emb_prob = tf.layers.dense(input_act_prob, units=64, activation=tf.nn.relu, kernel_initializer = tf.glorot_uniform_initializer())
        dense_prob = tf.layers.dense(emb_prob, units=32, activation=tf.nn.relu, kernel_initializer = tf.glorot_uniform_initializer())
        concat_layer = tf.concat([concat_layer, dense_prob], axis=1)
        dense = tf.layers.dense(concat_layer, units=hidden_size[0], activation=tf.nn.relu, kernel_initializer = tf.glorot_uniform_initializer())
        value = tf.layers.dense(dense, units=1, kernel_initializer = tf.glorot_uniform_initializer())
        value = tf.reshape(value, (-1,))

        # ----------------------- 后续操作 ------------------------------------------------

        action_mask = tf.one_hot(action, self.action_number)
        advantage = tf.stop_gradient(reward - value)

        log_policy = tf.log(policy + 1e-6)
        #之前是1e-6
        log_prob = tf.reduce_sum(log_policy * action_mask, axis=1)

        pg_loss = -tf.reduce_mean(advantage * log_prob)
        vf_loss = self.value_coef * tf.reduce_mean(tf.square(reward - value))
        neg_entropy = self.ent_coef * tf.reduce_mean(tf.reduce_sum(policy * log_policy, axis=1))
        total_loss = pg_loss + vf_loss + neg_entropy

        pg_loss_sum = tf.summary.scalar('pg_loss', pg_loss)
        tf.summary.scalar('vf_loss', vf_loss)
        tf.summary.scalar('neg_entropy', neg_entropy)
        tf.summary.scalar('total_loss', total_loss)

        tf.summary.histogram('policy-histogram', policy)

        self.merged = tf.summary.merge(tf.get_collection(tf.GraphKeys.SUMMARIES, self.name_scope))

        with tf.control_dependencies(tf.get_collection(tf.GraphKeys.UPDATE_OPS, self.name_scope)): #add
        # train op (clip gradient)
            optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate)
            gradients, variables = zip(*optimizer.compute_gradients(total_loss))
            gradients, _ = tf.clip_by_global_norm(gradients, 5.0)
            self.train_op = optimizer.apply_gradients(zip(gradients, variables))
            train_op = tf.train.AdamOptimizer(learning_rate=self.learning_rate).minimize(total_loss)

        self.input_act_prob = input_act_prob
        self.input_view = input_view
        self.input_feature = input_feature
        self.is_training = is_training
        self.action = action
        self.reward = reward
        self.value  = value
        self.train_op = train_op
        self.pg_loss = pg_loss
        self.vf_loss = vf_loss
        self.reg_loss = neg_entropy
        self.total_loss = total_loss
        


    def train(self):

        gamma = self.gamma
        batch_data = self.replay_buffer.episodes()
        self.replay_buffer = tools.EpisodesBuffer() 
        n = 0
        ct = 0
        for episode in batch_data:
            n += len(episode.rewards)

        self.view_buf.resize((n,) + self.view_space)
        self.feature_buf.resize((n,) + self.feature_space)

        self.action_buf.resize(n)
        self.reward_buf.resize(n)
        act_prob_buf = np.zeros((n, self.action_number), dtype=np.float32)

        view = self.view_buf
        feature = self.feature_buf

        action = self.action_buf
        reward = self.reward_buf
        prob = act_prob_buf

        # collect episodes from multiple separate buffers to a continuous buffer
        for k, episode in enumerate(batch_data):

            views, features, actions, rewards, probs= episode.views, episode.features, episode.actions, episode.rewards, episode.probs
            len_episode = len(rewards)

            keep = self.sess.run(self.value, feed_dict={
                self.input_view:[views[-1]],
                self.input_feature:[features[-1]],
                self.input_act_prob: [probs[-1]],
                self.is_training: True
            })[0]

            for i in reversed(range(len_episode)):
                keep = keep * gamma + rewards[i]
                rewards[i] = keep

            view[ct:ct + len_episode] = views
            feature[ct:ct + len_episode] = features
            action[ct:ct + len_episode] = actions
            reward[ct:ct + len_episode] = rewards
            prob[ct:ct + len_episode] = probs
            ct += len_episode

        _, pg_loss, vf_loss, ent_loss, state_value, summary = self.sess.run(
            [self.train_op, self.pg_loss, self.vf_loss, self.reg_loss, \
            self.value, self.merged], feed_dict={
                self.input_view: view,
                self.input_feature: feature,
                self.input_act_prob: prob,
                self.action: action,
                self.reward: reward,
                self.is_training: True
            })


        logging.info("[*] PG_LOSS: {}, VF_LOSS: {}, ENT_LOSS: {}, VALUE: {}".format(np.round(pg_loss, 6), np.round(vf_loss, 6), np.round(ent_loss, 6), np.mean(state_value)))

        return summary

    def save(self, dir_path, step=0):
        
        file_path = os.path.join(dir_path, "mfac_{}".format(step))
        self.saver.save(self.sess, file_path)

        logging.info("[*] Model saved at: {}".format(file_path))

    def load(self, dir_path, step=0):

        file_path = os.path.join(dir_path, "mfac_{}".format(step))
        self.saver.restore(self.sess, file_path)
        logging.info("[*] Loaded model from {}".format(file_path))


        # ----------------------- 加上batch normalization ------------------------------------------------

        # if self.network_config[0] == 'dense' and self.network_config[1] == 'glorot':


        #     flatten_vp = tf.reshape(input_vp, [-1, np.prod([v.value for v in input_vp.shape[1:]])])
        #     h_vp = tf.layers.dense(flatten_vp, units = hidden_size[0], use_bias=False, activation=None)
        #     h_vp = tf.layers.batch_normalization(h_vp, training=is_training)
        #     h_vp = tf.nn.relu(h_vp)

        #     flatten_bw = tf.reshape(input_bw, [-1, np.prod([v.value for v in input_bw.shape[1:]])])
        #     h_bw = tf.layers.dense(flatten_bw, units = hidden_size[1], use_bias=False, activation=None)
        #     h_bw = tf.layers.batch_normalization(h_bw, training=is_training)
        #     h_bw = tf.nn.relu(h_bw)

        #     flatten_remain = tf.reshape(input_remain, [-1, np.prod([v.value for v in input_remain.shape[1:]])])
        #     h_remain = tf.layers.dense(flatten_remain, units = hidden_size[1], use_bias=False, activation=None)
        #     h_remain = tf.layers.batch_normalization(h_remain, training=is_training)
        #     h_remain = tf.nn.relu(h_remain)

        #     self.h_vp = h_vp
        #     self.h_bw = h_bw
        #     self.h_remain = h_remain

        #     concat_layer = tf.concat([h_vp, h_bw], axis=1)
        #     concat_layer = tf.concat([concat_layer, h_remain], axis=1)

        #     dense = tf.layers.dense(concat_layer, units=hidden_size[0] * 2, use_bias=False, activation=None)
        #     dense = tf.layers.batch_normalization(dense, training=is_training)
        #     dense = tf.nn.relu(dense)

        #     self.dense = dense

        #     policy = tf.layers.dense(dense, units=self.action_number, activation=tf.nn.softmax, kernel_initializer = tf.glorot_uniform_initializer())
        #     policy = tf.clip_by_value(policy, 1e-10, 1-1e-10)

        #     self.policy = policy
        #     self.calc_action = tf.multinomial(tf.log(policy), 1)
        #     # for value obtain

        #     emb_prob = tf.layers.dense(input_act_prob, units=64, use_bias=False, activation=None)
        #     emb_prob = tf.layers.batch_normalization(emb_prob, training=is_training)
        #     emb_prob = tf.nn.relu(emb_prob)            

        #     dense_prob = tf.layers.dense(emb_prob, units=32, use_bias=False, activation=None)
        #     dense_prob = tf.layers.batch_normalization(dense_prob, training=is_training)
        #     dense_prob = tf.nn.relu(dense_prob)            

        #     concat_layer = tf.concat([concat_layer, dense_prob], axis=1)

        #     dense = tf.layers.dense(concat_layer, units=hidden_size[0], use_bias=False, activation=None)
        #     dense = tf.layers.batch_normalization(dense, training=is_training)
        #     dense = tf.nn.relu(dense)

        #     value = tf.layers.dense(dense, units=1, kernel_initializer = tf.glorot_uniform_initializer())
        #     value = tf.reshape(value, (-1,))
        #     self.emb_prob = emb_prob
        #     self.dense_prob = dense_prob
        #     self.concat_layer = concat_layer
        #     self.dense2 = dense
        #     self.value = value


        # ----------------------- dense ------------------------------------------------

        # if self.network_config[0] == 'dense' and self.network_config[1] == 'none':

        #     flatten_vp = tf.reshape(input_vp, [-1, np.prod([v.value for v in input_vp.shape[1:]])])
        #     h_vp = tf.layers.dense(flatten_vp, units=hidden_size[0], activation=tf.nn.relu)
        #     flatten_bw = tf.reshape(input_bw, [-1, np.prod([v.value for v in input_bw.shape[1:]])])
        #     h_bw = tf.layers.dense(flatten_bw, units=hidden_size[0], activation=tf.nn.relu)
        #     flatten_remain = tf.reshape(input_remain, [-1, np.prod([v.value for v in input_remain.shape[1:]])])
        #     h_remain = tf.layers.dense(flatten_remain, units=hidden_size[0], activation=tf.nn.relu)

        #     concat_layer = tf.concat([h_vp, h_bw], axis=1)
        #     concat_layer = tf.concat([concat_layer, h_remain], axis=1)

        #     self.concat_layer = concat_layer
        #     dense = tf.layers.dense(concat_layer, units=hidden_size[0] * 2, activation=tf.nn.relu)

        #     self.dense = dense

        #     policy = tf.layers.dense(dense, units=self.action_number, activation=tf.nn.softmax)
        #     policy = tf.clip_by_value(policy, 1e-10, 1-1e-10)

        #     self.policy = policy
        #     self.calc_action = tf.multinomial(tf.log(policy), 1)
        #     # for value obtain
        #     emb_prob = tf.layers.dense(input_act_prob, units=64, activation=tf.nn.relu)
        #     dense_prob = tf.layers.dense(emb_prob, units=32, activation=tf.nn.relu)
        #     concat_layer = tf.concat([concat_layer, dense_prob], axis=1)
        #     dense = tf.layers.dense(concat_layer, units=hidden_size[0], activation=tf.nn.relu)
        #     value = tf.layers.dense(dense, units=1)
        #     value = tf.reshape(value, (-1,))

        # # ----------------------- concat ------------------------------------------------

        # elif self.network_config[0] == 'concat' and self.network_config[1] == 'none':

        #     flatten_vp = tf.reshape(input_vp, [-1, np.prod([v.value for v in input_vp.shape[1:]])])
        #     flatten_bw = tf.reshape(input_bw, [-1, np.prod([v.value for v in input_bw.shape[1:]])])
        #     flatten_remain = tf.reshape(input_remain, [-1, np.prod([v.value for v in input_remain.shape[1:]])])

        #     concat_layer = tf.concat([flatten_vp, flatten_bw, flatten_remain], axis=1)

        #     self.concat_layer = concat_layer
        #     dense = tf.layers.dense(concat_layer, units=hidden_size[0] * 2, activation=tf.nn.relu)

        #     self.dense = dense

        #     policy = tf.layers.dense(dense, units=self.action_number, activation=tf.nn.softmax)
        #     policy = tf.clip_by_value(policy, 1e-10, 1-1e-10)

        #     self.policy = policy
        #     self.calc_action = tf.multinomial(tf.log(policy), 1)
        #     # for value obtain
        #     emb_prob = tf.layers.dense(input_act_prob, units=64, activation=tf.nn.relu)
        #     dense_prob = tf.layers.dense(emb_prob, units=32, activation=tf.nn.relu)
        #     concat_layer = tf.concat([concat_layer, dense_prob], axis=1)
        #     dense = tf.layers.dense(concat_layer, units=hidden_size[0], activation=tf.nn.relu)
        #     value = tf.layers.dense(dense, units=1)
        #     value = tf.reshape(value, (-1,))


        # # ----------------------- concat ------------------------------------------------

        # elif self.network_config[0] == 'concat' and self.network_config[1] == 'glorot':

        #     flatten_vp = tf.reshape(input_vp, [-1, np.prod([v.value for v in input_vp.shape[1:]])])
        #     flatten_bw = tf.reshape(input_bw, [-1, np.prod([v.value for v in input_bw.shape[1:]])])
        #     flatten_remain = tf.reshape(input_remain, [-1, np.prod([v.value for v in input_remain.shape[1:]])])

        #     concat_layer = tf.concat([flatten_vp, flatten_bw, flatten_remain], axis=1)

        #     self.concat_layer = concat_layer
        #     dense = tf.layers.dense(concat_layer, units=hidden_size[0] * 2, activation=tf.nn.relu, kernel_initializer = tf.glorot_uniform_initializer())

        #     self.dense1 = dense

        #     policy = tf.layers.dense(dense, units=self.action_number, activation=tf.nn.softmax, kernel_initializer = tf.glorot_uniform_initializer())
        #     policy = tf.clip_by_value(policy, 1e-10, 1-1e-10)

        #     self.policy = policy
        #     self.calc_action = tf.multinomial(tf.log(policy), 1)
        #     # for value obtain
        #     emb_prob = tf.layers.dense(input_act_prob, units=64, activation=tf.nn.relu, kernel_initializer = tf.glorot_uniform_initializer())
        #     self.emb_prob = emb_prob
        #     dense_prob = tf.layers.dense(emb_prob, units=32, activation=tf.nn.relu, kernel_initializer = tf.glorot_uniform_initializer())
        #     self.dense_prob = dense_prob
        #     concat_layer = tf.concat([concat_layer, dense_prob], axis=1)
        #     self.concat_layer
        #     dense = tf.layers.dense(concat_layer, units=hidden_size[0], activation=tf.nn.relu, kernel_initializer = tf.glorot_uniform_initializer())
        #     self.dense2 = dense
        #     value = tf.layers.dense(dense, units=1, kernel_initializer = tf.glorot_uniform_initializer())
        #     self.value = value
        #     value = tf.reshape(value, (-1,))
