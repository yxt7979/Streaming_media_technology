# 关于SVC的两点调研

## 1、是否需要逐层获取

答：需要，内部很复杂但一般都分为**三层**，且**基础层**结合**增强层**得到的**最高层**

越高的帧率，需要越高层，但每个高层的帧需要其下面的其他的帧做参考，每个level都需要其下面level的，不夸层的，每一层都需要依赖较低层才能被解码，但不需要任何较高层。

SVC分为**时间分级**，**空间分级**和**质量分级**。

- 时间分级是以帧为单位，给不同的帧分配不同的重要等级，以便于应用中按照重要程度显示帧(或在恶劣网络条件下主动放弃低等级的帧)
- 空间分级用于形成不同图像的分辨率。
- 质量分级是特殊的空间分级，从粗粒度变到中等粒度（没太看这块）

分辨率需要考虑**空间分级**中的过程，每个层对应一个支持的空间分辨率，由空间层或依赖标识符D引用。基本层的**依赖标识符**等于0，且逐层加一。对于给定的时间瞬间具有不同空间分辨率的表示形式构成一个访问单元，必须按照其相应的**空间层标识符的递增顺序**依次传输。

参考：

[《Overview_SVC_IEEE07》的第6，7页](http://ip.hhi.de/imagecom_G1/assets/pdfs/Overview_SVC_IEEE07.pdf):

<img src="https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210521145736700.png" alt="image-20210521145736700"  />

<img src="https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210521145757136.png" alt="image-20210521145757136"  />

[一个SVC实验的博客](https://blog.csdn.net/feixiang_john/article/details/7785859?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522162157776616780261940779%2522%252C%2522scm%2522%253A%252220140713.130102334.pc%255Fall.%2522%257D&request_id=162157776616780261940779&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~first_rank_v2~rank_v29-23-7785859.first_rank_v2_pc_rank_v29&utm_term=Scalable+Video+Coding&spm=1018.2226.3001.4187)

## 2、关于分辨率大小的问题

“对于质量分级和空域分级，同等质量需要**大概多10%的码率**。（压缩效率要比单层码流低10%，也就是和AVC对比）时域分级的码率有所提高（实际上相当于I,P,B帧的拓展），但是对运动强度比较大的场景，码率有所增加。”

我理解是：设置码率时，要在本来的码率基础上需要增加10%。论文中利用SHVC软件进行编码，QP（量化）参数的设定是：32-28-24。（QP参数越大码率越低）