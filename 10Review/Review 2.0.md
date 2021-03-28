# Review 2.0
|                             论文                             |   Fov预测方法    |       Caching Policy        |                        其他输入参数                         |
| :----------------------------------------------------------: | :--------------: | :-------------------------: | :---------------------------------------------------------: |
| [基于视图合成的360°VR缓存C-RAN系统](http://www.eng.auburn.edu/~szm0001/papers/TCSVT-19-final.pdf) |      莫得)       |    LFU + MaxMinDistance     |     Drcache(下载所需数据的造成的延迟)<br/>Popularity 等     |
| [Long term Fov Predi..](https://ieeexplore.ieee.org/document/8695336) |   convLSTM+FCN   |           莫得）            |                                                             |
|                         003（直播）                          |  （和命名法结合  |      Hot + Popularity       |                                                             |
|                             005                              |    还没看完）    |                             |                                                             |
|                        Flock - based                         | 加权计算概率矩阵 |         分组 + LRU          |                    Fov预测：头部轨迹数据                    |
|                          Fov-aware                           |      没说）      | 计算可能以q质量被请求的概率 | 视频块i在common-Fov中出现的概率<br/>高质量请求视频块i的概率 |
|                       SVC-Edge caching                       |   好像也没说）   |       计算cache value       |           Popularity，size，clock，isinfov，level           |
|                                                              |                  |                             |                                                             |

## 一、Caching Replace Policy

### 1、MaxMinDistance

计算D和N的例子：001 P7

![image-20210322181414063](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210322181414063.png)

D越小N越小则更佳

### 2、计算Cache 概率

输入参数：

- 视频块i在common-Fov中出现的概率
- 用户请求视频块i为高质量的概率

得到此视频块将来要被以q的质量请求的概率05

### 3、式子计算cache value



### 4、其他用于比较的算法：

| 名字 / 论文 |             指标             |       参数       |
| :---------: | :--------------------------: | :--------------: |
|     LRU     | 访问越久远越不容易被再次访问 | 最近一次访问时间 |
|     LFU     |    被访问次数最少的先淘汰    |     访问频率     |
| KP-Optimal  |    预先了解所有用户的请求    |                  |
|   VS-RDM    |      randomly /手动狗头      |                  |
|   VS-LFU    |       LFU结合tile合成        |                  |
|    ENEV     | 基于马尔科夫决策的启发式方法 |                  |
|             |                              |                  |
|             |                              |                  |

### 5、用到的评测指标：

- *Tile hit* (缓存命中率)
- *Bandwidth saving*
- *Reb*(缓冲频率)
- *DoR* [延迟时间(以秒为单位)]
- Qua[高质量的FoV(以百分比表示)]
-  byte hit ratio
-  average access latency ratio
- impact of the cache storage(稳定性)

## 二、Fov Prediction

### 预测方法：

- trajectory based

- content based

|                方法                 | 具体内容                                                     | 缺点                                                         |
| :---------------------------------: | ------------------------------------------------------------ | ------------------------------------------------------------ |
| linear regression<br/>+ 3 layer MLP |                                                              | only 100 *∼* 500 ms                                          |
|    a fixation prediction network    | 考虑视频内容和视场位置                                       |                                                              |
|                LSTM                 |                                                              | 只做提前1s的预测<br/>只有过去输入数据类型和数据分布与未来相同的情况下才合适 |
|          深度学习强化模型           | 离线通过视觉特征得到热图<br/>在线通过过去轨迹预测            |                                                              |
|              KNN + LR               | 考虑了cross-users而不仅仅是target user                       |                                                              |
|            DBSCAN + SVM             | 服务器：密度的聚类将用户分组<br/>客户端：SVM预测是哪一类后进而得到查看概率 |                                                              |
|          MLP mixing + AME           | 针对第1，3的改进：神经机器翻译体系seq2seq model<br/>         |                                                              |
|             Flock-based             | 矩阵加权计算                                                 | 没确定最开始看啥视频片段吧                                   |

### 结果参数：

- **Hit rate.** 
- **Mean Squared Error.** 
- **Tile overlapping ratio**.
- **FoV center estimation from the predicted heatmap**（从预测的热图中确定平均位置，进而计算hit rate 和 MSE
- QoE Metrics 计算了预测的注意分布与真实注意分布之间的KL散度The effective rate，The duration of video freeze

## 三、结果变量

1. Average cache hit rate
2. Backhaul traffic load
3. Average latency [ms]
4. Quality-of-experience (QoE)（Average video quality， Average quality variations (*V*)，Rebuffer time (*T* )， Startup delay ）

## 四、不同

003 - P5



view port

