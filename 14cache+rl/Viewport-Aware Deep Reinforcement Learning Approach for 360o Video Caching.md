# Viewport-Aware Deep Reinforcement Learning Approach for 360° Video Caching

online caching scheme

提出virtual viewport的概念： A virtual viewport has the same number of tiles with regular viewports, but it consists of the most popular ones.

目的：we first formulate the problem of 360*o* video caching as a Markov Decision Process (MDP). The aim is to find the optimal set of 360*o* videos and virtual viewports that should be cached at the SBS, so that the overall quality delivered to the users is maximized

## 1、整体思路

LSR 算法

MDP ： The aim is to find the optimal set of 360*o* videos and virtual

viewports that should be cached at the SBS 

用DQN 来更新策略函数

RL：优化内容缓存位置

两种情况：

1. 如果不是以basic质量请求的，会直接传给用户，但是如果他的popularity不够大则不会缓存进入cache中。
2. 如果是以basic请求的，在预测vp中的tile会以高质量被cache。

两点：

1. 从原站获取的是否缓存
2. tile的popularity

## 2、vp prediction

Last Sample Replication（LSR）算法

假设新的chunk的vp和上一个一样。

## 3、Which tile to cache

第一个请求w0将G个GOP都请求了（base quality），后面的请求是第i个GOP的vp中请求高质量。

Agent：SBSs

State：由Features组成，每个状态的特征都是从用户过去请求的观察中提取出来的

Features：

1. 和用户请求次数有关系：

   两个向量，分别表示长短请求，每个向量的元素表示为：第i个位置的缓存的视频被请求的总次数。
   $$
   \mathbf{x}^{n}=\left[\mathbf{x}_{s}^{n} \mathbf{x}_{l}^{n}\right]
   $$
   
2. 对应于缓存的360度视频的高质量tiles的请求总数，表示在第n个SBS上请求第i个缓存的360度视频的第j个（高质量）贴图的次数。

3. 当examined item是base quality：表示第n个SBS这个视频被请求的总次数。high quality：表示这个examined item被请求的总次数

Actions：

当收到用户的request时，3种可能:

1. 请求的视频没用被缓存
2. 请求的视频都是base quality，vp中的high quality
3. 请求的视频都是base quality，不同的vp中的high quality

当请求的video没有被cache，2种action：

1. 缓存空间内容不变
2. 替换

用C+1长度的列表表示A1

当请求的视频的vp中的tile被以高质量请求了 no action。

当视频以base quality被缓存，不同的vp中的high quality，2种action：

1. 不替换
2. 将新从源站带来的tile缓存

Viewport有k个tiles，用一个k长度的列表表示A2

Rewards：在H次请求后统计能将tile传送到达的次数和
$$
r(s, a)=\frac{1}{H} \sum_{h \in \mathcal{H}} \sum_{v \in \mathcal{V}} \sum_{g \in \mathcal{G}} \sum_{l \in \mathcal{L}} \sum_{m \in \mathcal{M}} \mathbb{1}\left(\phi_{h, v, g, l, m}\right) \cdot \delta_{v, g, l, m}
$$


base + 视野内：no action，接下来判断是否缓存下一个chunk中预测的vp中的tile

DQN：优化缓存

## 4、tiles' popularity

The DRL framework consists of two phases:

a) the offline phase where the DNN is trained

b) the online phase during which the actual caching decisions are made.

一个DNN：在state-action种做最优决策

第二个DNN：固定目标网络，用于函数逼近

最小单元the candidate item (360*o* video in base quality or tile in high quality)

