import os
import config

BW_TRACE_FOLDER = './data/dataset/HSDPA_NEW_SCALE/'


def load_bw_trace(bw_trace_folder=BW_TRACE_FOLDER, train = False):
    '''
    INPUT:  all the bandwidth trace
    OUTPUT: all_bw_bandwidth, which is a list of (86,各自时长)
    '''
    
    bw_files = os.listdir(BW_TRACE_FOLDER)
    all_bw_bandwidth = []

    for bw_file in bw_files:
        if bw_file == '.DS_Store':
            continue
        bw_file_path = bw_trace_folder + bw_file
        bw_bandwidth = []

        if train:
            if int(bw_file) <= config.config['train_bw_number']:
                with open(bw_file_path, 'r') as f:
                    for line in f:
                        bw_bandwidth.append(float(line) / config.config['bw_max'])
                all_bw_bandwidth.append(bw_bandwidth)  
        else:
            if int(bw_file) <= config.config['train_bw_number']:  #add
                with open(bw_file_path, 'r') as f:
                    for line in f:
                        bw_bandwidth.append(float(line) / config.config['bw_max'])
                all_bw_bandwidth.append(bw_bandwidth)  

    return all_bw_bandwidth

