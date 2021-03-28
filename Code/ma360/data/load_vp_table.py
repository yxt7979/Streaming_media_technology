import os
import pandas as pd
import config

VP_TABLE_FOLDER = './data/dataset/vp_table/'
SAMPLE_RATIO_COL = config.config['sample_ratio_col']
SAMPLE_RATIO_ROW = config.config['sample_ratio_row']

def load_vp_table(vp_table_folder=VP_TABLE_FOLDER):
    '''
    INPUT:  all the viewport table
    OUTPUT: all_vp_table, which is a list of (181,91,32)
    '''
    vp_files = os.listdir(VP_TABLE_FOLDER)
    all_vp_table = []

    for vp_file in vp_files:
        if vp_file == '.DS_Store':
            continue
        vp_file_path = vp_table_folder + vp_file

        data =  pd.read_csv(vp_file_path, header=None)

        for i in range(SAMPLE_RATIO_COL):
            vp_table = []
            for j in range(SAMPLE_RATIO_ROW):
                vp_table.append((list((data.ix[i*SAMPLE_RATIO_ROW+j])[2:34])))
            all_vp_table.append(vp_table)

    return all_vp_table
