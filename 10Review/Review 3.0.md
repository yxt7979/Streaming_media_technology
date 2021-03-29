# Fov - Aware caching policy

## 1、问题

缓存基于贴图的360视频的挑战是

- (i)如何用适当分辨率的贴图填充有限大小的缓存，以及适当的分辨率。
- (ii)当缓存容量超过时，将**哪些贴图从缓存中驱逐出来**，以便为新的贴图留出空间。

## 2、结构

客户必须根据**FoV**和**网络条件**来决定**tile的质量**。

### Fov Prediction：

每100ms从客户端提取100样本，选出前十个最新请求的为输入，利用WLR 预测1s后的Fov。

### Network：

$$
1、Fov内用高分辨率，其他用低分辨率,biterate: \left[14 \% \cdot R_{\text {high }}+86 \% \cdot R_{\text {low }}\right]
$$

$$
2、对所有的分块都请求低分辨率,biterate:\left[100 \% \cdot R_{\text {low }}\right]
$$

 throughput 样本的计算方法：

![image-20210329170036561](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210329170036561.png)
$$
\text { throughput_sample }=\frac{\sum_{j=1}^{t} \operatorname{size}\left(T_{j}\right)}{\sum_{i=1}^{t} \text { download_time }\left(T_{j}\right)}
$$
network throughput estimation = 最近3个样本的平均值
$$
如果network \ 在 \left[\frac{f}{t} \cdot R_{h i g h}+\frac{t-f}{t}\cdot R_{l o w}\right]区间内就可以第一种方式选择分辨率
$$

## 3、提出方法

### 前提特性

（1）**FoV Pattern**与内容的关系 -- heatmap 表示 -- 得到 common-Fov：

- 博物馆观光类：头部转动较多但是轨迹相似
- 赛车比赛类：较激烈的运动在前方，很少有向后看的

（2）**Impact of Video’s Bitrate on FoV’s Quality**

 网络条件固定时，Video’s Bitrate ↑，FoV’s Quality ↓。

### 提出 **FoV-aware Caching Policy**

adaption logic -- 根据计算的network 情况选择以何种方式缓存

Policy 考虑两个指标（based on viewing history）：
$$
1、tile 在common-Fov 中的概率 \ \theta_{v, s, i}
$$

$$
2、用户要求每个视频在Fov中的tile以高质量请求的概率 \ \psi v
$$

通过最大似然估计后求导得到上面两个参数。
$$
进而通过\gamma_{v, s, i, q}=\left\{\begin{array}{ll}
\theta_{v, s, i} * \psi_{v}, & \text { if } q=\text { high } \\
\left(1-\theta_{v, s, i}\right)+\theta_{v, s, i} *\left(1-\psi_{v}\right), & \text { if } q=\text { low }
\end{array}\right.得到\gamma_{v, s, i, q}
$$
γ代表：tile t 将在未来以q的质量请求的概率。

γ越小越优先剔除

## 4、实验









Chunk性质：

![image-20210329104123056](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210329104123056.png)

6 * 4

download time 用来测量网络吞吐量

resolution 分辨率：640 × 540 and 320 × 270 pixels （P6 - 5.1)

We encode each tile with Constant Rate Factor (CRF) of 21

set maximum bitrate per tile to 3Mbps --> high resolution tiles

1Mbps --> low resolution tiles





