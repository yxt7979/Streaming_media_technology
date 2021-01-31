# Rldish: Edge-Assisted QoE Optimization of HTTP Live Streaming with Reinforcement Learning

目的：通过RL的Rldish方案，为一个新加入的用户选择合适的视频段，且部署在边缘CDN服务器上。
## 1、介绍
### 问题：

现有的IVS选择有两种：固定值 ， 最优值

固定值：不适合动态的网络条件和高质量的视频流

最优值：两个缺陷

- 依赖于网络吞吐量的估计（与多个因素有关），用户多时，计算开销大。
- 用户新加入的时候只能通过信号强弱和移动模式估算网络吞吐量，不准确

### 思路：

在探索次优决策和利用当前最佳决策之间保持平衡。

- exploration and exploitation (E2) model
- 和Nginx等协作工作
- 对网络状况的改变做出反映

因为发现：访问同一段直播视频的观看者，通常共享同一段视频从源服务器到边缘的传输路径，从边缘获取同一段视频时一般会经历类似的网络状况

Rldish基于实时的QoE测量和反馈，不断更新当前最优的IVS选择，供直播观众在逐流的基础上进行选择。再将决策结果更新到文件中。

### 挑战：

1. QoE对RL有很大影响，相同的IVS有时可能会错过边缘缓存，但在其他时候会击中缓存。

   解决：我们通过考虑每个直播流在边缘服务器上的实时缓存状态，定义了一个新的RL选择坐标系统
   
2. 难以在边缘进行实时的QoE测量，因为QoE数据在客户端收集

   解决：我们深入Nginx内核，并做一些修改来收集TCP和HTTP性能数据
   (例如，HTTP响应时间和RTT)，从而进一步生成QoE数据

3. 难以均衡不同的QoE评测指标

   解决：自行改变α ， β ，δ 。

![image-20210131122221024](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210131122221024.png)

## 2、Rldish总览

![image-20210131124632625](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210131124632625.png)



### 1) *QoE Collector*

它与(HTTP)代理服务器实时通信，收集实时观看者的QoE数据(如启动延迟，视频缓冲时间)。

### 2) *RL based IVS Selector*

接受QoE采集器反馈的奖励反馈的最新数据，通过运行强化学习算法，不断更新每个直播流最新的IVS选择。

### 3) *Playlist Manager*

它周期性地向源服务器发送请求，以获取当前由本地用户访问的实时流的最新播放列表文件。它使用新的IVS(来自RL)来更新原始的播放列表文件，从而在本地缓存中维护所有实时流的播放列表文件。

更新Playlist：

1. RL模块提供了一个新的选择(不同于以前的一个)的IVS的直播流
2. 从源服务器获得具有新片段描述的新播放列表文件
3. 实时流的新片段缓存在边缘服务器中

当用户加入活动通道时，代理服务器将用户的播放列表文件的第一个请求定位到本地边缘缓存。通过从请求URI中识别所请求的通道ID和比特率信息，就可以从playlist管理器中获得所请求流的相应播放列表文件。一旦第一个请求的播放列表文件成功地交付给客户端，对播放列表文件的后续请求将由代理服务器独立处理:它将最新的未修改的播放列表文件返回给客户端。在实践中，HTTP代理服务器有很多方法来区分播放列表请求是否来自新客户端，以便采取不同的响应决策。最简单的方法之一是使用HTTP Cookie来指示连接的状态信息。（HLS）

## 3、RL算法

### 前置知识：强化学习概念，开发 PK 试探，Greedy

### *D-UCB*(探索未知和已知之间达到平衡)   

[UCB讲解](https://leovan.me/cn/2020/05/multi-armed-bandit/)

D-UCB算法可以适应实时流媒体的QoE波动，因为它可以通过一个折扣因子对历史测量值进行指数折扣，自动为最近的测量值赋予更高的权重。

### “奖励”的定义：QoE收集了什么信息

- *General latency (gl)*：由于估计太保守
- *Startup latency (sl)*：边缘还没请求到请求的第一个视频段
- *Buffering time (bt)*：估算太积极

![image-20210131140403196](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210131140403196.png)

且α + β + δ = 1而且可变

### “Arm”的定义

我们通过考虑视频片段在**边缘缓存中的实时位置**来定义手臂，而不是它们在播放列表中的位置来定义arm

### 大致算法：每次选取X_t + C_t最高的

X_t : 开发的价值

![image-20210131154458811](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210131154458811.png)

C_t : 探索的价值（N ↑，C_t ↓）

![image-20210131154515407](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210131154515407.png)

为了改进计算效率：

![image-20210131173927741](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210131173927741.png)

## 4. 实验




