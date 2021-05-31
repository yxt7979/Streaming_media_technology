# DeepCache: A Deep Learning Based Framework For Content Caching

## 1、介绍

难点：cache ＆ evict，流行程度变化，不能依赖于本地

1. 预测未来对象的特征
2. 连续预测
3. 利用特征提高缓存表现

目标：自适应缓存机制，了解请求流量的变化，预测未来特征，觉得缓存和驱逐哪些对象

两个要点：

1. popularity prediction：seq2seq model (LSTM)
2. DeepCache 的缓存框架：通过流行度做出决策

## 2、Overview

core idea：提前预测对象特征（预测对象的流行度）

- 提前预取对象，提高缓存命中率
- 了解对象的流行程度，防止替换出流行的chunk，减少网络抖动问题

目标：increase the number of cache hits

预测接下来3个时间段：three separate time intervals in future: 1-3 hours, 12-14
 hours and 24-26 hours

## 3、popularity prediction model

在过去流行度的基础上构建未来流行度，这里的向量特征都是**流行程度**

输入：t长度的数组，每个元素是与对象对应的d维的特征向量（d=不同objects的数量）
$$
X_{t}=\left\{x_{1}, x_{2}, \ldots, x_{t}\right\}
$$
输出：t长度的数组，每个元素是与对象对应的p维的特征向量（p=不同objects的数量）
$$
Y_{t}=\left\{y_{1}, y_{2}, \ldots, y_{k}\right\}
$$
最终是以这种格式：(#samples , d,m, 1) and (#samples , d, k, 1)

## 4、Caching policy

周期性的生成“fake content requests” 加到原本的请求的后面

## 5、实验

m = 20

数据1：50个不同的请求，80K个requests，6个间隔，每个间隔1000个请求左右，流行程度的排序是固定的，popularities满足参数不同的Zipf分布。(k = 10)

数据2：更类似真实数据，1425 unique objects with more than 2 million requests，每个都有存活期限。有Zipf的参数。(k = 26)



