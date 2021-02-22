# -*- coding: utf-8 -*-
import argparse
import os
import tensorflow as tf
import numpy as np

import env
import data
import config
import algo
from algo import tools
import logging

if __name__ == '__main__':

    #----- command line analysis -------------------- #
    parser = argparse.ArgumentParser()
    parser.add_argument('--algo', type=str, default = 'mfac', choices={'mfac', 'erp', 'tile', 'greedy', 'pytheas'}, help='choose an algorithm from the preset')
    parser.add_argument('--train', type=str, default='no', choices={'yes', 'no'}, help='train or test')
    parser.add_argument('--vp_prediction', type=str, default='real', choices={'real', 'lr','lstm', 'last'}, help='choose an algorithm to predict viewpoint')
    parser.add_argument('--bw_prediction', type=str, default='lstm', choices={'real', 'lr', 'lstm', 'last'}, help='choose an algorithm to predict bandwidth')
    parser.add_argument('--agent_number', type=int, default=48, choices=range(1,49), help='choose agent numbers') # the agent number is [1,48]
    # parser.add_argument('--agent_number', type=int, default=144, choices=range(1,149), help='choose agent numbers') # the agent number is [1,148] #zhd
    parser.add_argument('--round_number', type=int, default=50000, help='set the trainning round')  # 训练2000轮
    parser.add_argument('--test_number', type=int, default=1, help='set the test round')  # 训练2000轮
    parser.add_argument('--test_index', type=int, default=2750, help='set the test index')  # 训练2000轮
    parser.add_argument('--show_results_every', type=int, default=50, help='show the results every k steps') 
    parser.add_argument('--save_every', type=int, default=50, help='save model every k steps') 
    parser.add_argument('--multi_cache', type=str, default='no', choices={'yes', 'no'}, help='save model every k steps') 

    args = parser.parse_args()

    if args.multi_cache == 'yes':
        args.multi_cache = True
    else:
        args.multi_cache = False
    print (args.multi_cache)
    # ----------------- config tensorflow -------------------- #
    tf_config = tf.ConfigProto(
        allow_soft_placement=True, 
        log_device_placement=False, 
        device_count={"CPU":14},\
        inter_op_parallelism_threads=1,
        intra_op_parallelism_threads=1)
    tf_config.gpu_options.allow_growth = True
    sess = tf.Session(config = tf_config)

    # ----------------- config log address -------------------- #
    log_dir = './summary/models/{}'.format(args.algo)
    model_dir = './data/models/{}'.format(args.algo)

    # ----------------- load bw and vp trace -------------------- #
    all_bw_trace_train = data.load_bw_trace(train = True)  # (60 457)
    all_bw_trace_test = data.load_bw_trace(train = False)  # (26 1064)   //86+86
    if args.multi_cache:
        all_bw_trace_test = all_bw_trace_test + all_bw_trace_test  #zhd-add

    all_vp_trace_train = data.load_vp_trace(train = True, multi_cache = args.multi_cache)  # (48 8 278 2)
    all_vp_trace_test = data.load_vp_trace(train = False, multi_cache = args.multi_cache)  # (48 1 520 2)  

    # print (len(all_bw_trace_test), len(all_bw_trace_test[0]))
    # print (len(all_vp_trace_test), len(all_vp_trace_test[0]), len(all_vp_trace_test[0][0]))
    # # (172,441)和(48,3,373)


    all_vp_table = data.load_vp_table()  # (181,91,32)

    #----------------- generate random trace for each iteration -------------------- #
    np.random.seed(config.config['random_seed'])
    pick_trace_random = np.random.permutation(args.round_number)

    # # ----------------- args.algo == 'mfac' and train -------------------- #
    if args.algo == 'mfac' and args.train == 'yes':
        logging.basicConfig(format='%(levelname)s: %(message)s',
                            level=logging.INFO,
                            filename='./log/mfac-train'+ '_' + 
                            str(config.config['delay_param']) + '_' + 
                            str(config.config['cost_param']) +  '_' + 
                            str(config.config['diff_param']) +  '_' + 
                            str(config.config['cost_param_greedy']) + '_' + 
                            str(args.agent_number) + 
                            str(config.config['model_info']),
                            filemode='w')

        env_train = env.m_env(all_bw_trace_train, all_vp_trace_train, all_vp_table, 
            args.agent_number, args.vp_prediction, args.bw_prediction, pick_trace_random, 
            train = True, 
            concat = True,
            multi_cache = args.multi_cache)
        
        env_test  = env.m_env(all_bw_trace_test, all_vp_trace_test, all_vp_table, 
            args.agent_number, args.vp_prediction, args.bw_prediction, pick_trace_random, 
            train=False, 
            concat = True,
            multi_cache = args.multi_cache)
        models = [algo.mfac(sess, env_train, 'target-network',  **config.mfac_model), algo.mfac(sess, env_train, 'update-network', **config.mfac_model)]
        sess.run(tf.global_variables_initializer())

        #---------keep training from existed files-------
        # models[0].load(model_dir + '-target' + '_' + 
        #     str(config.config['delay_param']) + '_' + 
        #     str(config.config['cost_param']) + '_' + 
        #     str(config.config['diff_param']) + 
        #     str(config.config['model_info']) +
        #     str(args.agent_number), 620)

        # models[1].load(model_dir + '-update' + '_' + 
        #     str(config.config['delay_param']) + '_' + 
        #     str(config.config['cost_param']) + '_' + 
        #     str(config.config['diff_param']) + 
        #     str(config.config['model_info']) +
        #     str(args.agent_number), 620)

        runner_train = tools.Runner(sess, env_train, args.agent_number, models, 
            log_dir=log_dir, 
            model_dir=model_dir, 
            train=True, 
            concat=True, 
            multi_cache = args.multi_cache,
            **config.runner)

        runner_test = tools.Runner(sess, env_test, args.agent_number, models[0], 
            log_dir=log_dir, 
            model_dir=model_dir, 
            train=False, 
            concat=True,
            multi_cache = args.multi_cache, 
            **config.runner)

        for k in range(args.round_number):
            runner_train.run(k)
            if k % args.show_results_every == 0: #show results every 50 steps
                runner_test.run(0)

    # # ----------------- args.algo == 'mfac' and no train -------------------- #
    elif args.algo == 'mfac' and args.train == 'no':
        logging.basicConfig(format='%(message)s',
                            level=logging.INFO,
                            filename='./log/mfac-test'+ '_' +
                            str(config.config['delay_param']) + '_' + 
                            str(config.config['cost_param']) +  '_' + 
                            str(config.config['diff_param']) +  '_' + 
                            str(config.config['cost_param_greedy']) + '_' + 
                            str(args.agent_number) + 
                            str(config.config['model_info']),
                            filemode='w')

        print('algo ------ mfac - test')

        env = env.m_env(all_bw_trace_test, all_vp_trace_test, all_vp_table, 
            args.agent_number, args.vp_prediction, args.bw_prediction, pick_trace_random, 
            train=False, 
            concat=True,
            multi_cache = args.multi_cache)

        models = algo.mfac(sess, env, 'target-network', **config.mfac_model)
        sess.run(tf.global_variables_initializer())

        models.load(model_dir + '-target' + '_' + 
            str(config.config['delay_param']) + '_' + 
            str(config.config['cost_param']) + '_' + 
            str(config.config['diff_param']) + 
            str(config.config['model_info']) +
            str(args.agent_number), args.test_index)

        runner = tools.Runner(sess, env, args.agent_number, models, 
            log_dir=log_dir, 
            model_dir=model_dir, 
            train=False, 
            concat = True,
            multi_cache = args.multi_cache,
            **config.runner)

        for i in range(args.test_number):
            runner.run(i)

        print('algo ------ mfac - test')
    
    # # ----------------- args.algo == 'erp' -------------------- #
    elif args.algo == 'erp':
        logging.basicConfig(format='%(message)s',
                            # format='%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s',
                            level=logging.INFO,
                            filename='./log/erp'+ '_' +
                            str(config.config['delay_param']) + '_' + 
                            str(config.config['cost_param']) +  '_' + 
                            str(config.config['diff_param']) +  '_' + 
                            str(config.config['cost_param_greedy']) + '_' + 
                            str(args.agent_number) + 
                            str(config.config['model_info'] + 'Baseline_Viewport'),
                            filemode='w')

        print('algo ------ erp')
        env = env.m_env(all_bw_trace_test, all_vp_trace_test, all_vp_table, 
            args.agent_number, args.vp_prediction, args.bw_prediction, pick_trace_random, 
            train=False,
            multi_cache = args.multi_cache) 

        models = algo.erp()
        runner = tools.Runner(sess, env, args.agent_number, models, 
            log_dir=log_dir, 
            model_dir=model_dir, 
            train=False, 
            multi_cache = args.multi_cache,
            **config.runner)

        for i in range(args.test_number):
            runner.run(i, erp = True)

        print('algo ------ erp')

    # # ----------------- args.algo == 'tile' -------------------- #
    elif args.algo == 'tile':
        logging.basicConfig(format='%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s',
                            level=logging.INFO,
                            filename='./log/tile'+ '_' +
                            str(config.config['delay_param']) + '_' + 
                            str(config.config['cost_param']) +  '_' + 
                            str(config.config['diff_param']) +  '_' + 
                            str(config.config['cost_param_greedy']) + '_' + 
                            str(args.agent_number) + 
                            str(config.config['model_info']),
                            filemode='w')

        print('algo ------ tile')
        env = env.m_env(all_bw_trace_test, all_vp_trace_test, all_vp_table, 
            args.agent_number, args.vp_prediction, args.bw_prediction, pick_trace_random, 
            train=False,
            multi_cache = args.multi_cache) 

        models = algo.tile()
        runner = tools.Runner(sess, env, args.agent_number, models, 
            log_dir=log_dir, 
            model_dir=model_dir, 
            train=False,
            multi_cache = args.multi_cache, 
            **config.runner)

        for i in range(args.test_number):
            runner.run(i)
        print('algo ------ tile')

    # # ----------------- args.algo == 'greedy' -------------------- #
    elif args.algo == 'greedy':
        logging.basicConfig(format='%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s',
                            level=logging.INFO,
                            filename='./log/greedy'+ '_' +
                            str(config.config['delay_param']) + '_' + 
                            str(config.config['cost_param']) +  '_' + 
                            str(config.config['diff_param']) +  '_' + 
                            str(config.config['cost_param_greedy']) + '_' + 
                            str(args.agent_number) + 
                            str(config.config['model_info']),
                            filemode='w')        

        print('algo ------ greedy')
        env = env.m_env(all_bw_trace_test, all_vp_trace_test, all_vp_table, 
            args.agent_number, args.vp_prediction, args.bw_prediction, pick_trace_random, 
            train=False,
            multi_cache = args.multi_cache) 

        models = algo.greedy()
        runner = tools.Runner(sess, env, args.agent_number, models, 
            log_dir=log_dir, 
            model_dir=model_dir, 
            train=False, 
            multi_cache = args.multi_cache,
            **config.runner)

        for i in range(args.test_number):
            runner.run(i)
        print('algo ------ greedy')

    # # ----------------- args.algo == 'pytheas' -------------------- #
    elif args.algo == 'pytheas':
        logging.basicConfig(format='%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s',
                            level=logging.INFO,
                            filename='./log/pytheas'+ '_' +
                            str(config.config['delay_param']) + '_' + 
                            str(config.config['cost_param']) +  '_' + 
                            str(config.config['diff_param']) +  '_' + 
                            str(config.config['cost_param_greedy']) + '_' + 
                            str(args.agent_number) + 
                            str(config.config['model_info']),
                            filemode='w')

        print('algo ------ pytheas')
        env = env.m_env(all_bw_trace_test, all_vp_trace_test, all_vp_table, 
            args.agent_number, args.vp_prediction, args.bw_prediction, pick_trace_random, 
            train=False,
            multi_cache = args.multi_cache) 

        models = algo.pytheas()
        runner = tools.Runner(sess, env, args.agent_number, models, 
            log_dir=log_dir, 
            model_dir=model_dir, 
            train=False,
            multi_cache = args.multi_cache, 
            **config.runner)

        for i in range(args.test_number):
            runner.run(i)
        print('algo ------ pytheas')









