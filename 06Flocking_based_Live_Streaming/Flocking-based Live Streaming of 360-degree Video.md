[TOC]
# Flocking-based Live Streaming of 360-degree Video

## 1. 摘要

### （1）基本思路：“集群”

 the idea of “flocking”  --》

- 提高视场预测性能
- 在边缘服务器上缓存实时全景视频流

### （2）研究提出

a collaborative FoV prediction scheme--》利用群前用户的实际视场信息来预测群后用户的视场。

a network condition aware flocking strategy （一种网络条件感知的群集策略）--》减少视频冻结，增加所有用户的协同FoV预测机会。

facilitates caching --》前者缓存的可以留在边缘服务器中给后者使用

a latency-FoV based caching strategy（一种基于FOV的缓存策略）

applying transcoding on the  edge server（研究在边缘服务器上进行代码转换的潜在好处）

### （3）研究结果

评价的实验数据&环境：真实的用户Fov轨迹 & WiGig网络宽带跟踪

和只根据用户自身过去的Fov轨迹相比：

- 有效视频率提高一倍（有效：用户实际视野中的视频质量）
- 减少视频冻结时间
- 降低80%的核心网的流量（如果采用编码策略则可以降低更多）

## 2. 介绍

为了1. 减少延迟 2. 减低宽带需要：

- *Field-of-View (FoV) streaming*：stream the video only in predicted users' Fov（效果取决于预测用户视角的准确性）
- *content caching*

解释：

 “streaming flock” ： 在同一个本地网络看同一个直播视频的用户。

- in the front of a flock：有较短的回放延迟（作为预测的数据）
- behind .. :回放延迟较长

develop a novel light-weight FoV prediction algorithm，训练数据集为：

- 用户之前的运动轨迹
- 其他用户实际的轨迹

进一步研究当边缘服务器具有转码能力时对于宽带，计算，存储的影响

## 3. 近期工作（回顾）

### （1）**User FoV prediction**

对于3种类型的全景视频都很重要（VoD,live,interactive）：

- 线性回归 + DNN 实现基于用户历史轨迹的Fov预测
- 加上视频内容特征
- 长时间范围内的Fov预测（LSTM-based models）
- 自回归移动平均(ARMA)预测和转移概率模型
- 考虑物体运动速度，景深等
- collaborative FoV prediction（为Vod提出的，且假设有很多用户同时观看）

本算法：针对Live ，适应任何人数观看的场景，轻量级

### （2）**Live** 360◦ **video streaming**

- 已有360°视频QoE测量平台(video  bitrate, duration and the number of video freezes)
- 一个实时360◦流媒体系统（在质量和宽带消耗之间权衡）
- 编码效率因为live有极大的挑战

本算法：通过根据用户的网络条件，有意地分配不同的回放延迟，我们可以提高协同FoV预测的准确性，同时减少视频冻结的可能性。（这里延迟因为在10-30s内都很合适，因此可行）

### （3）**Edge caching**

- 基于内容和网络的二维5G缓存算法已经提出
- 编码的收益和延迟的权衡

本算法：我们考虑如何通过实时代码转换提高缓存性能，但代价是计算

## 4.  挑战和提出方案

### （1）Online User FoV Prediction

针对VoD：利用早期用户的Fov轨迹（尤其是峰值）来帮助预测未来用户的轨迹（但是需要一定量的用户，而Live的过去观看用户数量是动态的）

解决：a flocking-based real-time FoV information sharing strategy（自适应地结合用户自己过去的轨迹预测和用户群前的轨迹预测）

### （2）Temporal and Spatial Rate Adaptation（时间空间的速率适应）

视频的每一段会有质量的调整，而且为了应对用户视图方向的变化，在同一段内不同方向的速率分配必须被调整。

等矩形投影且每一块被编码成多种质量。（在预测的Fov内需要更高的质量，其余质量不需要太高），但是同时要考虑不同质量导致的边界衔接的问题

解决：基于总编码率计算，因为是帧级改变的，我们不预测方向，而是预测 *tile attention distribution*（注意力分布，即一个特定的贴图在一个片段的整个持续时间内进入用户视场的时间分数）在所有贴图上按比例分配某个部分的总比率预算。

### （3）Massive Concurrent Requests and Redundant Network Traffic（大量并发请求和冗余的网络流量）

- 每个用户的请求由不同质量的视频块组成
- 由于大量用户观看同一直播事件，网络上传输的大部分流量都是冗余的。

目标：服务突发请求和消除冗余视频流量

解决：利用缓存解决，且缓存每一块只需要持续较短的时间（最先和最后的延迟30s左右）我们将开发一种新颖的实时360◦视频贴图缓存算法，该算法考虑了群内用户的延迟传播和视场发散。

## 5. **FLOCKING-BASED LIVE** 360◦ VIDEO STREAMING（基于群集的全景视频流）

总体流程：

- 在回放过程中，每个用户将记录每个观看帧的FoV中心方向，并将历史FoV轨迹连同请求新贴图一起上传到视频服务器。
- 服务器将接收到的用户FoV信息存储到共享FoV表中。
- 用户可以下载共享的FoV信息和MPD (Media Presentation Description)文件。
- 由服务器维护的共享FoV表允许群集中的所有用户完全交换他们最新的FoV信息，这可以用来提高他们的FoV预测精度。

### （1） Collaborative FoV Prediction（协作Fov预测）

下图说明了如何通过flock前面用户的历史数据对后面观看的用户视角进行预测

![image-20210125190009836](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210125190009836.png)

- 此时：用户A在看第i+1段（有i+2在缓存中，且想去看第i+3段）

- 在向服务器发送缓存请求之前，首先预测出第i+3段的Fov中心C，预测的数据是他知道i+1段前几帧的之前的轨迹，用Kalman Filter（卡尔曼滤波器）过滤噪声后，带入Fov预测方法中（线性回归、递归最小二乘(RLS)和长期短期记忆(LSTM)。这里采用截断线性FoV预测方法[32]）

- 得到中心C后，我们利用 ERP投影，计算出每块贴图中有多少在预测Fov中（百分比）。（Fov中心的预测可以用片段每一帧的概率求平均值，或者直接预测，后期待探索）

  ![image-20210125182006344](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210125182006344.png)

- 上面是利用自身历史数据，我们同时利用已经观看过的真实用户数据进行预测，分别得到类似上面的概率矩阵，分别×相应的权重，

  ![image-20210125182552762](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210125182552762.png)

  得到一个基于真实数据的矩阵。

  ![image-20210125182229269](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210125182229269.png)

  其中权重W的计算和真实用户分别和待预测用户轨迹的相似度有关：如下图中d(1,2)比d(1,3)更小，因此权重W2更大。其中d定义为所有时间对准视场中心对的**平均大圆球距离**。

  ![image-20210125182415520](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210125182415520.png)
  
  
  
  下面的式子为通过d(1,n)计算对于n的**权重W**的方法：(这里的γ和Q是离线得到的最优值，分别为3和0.5)
  
  ![image-20210125182749136](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210125182749136.png)
  
  
  
  继而可以求出每个真实用户的占比也就是自身W / 全部真实用户的W和。
  
  ![image-20210125183305539](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210125183305539.png)
  
- 每当另一个用户看了第i+3段之后，我们通过和之前一样的方法，记录视频段F_i+3中每一帧f的概率矩阵M，再叠加后➗帧的总数得到最终的每个视频块的视场分布矩阵。

  ![image-20210125183932806](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210125183932806.png)

- 最后我们将用户自身预测的结果(^)和通过历史数据预测的结合起来成为最终的Fov预测值。
  ![image-20210125184456152](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210125184456152.png)
  
  这里的两个矩阵叠加，也分别有相应的权重：
  
  ![image-20210125184711180](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210125184711180.png)
  
  其中的α是以下的算式得出，我们可以发现当在此用户之前如果没有其他用户观看带预测视频的时候，α = 1，也不会影响整个算法的运行。
  
  ![image-20210125184802426](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210125184802426.png)

### （2） Network Aware Latency and Buffer Upper Bound Assignment（网络感知延迟和缓冲区上限分配）

> When birds fly in a flock, the birds in the front have to fight harder
> against headwind.

这部分我们需要确定让flock中的哪些用户在flock的较前面，（他们的概率矩阵不那么准确，因为在他们之前的数据非常少），哪些用户在flock的较后面。

![image-20210125192427783](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210125192427783.png)

这里的B_n 都需要小于G_n。

在t时刻时，如果延迟为l,那么用户当前看的为t-l时刻的视频，最大缓冲区的长度为B则用户应该下载[t-l,t-l+B]长度的视频，

- B越大时，基于自身的预测权重应该越小，
- l越大时，用户更可以利用延迟较短的协同预测的信息，也就是协同预测的权重更大。

因此，分配在front of the flock的用户应该网络和宽带较好，这样才不会由于缓冲不足使得出现断片。（不过好在由于他们需要的B不用太长，因此还是挺准确的）

而网络不通畅的用户要分布在 the back of the flock，因为他们的B需要较大。

这种协作群策略可以同时提高单个用户和整体用户的QoE。

### （3）Spatial and Temporal Rate Adaption（时空速率适应）

#### 1、宽带预测

在随后的仿真结果中，计算过去10个视频段下载带宽的谐波均值作为下一个视频段的预测带宽。

#### 2、时间适应速度

用户的QoE也会受到两个相邻视频段之间的速率波动的影响，需要对时间速率适应性进行优化。

- 模型预测控制(MPC)
- 强化学习(RL)
- 在目前的工作中，我们将基于一步带宽预测进行时间速率分配，并在未来的工作中探索不同时间速率自适应算法的潜在增益。

#### 3. 空间速度适应

由于每个360◦帧在空间上被划分为多个贴图，在有限的带宽预算下，分配给每个贴图多少带宽可能会导致不同的感知。

因此，可以通过基于位置相关质量率模型的费率优化配置来进一步提高配送质量。这是一个有待进一步研究的课题。

## 6. FLOCKING-BASED LIVE 360◦ VIDEO CACHING

### （1） Latency-FoV based Caching Strategy（基于延迟Fov的缓存策略）

基于延迟fov的缓存策略。根据**用户过去的视场轨迹相似度**，将用户分为不同的视场组。每个组中有最大延迟的用户(用户4和6)被标记，组中只有一个用户(用户1)也被标记。

![image-20210125201031721](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210125201031721.png)

### （2）Transcoding and Enhanced Transcoding at Edge Server（在边缘服务器中转码）

我们假设边缘服务器支持**实时视频转码**。例如，如果一个360◦视频视频块被请求，并且有一个相应的tile以更高码率存储在缓存中，边缘服务器可以操作**从高编码率到请求的编码率**的**实时转码**。这样可以节省在核心网络上传输的流量。

**增强代码转换(E-Transcoding)策略**：只要请求一个360度的视频贴图，这个贴图就会以最高编码率从原始服务器下载并缓存在边缘。然后边缘服务器将其转换为任何请求的较低速率。假设视频服务器和边缘缓存之间有充足的缓存存储和带宽，只要有一个视频段准备好，视频服务器就可以以最高的速率将所有贴图发送到边缘。在这种情况下，所有请求的贴图都将击中缓存。 (U-Transcoding)【这是一种极限的理想情况】

## 7.  PERFORMANCE EVALUATION（性能评估）

### （1）实验平台
- 9视频48用户的轨迹
- WiGig模拟网络状况
- HMM合成带宽轨迹（page8)
- 码率选择（？
- 预测带宽 ：计算过去10个视频段下载带宽的谐波均值作为下一个视频段的预测带宽。


### （2）Evaluation of Flocking-based Live 360◦ Video Streaming

#### 1、 *QoE Metrics.*

计算了预测的注意分布与真实注意分布之间的KL散度

- The effective rate
- The duration of video freeze

#### 2、*Gain from Collaborative FoV Prediction.*

![image-20210127001435259](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210127001435259.png)

我们根据用户的网络环境分成几段，第一梯队的属于in the front of flock因此含有的协作预测信息太少，所以橙色条没有后面明显。

但是可以发现，加上了协同预测后的所有KL散度都减小甚多，说明协同预测非常有效。

#### 3、*Gain from Latency and Buffer Upper Bound Assignment*

![image-20210127002428738](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210127002428738.png)

上面的4张图中，左面两个是随机分配所在flock区域的，右面两个是根据计算得到的最优所在位置。

灰色线是有效带宽，(a),(b)图中的绿色线(交付视频比特率)大致相同，但是橙色线(有效视频比特率)明显(b)比(a)强。

因为有效视频和对Fov的预测有关，因此右面的计算后的智能分配会使得他有更多的协作用户数据，因此(d)比(c)的KL散度更准确些，于是Eeffective Rates 也就更高。

### （3）Caching Performance for Live 360◦ Video Streamin
#### 对于无限制的缓存容量 -- 编码的影响
- cache hit rate
- network efficiency
- transcoding ratio
- the storage requirement

#### 对于不同容量下的缓存性能
![image-20210127164342565](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210127164342565.png)
当容量达到15G左右时基本到达峰值，可以覆盖48s的内容。
Network Efficiency ： A-B/B
A：用户请求的 
B：从原始服务器传送到缓存的总流量











