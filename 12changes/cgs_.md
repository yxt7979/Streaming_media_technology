### 几种访问类型：

1.顺序访问。所有的块一个接一个被访问，不存在重访问。

2.循环访问。所有块都按照一定的间隔重复访问

3.时间密集访问。最近被访问的块是将来最有可能被访问的。

4.概率访问。所有块都有固定的访问概率，所有块都互相独立地根据概率被访问。

5.关联访问(Correlated References)，块被首次访问之后，紧接着的短时间内会有数次访问。

## LRU

淘汰最长时间未被使用的页面。

- 对冷数据突发性访问抵抗能力差，可能会因此淘汰掉热的文件。热点页面在偶然一个时间节点被其他大量仅访问了一次的页面所取代则造成浪费。
- 对于大量数据的循环访问抵抗能力查，极端情况下可能会出现命中率0%。（如：循环访问）
- 不能按照数据的访问概率进行淘汰。

## LRU - K

相比于传统的LRU就是LRU - 1，仅访问了一次就能代替别人。

对比：最后第K次的访问距离。访问距离 ↑，时间间隔 ↑ ，被替换 ↑ 。

LRU-2，只有当数据的访问次数达到2次的时候，才将数据放入缓存。当需要淘汰数据时，LRU-2会淘汰第2次访问时间距当前时间最大的数据。

针对问题1：关联访问，即块被首次访问之后，紧接着的短时间内会有数次访问。

提出参数：

- Correlated References Period（块首次访问后的一段时间）

- Reference Retained Information Period（对于替换出cache后的块会继续保留访问信息一段时间）

## 2Q



## LIRS (Low Inter-reference Recency Set)



## EELRU



[参考地址1](https://blog.csdn.net/Pun_C/article/details/50920469?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522161900299716780271575751%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=161900299716780271575751&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduend~default-3-50920469.first_rank_v2_pc_rank_v29&utm_term=LIRS)

[参考地址2 - LRU - K](https://segmentfault.com/a/1190000022558044)