import config
import numpy as np

class Greedy:
	def __init__(self):
		self.name = 'greedy'

	def act(self, vp, bw, remain, train):
		agent_number = len(vp)
		# tile_number = len(vp[0][0])
		tile_number = 32
		size_list = config.config['video_size']
		video_quality = config.config['video_quality']
		size_level = config.config['video_size_level']
		cost_param = config.config['cost_param_greedy']
		agent_selected = np.zeros((agent_number))
		tile_size_selected = np.zeros((tile_number, size_level))
		action = [0 for i in range(agent_number)]

		last_qoe_total = 0
		qoe_single = 0
		agent_id = 0
		rate_id = 0
		# print('vp = ', vp)
		# print('bw = ', bw)
		while agent_selected.sum() != agent_number:
			mmax = - 10000
			for i in range(agent_number):
				if agent_selected[i] == 1:
					continue
				for k in range(size_level):
					total_size = 0
					# quality = size_list[k] * sum(vp[i][0]) 
					# print('h')
					quality = video_quality[k]
					cost = 0
					for t in range(tile_number):
						if vp[i][0][t] == 0:
							total_size += size_list[0]
							if tile_size_selected[t][0] == 0:
								cost += size_list[0]
						else:
							total_size += size_list[k]
							if tile_size_selected[t][k] == 0:
								cost += size_list[k]

					if total_size / bw[i][0] > 1 and k!=0:
						continue
					qoe_single = quality - cost_param * cost
					# print (qoe_single)
					# print('i = {}, k = {}, quality = {}, cost = {}, qoe_single = {}'.format(i, k, quality, cost, qoe_single))
					assert qoe_single > -10000
					if qoe_single > mmax:
						mmax = qoe_single
						agent_id = i
						rate_id = k
						# print (agent_id, rate_id)


			for t in range(tile_number):
				if vp[agent_id][0][t] == 0:
					tile_size_selected[t][0] = 1
				else:
					tile_size_selected[t][rate_id] = 1
			# print("-------agent_id---------", agent_id)

			agent_selected[agent_id] = 1
			action[agent_id] = rate_id
		# print ("-------=======---------")

		return action







