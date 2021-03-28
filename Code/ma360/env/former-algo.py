
        # -----------global------------------
        # viewport_pre_global = np.mean(self.viewport_pre, axis = 0)
        # bandwidth_pre_global = np.mean(self.bandwidth_pre, axis = 0)
        # visible_tiles = [sum(self.viewport_pre[j]) for j in range(self.agent_number)]
        # remain_part_local = [[self.remaining_part[i] / (visible_tiles[i] * rate + (self.total_tile_number - \
        #     visible_tiles[i]) * self.video_size[0]) for rate in self.video_size] for i in range(self.agent_number)]
        # remain_part_global = np.mean(np.array(remain_part_local), axis = 0)

        # for i in range(self.agent_number):
        #     self.vp[i] = [self.viewport_pre[i], viewport_pre_global]
        #     self.bw[i] = [self.bandwidth_pre[i], bandwidth_pre_global]
        #     self.remain[i] = [remain_part_local[i], remain_part_global]


        # -----------global last viewport------------------

        # viewport_pre_global = np.mean(self.viewport_pre, axis = 0)
        # bandwidth_pre_global = np.mean(self.bandwidth_pre, axis = 0)
        # visible_tiles = [sum(self.viewport_pre[j]) for j in range(self.agent_number)]
        # remain_part_local = [[self.remaining_part[i] / (visible_tiles[i] * rate + (self.total_tile_number - \
        #     visible_tiles[i]) * self.video_size[0]) for rate in self.video_size] for i in range(self.agent_number)]
        # remain_part_global = np.mean(np.array(remain_part_local), axis = 0)

        # for i in range(self.agent_number):
        #     self.vp[i] = [self.viewport_pre[i], self.last_viewport[i], viewport_pre_global]
        #     self.bw[i] = [self.bandwidth_pre[i], self.bandwidth_batch[i,-2], bandwidth_pre_global]
        #     self.remain[i] = [remain_part_local[i], remain_part_global]

        # # -----------near------------------
        # remain_part_local = [[] for _ in range(self.agent_number)]
        # remain_part_local_idx = [[] for _ in range(self.agent_number)]
        # visible_tiles = [sum(self.viewport_pre[j]) for j in range(self.agent_number)]

        # remain_part_local = [[self.remaining_part[i] / (visible_tiles[i] * rate + (self.total_tile_number - \
        #    visible_tiles[i]) * self.video_size[0]) for rate in self.video_size] for i in range(self.agent_number)]
       

        # for i in range(self.agent_number):
        #     viewport_pre_near =  np.mean([self.viewport_pre[j] for j in self.min_distance_list[i]], axis = 0)
        #     self.vp[i] = [self.viewport_pre[i], viewport_pre_near]
        #     bandwidth_pre_near = np.mean([self.bandwidth_pre[j] for j in self.min_distance_list[i]], axis = 0)
        #     self.bw[i] = [self.bandwidth_pre[i], bandwidth_pre_near]

        #     remain_part_local_idx[i] = np.mean(np.array([remain_part_local[j] for j in self.min_distance_list[i]]), axis = 0)
        #     self.remain[i] = [remain_part_local[i], remain_part_local_idx[i]]

        # -----------global-near-3x------------------
        # remain_part_local = [[] for _ in range(self.agent_number)]
        # remain_part_local_idx = [[] for _ in range(self.agent_number)]
        # visible_tiles = [sum(self.viewport_pre[j]) for j in range(self.agent_number)]

        # viewport_pre_global = np.mean(self.viewport_pre, axis = 0)
        # bandwidth_pre_global = np.mean(self.bandwidth_pre, axis = 0)

        # remain_part_local = [[self.remaining_part[i] / (visible_tiles[i] * rate + (self.total_tile_number - \
        #     visible_tiles[i]) * self.video_size[0]) for rate in self.video_size] for i in range(self.agent_number)]
        # remain_part_global = np.mean(np.array(remain_part_local), axis = 0)

        # for i in range(self.agent_number):
        #     viewport_pre_near =  np.mean([self.viewport_pre[j] for j in self.min_distance_list[i]], axis = 0)
        #     self.vp[i] = [self.viewport_pre[i], viewport_pre_near, viewport_pre_global]
        #     bandwidth_pre_near = np.mean([self.bandwidth_pre[j] for j in self.min_distance_list[i]], axis = 0)
        #     self.bw[i] = [self.bandwidth_pre[i], bandwidth_pre_near, bandwidth_pre_global]
        #     remain_part_local_idx[i] = np.mean(np.array([remain_part_local[j] for j in self.min_distance_list[i]]), axis = 0)
        #     self.remain[i] = [remain_part_local[i], remain_part_local_idx[i], remain_part_global]

        # -----------near-specific-----------------
        # self.vp = [ [] for _ in range(self.agent_number)]
        # self.bw = [ [] for _ in range(self.agent_number)]
        # self.remain = [ [] for _ in range(self.agent_number)]
        # for i in range(self.agent_number):
        #     for j in self.min_distance_list[i]:
        #         self.vp[i].append(self.viewport_pre[j])  #20,5,32
        #         self.bw[i].append(self.bandwidth_pre[j]) #20,5,1
        #         visible_tiles = sum(self.viewport_pre[j])
        #         self.remain[i].append([self.remaining_part[j] / (visible_tiles * rate + (self.total_tile_number - visible_tiles) * self.video_size[0]) for rate in self.video_size])  #5,6


        # -----------near-specific-global-----------------
        # self.vp = [ [] for _ in range(self.agent_number)]
        # self.bw = [ [] for _ in range(self.agent_number)]
        # self.remain = [ [] for _ in range(self.agent_number)]
        # viewport_pre_global = np.mean(self.viewport_pre, axis = 0)
        # bandwidth_pre_global = np.mean(self.bandwidth_pre, axis = 0)
        # visible_tiles = [sum(self.viewport_pre[j]) for j in range(self.agent_number)]
        # remain_part_local = [[self.remaining_part[i] / (visible_tiles[i] * rate + (self.total_tile_number - \
        #     visible_tiles[i]) * self.video_size[0]) for rate in self.video_size] for i in range(self.agent_number)]
        # remain_part_global = np.mean(np.array(remain_part_local), axis = 0)

        # for i in range(self.agent_number):
        #     for j in self.min_distance_list[i]:
        #         self.vp[i].append(self.viewport_pre[j])  #20,5,32
        #         self.bw[i].append(self.bandwidth_pre[j]) #20,5,1
        #         self.remain[i].append([self.remaining_part[j] / (visible_tiles[j] * rate + (self.total_tile_number - visible_tiles[j]) * self.video_size[0]) for rate in self.video_size])  #5,6

        #     self.vp[i].append(viewport_pre_global)
        #     self.bw[i].append(bandwidth_pre_global)
        #     self.remain[i].append(remain_part_global)


                # -----------concat-dont need ID-----------------
        # if self.concat:

        #     viewport_pre_global = np.mean(self.viewport_pre, axis = 0)
        #     bandwidth_pre_global = np.mean(self.bandwidth_pre, axis = 0)
        #     visible_tiles = [sum(self.viewport_pre[j]) for j in range(self.agent_number)]
        #     remain_part_local = [[self.remaining_part[i] / (visible_tiles[i] * rate + (self.total_tile_number - \
        #         visible_tiles[i]) * self.video_size[0]) for rate in self.video_size] for i in range(self.agent_number)]
        #     remain_part_global = np.mean(np.array(remain_part_local), axis = 0)


        #     for i in range(self.agent_number):
        #         for k, j in enumerate(self.min_distance_list[i]):
        #             self.view[i][k][:self.total_tile_number] = self.viewport_pre[j]
        #             self.view[i][k][self.total_tile_number] = self.bandwidth_pre[j]
        #             self.view[i][k][self.total_tile_number+1:] = remain_part_local[j]
        #             # self.vp[i].append(self.viewport_pre[j])  #20,5,32
        #             # self.bw[i].append(self.bandwidth_pre[j]) #20,5,1
        #             # self.remain[i].append([self.remaining_part[j] / (visible_tiles[j] * rate + (self.total_tile_number - visible_tiles[j]) * self.video_size[0]) for rate in self.video_size])  #5,6

        #         self.view[i][self.nearest_k][:self.total_tile_number] = viewport_pre_global
        #         self.view[i][self.nearest_k][self.total_tile_number] = bandwidth_pre_global
        #         self.view[i][self.nearest_k][self.total_tile_number+1:] = remain_part_global

        #         # self.feature[i][:6] = self.id[i]
        #         self.feature[i][:self.video_size_level] = self.action_one_hot[int(self.action[i])]
        #         self.feature[i][self.video_size_level] = self.reward[i]
        #         self.feature[i][self.video_size_level + 1: self.video_size_level + 1 +self.total_tile_number] = self.viewport_pre[i]
        #         self.feature[i][self.video_size_level + 1 +self.total_tile_number] = self.bandwidth_pre[i]
        #         self.feature[i][self.video_size_level + 2 +self.total_tile_number] = self.remaining_part[i]

        # -----------concat-viewpoint-----------------
        # if self.concat:

        #     self.total_view_dim = 2 + 1 + self.video_size_level
        #     self.total_feature_dim = 6 + self.video_size_level + 1 + 2 + 1 + self.video_size_level


        #     viewpoint_pre_global = np.mean(self.viewpoint_pre, axis = 0)
        #     bandwidth_pre_global = np.mean(self.bandwidth_pre, axis = 0)
        #     visible_tiles = [sum(self.viewport_pre[j]) for j in range(self.agent_number)]
        #     remain_part_local = [[self.remaining_part[i] / (visible_tiles[i] * rate + (self.total_tile_number - \
        #         visible_tiles[i]) * self.video_size[0]) for rate in self.video_size] for i in range(self.agent_number)]
        #     remain_part_global = np.mean(np.array(remain_part_local), axis = 0)


        #     for i in range(self.agent_number):
        #         for k, j in enumerate(self.min_distance_list[i]):
        #             self.view[i][k][0] = self.viewpoint_pre[j][0] / (2 * math.pi)
        #             self.view[i][k][1] = self.viewpoint_pre[j][0] / (math.pi)

        #             self.view[i][k][2] = self.bandwidth_pre[j]
        #             self.view[i][k][3:] = remain_part_local[j]
        #             # self.vp[i].append(self.viewport_pre[j])  #20,5,32
        #             # self.bw[i].append(self.bandwidth_pre[j]) #20,5,1
        #             # self.remain[i].append([self.remaining_part[j] / (visible_tiles[j] * rate + (self.total_tile_number - visible_tiles[j]) * self.video_size[0]) for rate in self.video_size])  #5,6

        #         self.view[i][self.nearest_k][0] = viewpoint_pre_global[0] / (2 * math.pi)
        #         self.view[i][self.nearest_k][1] = viewpoint_pre_global[0] / (math.pi)

        #         self.view[i][self.nearest_k][2] = bandwidth_pre_global
        #         self.view[i][self.nearest_k][3:] = remain_part_global

        #         # self.feature[i][:6] = self.id[i]
        #         self.feature[i][:self.video_size_level] = self.action_one_hot[int(self.action[i])]
        #         self.feature[i][self.video_size_level] = self.reward[i]
        #         self.feature[i][self.video_size_level + 1: self.video_size_level + 1 + 2] = self.viewpoint_pre[i]
        #         self.feature[i][self.video_size_level + 1 + 2] = self.bandwidth_pre[i]
        #         self.feature[i][self.video_size_level + 2 + 2] = self.remaining_part[i]

        #------------global-----------------------
        # vp_space = (2, self.total_tile_number)  #(2,32)
        # bw_space = (2,)  #(2,) 
        # remain_space = (2, self.video_size_level) #(2,5)

        #------------global-last-viewport----------------------
        # vp_space = (3, self.total_tile_number)  #(2,32)
        # bw_space = (3,)  #(2,) 
        # remain_space = (2, self.video_size_level) #(2,5)


        # -----------near------------------
        # vp_space = (2, self.total_tile_number)  #(2,32)
        # bw_space = (2,)  #(2,) 
        # remain_space = (2, self.video_size_level) #(2,5)

        # #------------global-near-----------------------
        # vp_space = (3, self.total_tile_number)  #(2,32)
        # bw_space = (3,)  #(2,) 
        # remain_space = (3, self.video_size_level) #(2,5)

        # # #------------ near specific-----------------------
        # vp_space = (self.nearest_k, self.total_tile_number)  #(2,32)
        # bw_space = (self.nearest_k,)  #(2,) 
        # remain_space = (self.nearest_k, self.video_size_level) #(2,5)

        # # #------------ near specific global-----------------------
        # vp_space = (self.nearest_k + 1, self.total_tile_number)  #(2,32)
        # bw_space = (self.nearest_k + 1,)  #(2,) 
        # remain_space = (self.nearest_k + 1, self.video_size_level) #(2,5)


                # ----------bitrate-------------------
                # if not erp:
                #     total_viewport_size = 0
                #     for tile in range(self.total_tile_number):
                #         if self.viewport[i][tile] == 1 and self.viewport_pre[i][tile] == 1:
                #             total_viewport_size += self.video_size[action[i]]
                #         elif self.viewport[i][tile] == 1 and self.viewport_pre[i][tile] == 0:
                #             total_viewport_size += self.video_size[0]
                #         if self.viewport_pre[i][tile] == 1:
                #             tile_download_times[tile][action[i]] += 1
                #         else:
                #             tile_download_times[tile][0] += 1
                #     # reward_qoe[i] = total_viewport_size / real_visible_tile_number[i]
                #     reward_qoe[i] = total_viewport_size
                #     # reward_qoe[i] = total_viewport_size / 4  #byx-add
                # ----------bitrate-------------------
