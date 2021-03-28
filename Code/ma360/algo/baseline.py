import config

class BaselineERP:
	def __init__(self):
		self.name = 'erp'
	def act(self, vp, bw, remain, train):
		agent_number = len(vp)
		# tile_number = len(vp[0][0])
		tile_number = 32
		size_list = config.config['video_size']
		size_level = config.config['video_size_level']
		size_number = size_level - 1
		action_list = []

		for i in range(agent_number):
			for k, size in enumerate(reversed(size_list)):
				if tile_number * size <= bw[i][0]:
					action_list.append(size_number - k)
					break
				elif k == size_number:
					action_list.append(size_number - k)
		return action_list

class BaselineTile:
	def __init__(self):
		self.name = 'tile'
	def act(self, vp, bw, remain, train):
		agent_number = len(vp)
		# tile_number = len(vp[0][0]) 
		tile_number = 32
		size_list = config.config['video_size']
		size_level = config.config['video_size_level']
		size_number = size_level - 1
		action_list = []
		for i in range(agent_number):
			visible_tile_number = sum(vp[i][0])
			for k, size in enumerate(reversed(size_list)):
				if visible_tile_number * size + (tile_number - visible_tile_number) * size_list[0]<= bw[i][0]:
					action_list.append(size_number - k)
					break
				elif k == size_number:
					action_list.append(size_number - k)
		return action_list

# class