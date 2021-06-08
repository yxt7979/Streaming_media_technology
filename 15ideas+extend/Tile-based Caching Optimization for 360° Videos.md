# **Tile-based Caching Optimization for 360**° **Videos**

目标：**decide which tiles and tile resolutions to cache**，each tile should be *as close* *as possible* to the required ones.

low average content delivery delay & low bandwidth consumption

increase hit ratio minimize average delivery delay

避免分辨率高，防止不必要的浪费，同时需要的分辨率也应该满足用户需求。

目标：让缓存的tile的分辨率尽可能接近

## 1、Model

video S segments

tile i : the number of the special side，tile number

Pis：the probability that tile i is requested in segment s

Qiv：viewport v 中的tile i

Pir：第i块被请求，以qr为分辨率请求的条件概率

video encoding model：

1. *multiple-versions*
2. *layered-encoding*

## 2、Problem Statement

We are interested in finding a tile and tile resolution caching policy that are optimal in the sense outlined below.

给一个贴图多个分辨率会占用别的贴图的空间 -> certain tiles request fewer/one resolution

layered encoding：确定缓存的最高层

### Multiple-versions case

tile i ,resolution qr

*x* *ir* = 1，表示以第r大的分辨率存储第i个tile，否则为0

差距：归一化平方误差
$$
\operatorname{dist}\left(q_{r}, q_{\tilde{r}}\right)=\frac{1}{D}\left(q_{r}-q_{\tilde{r}}\right)^{2}
$$
高：浪费带宽

低：降低用户QoE

目标：finding the subsets R of resolutions to cache for each tile i. **minimize the average squared error metric**

### Layered-encoding case

XilL = 1表示第i个tile会缓存第i层到第l层layers （L表示一共的layer数）
$$
\operatorname{dist}_{L}\left(q_{r}, q_{\ell}\right)=\frac{1}{D}\left(q_{r}-q_{\ell}\right)_{+}^{2}
$$
区别：当缓存的不足以提供请求的才会受到影响。

## 3、Implementation & Evaluation

通过更新policy函数来优化

Policy vector：一个n字节的字符串（没懂）

memory overhead

