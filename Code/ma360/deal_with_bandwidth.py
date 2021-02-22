import os

'''
This program is to scale the HSDPA data to (x+500)*10,
which can make the bandwidth fall in [5000, 40000]
'''

BW_TRACE_FOLDER = './data/dataset/HSDPA/'
NEW_TRACE_FOLDER = './data/dataset/HSDPA_NEW_SCALE/'
    
bw_files = os.listdir(BW_TRACE_FOLDER)
for bw_file in bw_files:
	if bw_file == '.DS_Store':
		continue
	bw_file_path = BW_TRACE_FOLDER + bw_file
	bw_new_file_path = NEW_TRACE_FOLDER + bw_file

	

	f_bw = open(bw_file_path, 'r')
	f_bw_new = open(bw_new_file_path, 'w')

	for line in f_bw:
		if float(line) > 5000:
			continue
		new_bw = float(line) * 21000 / 5000 + 4000
		# new_bw = (float(line) + 500.0)*10
		f_bw_new.write(str(new_bw)+'\n')

	f_bw.close()
	f_bw_new.close()



