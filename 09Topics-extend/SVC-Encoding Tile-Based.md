# 《Edge Cache Replacement Strategy for SVC-Encoding Tile-Based 360-degree Panoramic Streaming 》阅读整理

## 1、本篇介绍

### Requerement: 

- ultra-high bandwidth 
- ultra-low Motion-to-Photon (MTP)delay (减少头部运动和视频渲染的延迟) 需要 MTP <= 20ms，防止生理晕眩。

### Problems to solve : 

- 如何在有限缓存大小的边缘服务器的本地缓存中选择合适的视频表示
- 当缓存不足时应该替换哪个质量的块表示

本文旨在通过研究**基于SVC的 tile 360度视频编码的边缘缓存替换策略**，提高缓存命中率，最大化用户的QoE。

这里规定：基础层可以独立解码，而增强层必须依赖于基础层解码

1. 因为低层视频块的请求量较大，当超过缓存容量时，低层视频块被驱逐的概率要比**高层视频块**小。
2. 如果数据块在用户的**FoV中**，它将具有较低的驱逐优先级。
3. **受欢迎度较高**的块应该以较高的概率缓存
4. 研究发现，替换**一个大的内容块**比替换多个小的内容块更能提高命中率。（考虑视频块大小）
5. An aging factor

最后的实验结果与LRU, LFU and GDSF相比较，更优。

## 2、系统架构

(1) 网络管理方案

客户端请求到达BS时，先检测请求到的内容是否在缓存中：

- cache hit
- cache miss

Our goal: increase the cache hit

(2) 360°视频模型

参数了解：N段视频，每段D秒，$S-t$ 是第t段视频，假设视频为每秒30帧，等矩形投影ERP. M tiles, 每个tile根据SVC被编码到L个不同的质量层中，编码后的贴图称为chunk.

注：所有chunk都有MPD文件，一起储存在服务器上。

Adaption（自适应）Input 包括：

- 视频信息Video information
- Viewpoint：来着用户以前的视角
- Network throughput: 网络吞吐量，从之前下载的块中测量
- Buffer status：以秒为单位

Output：（调度策略）

- 视角
- 质量调整

## 3、方法提出

(1) 计算视频块的Cache Value

Cache Value：缓存这个视频的可能性。越小越应该被替换掉。
$$
H\left(t, C_{v, k, i, q}\right)= C_{v, k, i, q}段视频在时间t的Cache  Value
$$

$$
\begin{aligned}
H\left(t, C_{v, k, i, q}\right)=& \text { clock }+P_{C_{v, k, i, q}}(t) \times \frac{1}{\operatorname{size}_{C_{v, k, i, q}}} \times \frac{L-q}{L} \times \frac{1+i s f o v_{C_{v, k, i, q}}}{2}
\end{aligned}
$$

解释1 ：
$$
P_{C_{v, k, i, q}}(t) 表示C_{v, k, i, q}段视频在时间t的流行程度
$$

$$
P_{C_{v, k, i, q}}(t)=\left\{\begin{array}{ll}
1, & \text { if } n=1 \\
1+\sum_{j=1}^{n-1} \frac{1}{t-t_{j}}, & \text { if } n>1
\end{array}\right.
$$

其中，n是这块被请求的次数，t_j是第j次被请求的时间，n越大，P越大。

解释2 ：
$$
{size}_{C_{v, k, i, q}}表示此块视频的大小
$$
解释3 ：
$$
L是等级数量，q是当前视频的等级。
$$
解释4 ：
$$
i s f o v_{C_{v, k, i, q}}是一个表示是否在预测Fov内的bool值
$$
解释5：
$$
Clock\ 是 \ cache\ aging\ factor
$$
当缓存空间不足以存储新块时，必须替换一个或多个缓存的视频块，以便为新块腾出空间。如果只需要更换一个视频块，则新视频块的时钟值设置为新视频块的缓存值H。否则，它被设置为所有被替换的视频块中最大的缓存值。

(2) SPLF (Size-Popularity-Layer-Fov)缓存替换策略

流程图形式表示

![image-20210301215651935](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210301215651935.png)

## 4、实验过程和实验结果



















