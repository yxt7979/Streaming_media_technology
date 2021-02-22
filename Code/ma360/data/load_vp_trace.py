import os
import pandas as pd
import numpy as np
import config

VP_TRACE_FOLDER = './data/dataset/Experiment_2/'
USER_NUMBER = config.config['available_user_number']
VIDEO_NUMBER = config.config['available_video_number']

def load_vp_trace(vp_trace_folder=VP_TRACE_FOLDER, train = False, multi_cache = False):
    '''
    INPUT:  all the viewport 
    OUTPUT: all_vp_trace, which is a list of (48,9,秒数,2) 分别代表48个用户9个视频第几秒钟的alpha和beta.
    '''
    
    user_files = os.listdir(VP_TRACE_FOLDER)

    # if train:
    #     all_user_vp = [[0 for i in range(VIDEO_NUMBER-1)] for i in range(USER_NUMBER)]
    # else:
    #     # all_user_vp = [[] for i in range(USER_NUMBER)]
    all_user_vp = [[] for i in range(USER_NUMBER)]


    for user_file in user_files:
        if user_file  == '.DS_Store':
            continue

        user_file_path = vp_trace_folder + user_file
        user_file_index = int(user_file)-1
        user_video_files = os.listdir(user_file_path)
        for user_video_file in user_video_files:
            if user_video_file == '.DS_Store' or user_video_file[0] == 'v':
                continue
            user_video_index = int(user_video_file[-5])
            if train:
                if user_video_index == config.config['train_vp_number']:
                    continue
                user_video_file_path = user_file_path + '/' + user_video_file
                data =  pd.read_csv(user_video_file_path, header=None)
                data = ((np.array(data))[:,1:3]).tolist()
                (all_user_vp[user_file_index]).append(data)
            else:
                if not multi_cache:
                    if user_video_index == config.config['test_vp_index']:             
                        user_video_file_path = user_file_path + '/' + user_video_file
                        data =  pd.read_csv(user_video_file_path, header=None)
                        data = ((np.array(data))[:,1:3]).tolist()
                        (all_user_vp[user_file_index]).append(data) #zhd-delete
                else:
                    if user_video_index in [6,7,8]:
                        user_video_file_path = user_file_path + '/' + user_video_file
                        data =  pd.read_csv(user_video_file_path, header=None)
                        data = ((np.array(data))[:225,1:3]).tolist() #zhd-add
                        (all_user_vp[user_file_index]).append(data)   #zhd-add

    return all_user_vp

