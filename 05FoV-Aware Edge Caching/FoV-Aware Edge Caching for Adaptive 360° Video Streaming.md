[TOC]
# **FoV-Aware Edge Caching for Adaptive 360**° **Video Streaming**

## Part One ：Background

### （0）解决目标

- 减少宽带消耗
- 解决网络延迟

### （1）现有解决方法

现有**减少宽带消耗**的方法（FoV-adaptive 360◦视频流）具体为：

- 用户视角FOV内发送高分辨率的贴图
- 其他贴图发送低分辨率或不发送

但是没有解决**网络延迟**

### （2）关键思路

缓存**靠近**终端用户的**流行内容**(Caching popular content close to the end users)可以同时解决网络延迟和宽带需求。

- 靠近：启用**基站**作为缓存模块来实现(BSs)位于RAN(无线接入网)边缘。

- 流行内容：预测下一次的Fov，**提高命中率**

### （3）解决方法

有两个方法：

- 缓存全部视频（无论是否在视角内）的所有分辨率视频

- 只缓存高分辨率视频 ，同时应用高转低的编码方法（但是对缓存服务器的要求过高，可能导致计算资源的浪费）

因此，缓存基于贴图的360视频的挑战是

- (i)如何用适当分辨率的贴图填充有限大小的缓存，以及
- (ii)当缓存容量超过时，将**哪些贴图从缓存中驱逐出来**，以便为新的贴图留出空间。

一种新的**基于用户视场**的缓存策略，**视场感知缓存策略**。在视场感知的缓存策略中，我们根据以前的用户浏览历史来学习每个360视频的共同视场的**概率模型**，以提高缓存性能。

大致内容：

1. FoV-aware caching policy：**a probabilistic model** based on previous users’ **watching histories** 来确定当缓存容量超过时，缓存模块应用这些知识来确定清除块的优先级。

2. 我们采用众所周知的缓存策略，如最近最少使用(LRU)和最不经常使用(LFU)，以瓷砖为基础的360◦视频流，并**分析这些策略的性能**。

3. 我们利用真实用户头部运动数据集和真实4G蜂窝网络带宽跟踪来评估FoV-aware缓存策略。


### （4）实验结果

与两种缓存策略：最少使用次数(LFU) 和 最少最近使用次数(LRU)相比，我们提出的方法提高了**缓存命中率**分别至少增加40%和17%。

## Part Two: System architecture（整体系统架构）

### （1）Network Model

在用户和服务器之间添加代理缓存 --> 减少发送到远程内容服务器的请求数量 & 减少服务器的负载  --> 利用CDN服务中的缓存结构

一个离用户很近的基站，存储空间有限，需要一个**缓存替换策略**

- 如果缓存有请求的内容，直接调用；

- 如果没有缓存，先从CDN上调用下载，然后再给客户端。（增加延迟 & 带宽消耗）

因此需要提高命中率。

### （2）**360**◦ **Video Model**

#### 目标：

满足当前网络吞吐量的情况下，为用户实际的FoV内提供尽可能高的质量。

#### 实验假设 ：

- pre-recorded （预录）
- all videos have the same duration（相同延续时间）

#### 实验变量：

- S：一段视频含有的片段数量（每段固定时长的回放时间为1秒）

- N：每秒的帧数（这里固定为30）

  这里每帧是一个等矩形表示的球面视图

- T：矩形平面被分成的块数

- Q：分辨率种类

- MPD：（明确下一段放啥）

- FoV （固定设为100◦ × 100◦ ）

#### 1. FoV Prediction（对下一个视角的估算）

- 每100ms提取一次样本
- 每次选择10个最近的Fov样本作为输入
- 加权线性回归
- 同时得到是否判断正确的flag

#### 2. *Network Throughput Estimation*（网络吞吐量估计）

两种对于网络的模式：

- Fov内用高分辨率，其他用低分辨率（网络良好）

- 对所有的分块都请求低分辨率。（网络堵塞）

我们要计算的吞吐量为K，吞吐量样本为SS：

【吞吐量样本SS】对于一个视频片段（有t个视频块）来说的：

【吞吐量样本SS】 = （所有t个视频块的大小和）/ （下载所有的视频块的时间和）

网络吞吐量样本K = 最近3个SS / 3 --》 确定预测的Fov是否可以采用高质量

R_h : 整体高分辨率，R_l : 整体低分辨率，f是Fov包含的视频块

吞吐量大于R_h * f/t + R_l * (t-f)/t 即可。

【【【【Latex语法待补充】

## Part Three: proposed method

> 我们通过对Fov和视频比特率的研究，得到最终的FoV-aware缓存策略

### （1） **Users’ FoV Pattern**

已知：用户的Fov和内容关系极大，赛车--》正前方，观光游览--》360°

收集真实轨迹的头部跟踪数据集，并显示用户在虚拟环境有某些类似的观看模式时

数据集：10短视频，每段50人观看，计算**FOV的热力图**。

![image-20210120161455103](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210120161455103.png)

第一种：自然现象，快节奏，跳水

第二种：自然现象，慢速，吃豆豆

第三种：电脑生成的快节奏

大多数用户集中在红色区域，common-Fov --》大家普遍看的内容范围

### （2） **Impact of Video’s Bitrate on FoV’s Quality**（比特率对质量的影响）

视频由比特率编码《-- 取决于视频内容的纹理和运动《--场景越复杂，需要更高的比特率来维持相同水平。

#### 比特率的计算

R_high:表示高质量视频块的比特率， R_low:表示低质量视频块的比特率

Fov设为100 * 100，则Fov的占比为100/180  *  100/360 = 14%。

Effective Bitrate网络良好时：0.14 * R_high+ 0.86 * R_low

All low 网络堵塞时：1 * R_low

#### 实验

实验目的：了解不同的360◦视频比特率对接收FoV质量的影响

实验条件：相同网络条件下，10个有不同比特率的视频 (网络条件： link capacity is 1 Gbps, latency (round-trip time) and packet loss are 10 ms and 0.01)

实验过程：以两种方式（Ef & All_low）看10种不同比特率的视频。

实验结论：

![image-20210120214826717](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210120214826717.png)

看懂了，等等细说。

### （3）**FoV-aware Caching Policy**

两个参数确定是否应该剔除：

- 进入common - Fov  的概率
- 用户要求每个视频在Fov中使用贴图的概率

#### *Learning Parameters*

- 参数Q_vsi : 视频块i在common-Fov中出现的概率

  训练数据：对于第i块的请求（信息为：第i块是否在请求的Fov中）

- 参数F_i：用户请求高质量视频块的概率

  训练数据：对于Fov中第i块的请求（信息为：是否需要高质量）

模型的选择：

- 因为都分别**只有一个变量影响**，选择**朴素贝叶斯算法**来构造每个参数的概率模型。
- 最大似然估计（MLE），使得Q_vsi和F_i最接近数据集中两者的公式。

<img src="https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210120225322570.png" alt="image-20210120225322570" style="zoom:67%;" />

**其中：α**inFoV_v,s,i和**α**outFoV_v,s,i分别是第i块被请求在Fov中和不在Fov中的次数。**β**high_v和 **β**low_v分别为Fov中的视频块V被请求为高质量和低质量的次数。

为了使得上述方程最大化（Max），我们对方程求导：以第一个方程为例

<img src="https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210120230229162.png" alt="image-20210120230229162" style="zoom:67%;" />

最终得到了两个参数的模型：

![image-20210120230259774](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210120230259774.png)

 #### *Caching Policy.* 

下面我们的目标就是最终如何建立缓存算法（策略）——FoV-aware caching policy

该算法描述了缓存模块在接收到对质量为q的视频v的段s的平铺数i的请求时所采取的动作。

![image-20210120215141858](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210120215141858.png)

解释：

*update_parameters*  ： 学习更新Q和F得到R（第i视频块在将来被以q的质量请求的概率）

*cache.contains*：查看缓存中是否已经缓存，如果已经缓存则调用

*cache.download* ：如果没缓存则下载，并*cache.add*进缓存空间中。

*cache.remove_min* ：如果缓存空间满了，就remove掉R最小的。

【待补充：以流程图画upon_parameters】

![image-20210120232107033](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210120232107033.png)



那如何计算得到R呢，

- 对于低质量版本的视频块有两种可能被请求：
  1. 不在Fov内
  2. 在Fov内但是用户请求为低质量
- 对于高质量的视频块请求只有一种可能：在Fov内且高质量请求。

![image-20210120232043852](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210120232043852.png)

因此我们可以通过以下的update_parameters函数得到R：

![image-20210120232523818](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210120232523818.png)

这样我们就用上述的方法进行模拟缓存的过程了。

## Part Four: experiment setup

> Mahimahi LinkShell来模拟移动网络的行为

### 不同的网络状况：

![image-20210120233620446](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210120233620446.png)

### 不同的缓存存储容量：

- 0.25的视频（0.61GB）
- 0.50的视频（1.22GB）

### 不同的全景视频

假设创建会话的频率为平均30s一次

数据集：

- 10个不同内容的全景视频，每个视频50用户观看，这样可以得到500个运动轨迹。
- 对于每个视频段（矩形）分成24（6×4）块，且每块有两种像素640 × 540 and 320 × 270 也就是对于整个矩形来说：3840×2160 and 1920 × 1080
- 我们规定编码的速率因子（CRF）为21，高质量比特率为3Mbps,低分辨率为1Mbps

### 视频分段：

使用GPAC MP4Box工具将每个视频分成1秒的片段。

这样一个片段的每个平铺都可以单独使用。

最终所有贴图：高质量26.3Mbps,低质量8.7Mbps

## Part Five: experimental results

我们将我们的研究成果和现有的3种做对比：

- *end-to-end*: 客户端和服务器间无缓存（炮灰）
- *LFU*: 在LFU缓存策略中，我们保留了贴图的频率信息，当缓存已满时，访问频率最低的贴图将被从缓存中删除，以便为新贴图腾出空间。
- *LRU*:在LRU的缓存策略中，当缓存被填满时，我们删除从最后一次访问以来持续时间最长的贴图，为新贴图留出空间。

验证策略优良的指标：

- *Tile hit* (缓存命中率):请求的贴图在缓存中找到的比例。
- *Bandwidth saving*[带宽节省(以百分比表示)]:当客户端请求命中缓存时，所节省的带宽超过所有请求的总带宽消耗。
- *Reb*(缓冲频率)：没有任何视频可以播放了
- *DoR* [延迟时间(以秒为单位)]:该指标显示客户端经历延迟的总持续时间。
- Qua[高质量的FoV(以百分比表示)]:客户端接收瓷砖内FoV高质量超过360视频的总段数的片段数。

### （1）Caching Policy Performance

性能指标：*Tile hit* + *Bandwidth saving*

- 较高的缓存命中率减少了对内容服务器的请求数量，从而节省了核心网络中的带宽。

Tile hit:

![image-20210121000732440](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210121000732440.png)

Bandwidth saving:

![image-20210121000746695](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210121000746695.png)

最好的缓存策略：**删除将来被请求的可能性最小的块**。

FoV-aware缓存策略利用常见的fov现象(即，观看同一视频的大多数用户的fov有显著的重叠)来驱动对未来请求贴图的更好预测。

【【【【这里还有一段分析要看

### （2）Streaming Performance

性能指标：Reb，Dor，Qua

### （3） Impact of Cache Capacity

研究缓存容量对所有三种缓存策略的影响，

所有的策略性能都随着缓存容量的减小而降低。

对于命中率，Fov - aware的策略比另外两种降低的都小

![image-20210121001827481](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210121001827481.png)

同时对于Bandwidth saving来说，也是Fov策略性能下降的更小。

![image-20210121001926824](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210121001926824.png)

## Part Six: Related works（不是这次重点，再说吧）

*Overview of 360*◦ *video streaming*

这里用的等直角投影，采用了自适应流的平铺方法和视场预测方法。结果表明，线性回归方法可以预测用户未来的FoV最多2秒，从而可以预取相关的FoV贴图，实现流畅的视频播放

对于每个分块采用Scalable Video Coding (SVC)

另外，为了解决用户侧多解码器对每个贴图进行解码的问题，[33]采用了高效视频编码(HEVC)标准中运动约束贴图集(MCTS)的特性，采用了单一的硬件解码器。

*Edge computing and caching:

总结：

在移动网络边缘缓存内容可以掩盖流行项目重复下载的缺点，减少长网络延迟和带宽消耗。将所有这些优点结合起来，缓存可以改善360视频流，特别是在移动网络等动态网络条件下。在本文中，我们提出了一种基于平铺的自适应360视频流的缓存策略，通过识别共同视场并利用这一知识来实现更好的缓存性能。结果表明，与LRU和LFU相比，该方案不仅在缓存命中率和带宽节省方面具有优势，而且通过减少延迟事件的数量和持续时间提高了QoE，为FoV提供了高质量。