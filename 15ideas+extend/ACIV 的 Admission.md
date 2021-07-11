# ACIV 的 Admission

监督二分类问题，训练GBDT分类器

两个难点：

1. time horizon：在某长的时间间隔中，被请求的chunk不会被再次请求
2. choice of features

Time horizon：

depend on cache size，