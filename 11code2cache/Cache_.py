# 进来一个请求，lookup（）查找cache中有没有，没有就向Server侧请求，然后将它发到客户端并存到cache上，
# 这个时候会进入admit（），判断是否要存这个chunk，如果要存，cache没满就跳过，满了就进入evict（），进行替换策略
import time
import math

all = {}
# video时长
video = [0,100,100,100,100,100]
# 每个segment的秒数
segment_time = 2
dk = 5000
# # 几种quality的比特率
# B = [30,50]
# 每个video的segment数量
segment_nums = [0,0,0,0,0,0]
cnt = 0
for i in video:
    segment_nums[cnt] = math.ceil(i / segment_time)
    print(segment_nums[cnt])
    cnt += 1

# tile数量的前缀和
all_tile_nums = [0,0,0,0,0,0]
for i in range(len(segment_nums)):
    all_tile_nums[i] = segment_nums[i] * 24
    if i > 0:
        all_tile_nums[i] = all_tile_nums[i] + all_tile_nums[i-1]
        print(all_tile_nums[i])

class Chunk(object):
    def __init__(self, start_time, video_id, tile_id, bitrate, quality, level):
        self.start_time = start_time
        self.video_id = video_id
        self.tile_id = tile_id
        self.quality = quality
        self.level = level
        self.bitrate = bitrate
        self.get_seg_id()
        self.get_exac_id()
        self.get_size()
        # self.idname
        all[self.exacid] = self
        print('请求的这个Chunk的video——id:',self.video_id,'seg_id:',self.segment_id,'tile_id',self.tile_id,'exactid:',self.exacid)

    def get_exac_id( self ):
        self.exacid = all_tile_nums[self.video_id - 1] + (self.segment_id - 1) * 24 + self.tile_id

    def get_seg_id( self ):
        self.segment_id = math.floor(self.start_time / segment_time)

    def get_size( self ):
        self.size = self.bitrate * segment_time


class Cache:
    def __init__(self, capacity = 100):
        self.capacity = capacity
        self.have = {}
        self.size = 0
    # tile 是否在缓存中(T/F)
    def lookup(self, Chunk):
        return Chunk.exacid in self.have.keys()

    # 目前缓存的所有cache
    def size(self):
        return self.capacity

    def call( self , Chunk):
        time = Chunk.size / dk
        print('cache到server的延迟：',time,'s')
        print('从Server中请求',Chunk.exacid)

    # 从server请求加入到缓存中
    def add_from_server(self, Chunk):
        self.call(Chunk)
        self.have[Chunk.exacid] = 1
        self.size = self.size + Chunk.size

    # 发送缓存
    def send(self, Chunk):
        print('向用户发送',Chunk.exacid)
        pass

    def admit( self ):
        if self.size > self.capacity:
            self.evict()

    def evict( self ):
        while self.size > self.capacity:
            # 添加上要用的算法
            for keys in self.have.keys():
                self.size -= all[keys].size
                self.have.pop(keys)
                break

    def request( self , Chunk):
        if self.lookup(Chunk):
            self.have[Chunk.exacid] += 1
            self.send(Chunk)
        else:
            self.add_from_server(Chunk)
            self.send(Chunk)
            self.admit()

class LRUCache(Cache):
    def __init__ ( self ):
        Cache.__init__(self)

    def evict ( self ):
        while self.size > self.capacity:
            d_order = sorted(self.have.items(), key=lambda x: x[1], reverse=False)
            # 删除排序后的第一个
            det_id = d_order[0][0]
            self.have.pop(det_id)
            print('删除',det_id,'的Chunk')
            self.size -= all[det_id].size

my_cache = LRUCache()
chunks = [Chunk(10,2,3,1,1,1),Chunk(5,2,3,1,0,1),Chunk(10,2,3,1,1,1),Chunk(10,2,3,1,1,1),Chunk(10,3,3,1,0,1),Chunk(10,3,3,1,0,1),Chunk(10,3,3,1,0,1)]
if __name__ == '__main__':
    for i in [0,1,2,3,4,5,6]:
        c = chunks[i]
        my_cache.request(c)
        for key, value in my_cache.have.items():
            print('{key}: {value}'.format(key=key, value=value))
        print('--------------------------------', my_cache.size)


