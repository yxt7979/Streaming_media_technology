[TOC]

## (1) Fov prediction

### VOD：[9,17,29,33]

针对VoD流媒体提出的，并且假设总是有大量的用户在观看同一段视频。

1. 建立针对用户头部转动速度的FoV视点预测模型,通过隐马尔可夫模型(Hidden Markov Model,HMM)与混合高斯分布模型(Gaussian Mixed Model,GMM)建立以用户头部转动速度为观测的时序模型,以HMM的隐藏状态描述对应用户头部转动速度序列的内部模式信息。
2. 针对现有利用LSTM网络预测FoV分块的方案中,输入特征数据量较大且没有充分挖掘用户观看行为规律的问题,以及模型训练目标不符合实际应用场景的问题,提出基于LSTM网络的改进FoV分块预测模型。同时,提出覆盖一定时间范围内用户FoV的预测目标和训练数据标记方式。基于模型的分块级预测序列,提出重点参考预测值较高分块信息的同时结合预测结果在空间域分布信息的FoV区域划分方案。在预测准确度与F-Score性能上均实现了对现有方法的提高。
3. 分治思想【17】
4. 16年提出下载子区域，提出tile的思想。LR，WLR回归方法。统计数据【29】
5. 在[4]中，提出了基于线性回归和深度神经网络(DNN)的解决方案，利用历史视场轨迹预测用户未来视场中心。
6. 在[11]中，不仅使用过去的FoV轨迹，还利用视频内容特征来预测未来的FoV。
7. 在[19]中，作者着重研究了长时间范围的FoV预测，这对于具有长缓冲区的按需流平滑网络流量非常重要，并提出了多种基于lstm的模型。
8. 在[12]中采用了自回归移动平均(ARMA)预测
9. [7]中转移概率模型
10. [16]的研究表明，用户感知质量也受到物体相对移动速度、景深和亮度变化的影响
11. [3, 19]考虑了基于其他用户观看方向的协同FoV预测。然而，这些方法是

### live 360：[14,30]

1. 带宽使用和视频质量之间进行了权衡。我们创建了一种将RTP和DASH结合在一起的架构，可将360°VR内容提供给华为机顶盒和三星Galaxy S7
2. 

### 交互式360：[5,40]



## (2) Live 360◦ video streaming：

- 在[20]中，作者提出了一个**测量平台**，对现有的商业直播360°流媒体平台，如Facebook和YouTube进行测量。QoE指标包括视频比特率，持续时间和视频冻结的数量，以及用户实时延迟收集了来自不同国家的大量观众。
- [14]还提出了一个360°实时流媒体系统，**在用户视场内的带宽使用和视频质量之间进行权衡**。在直播360流媒体系统中，严格的实时性要求对编码效率提出了挑战。基于这个设计，可以使用不同的编码方法。
- 在[31]中，具有不同分辨率的片被实时聚合成一个高效视频编码(HEVC)位流，允许在终端设备上仅使用一个解码器。
- 基于gpu的实时HEVC编码平台在[2]中开发，采用[25]中提出的5G网络环境下的测量框架进行评估。
- 文献[27,35]采用**分层编码方案**，在不影响视频质量和带宽效率的情况下减少视频冻结的发生。我们专注于直播的系统级设计，利用观众通常对类似区域感兴趣的事实.

- 即以高质量交付包含在用户视场(FoV)中的视频帧的部分，而以低质量交付帧的其余部分，以节省带宽。
- 在点播的顶级流媒体类型的应用领域，有许多解决方案使用DASH(动态自适应流在HTP上)，旨在优化tile选择，速率适应和存储优化等。但是这些方法有可能节省大量带宽，但在tiles中编码视频会带来流媒体和存储损失，因为需要更多的头部，编码效率降低，必须发送更多的下载请求。此外，如果下载策略未能及时为FoV下载高质量的贴图以供回放，那么感知到的视频质量就会受到影响，例如，在dash风格的流媒体中，质量可能会在段边界发生变化，即通常每两秒发生一次。如果视场在片段回放的中间移动到一个低质量的贴图，视场的质量就会下降。

## (3) **Edge caching**

视频流的边缘缓存在最近的研究中得到了广泛的研究[18,21,41]。

- 在[13]中，提出了5G网络中同时考虑内容和网络上下文的二维缓存算法。
- 在360°视频的[28]中研究了编码缓存增益和传输延迟之间的权衡，边缘缓存在解决网络效率和视频传输问题上也发挥了重要作用。与传统的视频缓存不同，360°用户在播放过程中在tile之间移动他们的fov(被认为是非线性观看)，这可以从[15]中提出的缓存技术中受益，该技术被证明对非线性视频内容有益。
- 在[22]中，提出了fov感知的缓存策略，结果表明所提出的算法与传统的缓存相比有显著的改进。然而，他们认为用户开始观看360°视频时，会有30秒左右的延迟间隙。与此不同的是，我们的工作策略性地在一个可接受的范围(0-20秒)内分配给用户不同的延迟，并考虑视场和延迟因素来决定是否缓存下载的视频块。
- 在[10]中提出了一种新的HEVC转码方案。
- [6]的作者研究了沉浸式视频传输的缓存和边缘计算之间的权衡。
- 缓存和计算卸载策略联合优化，以减少所需的传输速率在[34]。这里我们考虑如何通过实时代码转换提高缓存性能，但代价是计算。

边缘计算和缓存:利用kedge技术，如在网络边缘的计算和存储，接近终端用户，可以流媒体的高级多媒体，如360°视频。这些技术的出现降低了高质量视频[31]的端到端延迟、带宽消耗和能量消耗。作者在[7]中使用边缘计算来实现交互式多媒体和视频流的实时响应。[15]通过提出在云服务器或边缘服务器上完成呈现任务来解决比特率和延迟需求的挑战。在移动网络环境下，[20]利用移动边缘计算(MEC)对视场进行处理和渲染，以优化带宽消耗和电池利用率。[8]研究了通过回程链路连接的小蜂窝基站(BSs)之间的合作，设计了一个优化框架，通过向用户提供360°可导航视频，使每个基站的奖励最大化

## (4) 360° 视频概述 【MM18】

**投影**：成2D进行编码，投影方法有等矩形投影和立方体地图投影。等直角投影是最常用的方法[12,22]。

**分块技术**：该视频分为瓷砖，瓷砖内的用户的FoV是流在高质量的[27]。

[26]采用了自适应流的平铺法和视场预测。结果表明，线性回归方法可以预测用户未来的FoV最多2秒，从而可以预取相关的FoV贴图，实现流畅的视频播放。

在[25]中使用HTTP/2协议来传输多个块，具有更高的性能。在[22]中，tile采用了SVC (Scalable Video Coding)编码方法，tile是逐层流的。该方法可以减少视频延迟事件的数量。

另外，为了解决用户侧多解码器对每个贴图进行解码的问题，[33]采用了高效视频编码(HEVC)标准中运动约束贴图集(MCTS)的特性，采用了单一的硬件解码器。

## 1、目前进度和研究成果

### For Effective video rate（有效视频率）

就是用户实际视角内的视频码率

- Flock

### bandwidth-effective

### 码率效率（encoding efficiency）

##### VOD：

- 基于tile的视频编码和传输被广泛用于实现视场自适应视频流[1,42]。切片：基于贴图(tile - based)的视频编码和传输被广泛应用于视场自适应视频流，这样可以使用不同的编码方法。【1，42】采用不同分辨率

1. 



## 2、文献

[1] Patrice Rondao Alface, Jean-François Macq, and Nico Verzijp. 2012. Interactive omnidirectional video delivery: A bandwidth-effective approach. *Bell Labs* Technical Journal* 16, 4 (2012), 135–147.

很大一部分的带宽被浪费在了传输高质量视频的区域上，而这些区域并没有被显示出来。我们评估了个性化传输的相关性和最优性，其中质量在球形或圆柱形区域中呈结节状，这取决于在实时用户交互过程中它们被查看的可能性。我们基于交互延迟和带宽限制，如何平铺和预测方法可以改进现有的方法。



[2] Trevor Ballard, Carsten Griwodz, Ralf Steinmetz, and Amr Rizk. 2019. RATS:adaptive 360-degree live streaming. In *Proceedings of the 10th ACM Multimedia *Systems Conference*. 308–311.

当只有部分视频（例如当前和预测的视口）以高质量传输而其余的360°视频图块传输时，最新的平铺360°自适应比特率视频流传输方法可节省大量带宽，几乎不会出现停顿的风险质量较低。尽管目前这对于Vod视频方案是可行的，但由于缺乏现有硬件编码器中的切片支持，会产生相当大的开销，因此对于360°实时流提出了一个难题。

在本演示中，我们显示实时自适应360流，其中我们利用基于GPU的HEVC编码来实时平铺，编码和缝合不同质量的360°视频。



[9] Xavier Corbillon, Gwendal Simon, Alisa Devlic, and Jacob Chakareski. 2017.Viewport-adaptive navigable 360-degree video delivery. In *2017 IEEE international* *conference on communications (ICC)*. IEEE, 1–7.

我们调查了各种球面到平面投影和质量安排对显示给用户的视频质量的影响，结果表明，在给定的比特率预算下，立方体贴图布局可提供最佳质量。对用户浏览360度视频的数据集进行的评估表明，分段需要足够短才能启用频繁的视图切换。



[12] Mario Graf, Christian Timmerer, and Christopher Mueller. 2017. Towards Bandwidth Efficient Adaptive Streaming of Omnidirectional Video over HTTP: Design,Implementation, and Evaluation. In *Proceedings of the 8th ACM on Multimedia* *Systems Conference*. ACM, 261–271.





[14] Carsten Griwodz, Mattis Jeppsson, Håvard Espeland, Tomas Kupka, Ragnar Langseth, Andreas Petlund, Peng Qiaoqiao, Chuansong Xue, Konstantin Pogorelov, Micheal Riegler, et al. 2018. Efficient Live and on-Demand Tiled HEVC 360 VR Video Streaming. In *2018 IEEE International Symposium on Multimedia* *(ISM)*. IEEE, 81–88.https://ieeexplore.ieee.org/document/8603263

随着360°全景视频技术的普及，对于此类视频的高效流式传输方法的需求不断增加。我们超越了现有的按需解决方案，并提出了一种实时流传输系统，该系统在用户视野内的带宽使用和视频质量之间进行了权衡。我们创建了一种将RTP和DASH结合在一起的架构，可将360°VR内容提供给华为机顶盒和三星Galaxy S7。我们的系统多路复用单个HEVC硬件解码器，以提供比传统GOP边界更快的质量切换。我们通过实际实验演示了性能并说明了权衡取舍，在这些实验中，我们可以报告与现有按需方法可比的带宽节省，但是当视野改变时，可以更快地切换质量。



[17] Mohammad Hosseini and Viswanathan Swaminathan. 2016. Adaptive 360 VR video streaming: Divide and conquer. In *2016 IEEE International Symposium on* *Multimedia (ISM)*. IEEE, 107–110.

我们提出了一种采用分而治之的自适应带宽高效的360 VR视频流系统。我们提出了一种动态的视图感知自适应技术，以解决360 VR视频流的巨大带宽需求。



[20] Xing Liu, Bo Han, Feng Qian, and Matteo Varvello. 2019. LIME: understanding commercial 360° live video streaming services. In *Proceedings of the 10th ACM* *Multimedia Systems Conference*. ACM, 154–164.

研究人员对投影/编码方法[6,10,25,31,52]、能量消耗[23l]、视口自适应流媒体[12,13,15,16,20,32,35,36,45-471、跨层交互[41,48]、用户体验[14]等方面进行了研究。上述研究大多集中在非直播的360视频上，没有一个像我们使用众包（crowd-sourcing.）那样调查商业360视频流平台。（QoE指标包括视频比特率，持续时间和视频冻结的数量，以及用户实时延迟收集了来自不同国家的大量观众。）



[22] Afshin Taghavi Nasrabadi, Anahita Mahzari, Joseph D. Beshay, and Ravi Prakash.2017. Adaptive 360-Degree Video Streaming Using Scalable Video Coding. In *Proceedings of the 2017 ACM on Multimedia Conference (MM ’17)*. ACM, 1689–1697. https://doi.org/10.1145/3123266.3123414





[25] Cise Midoglu, Özgü Alay, and Carsten Griwodz. 2019. Evaluation Framework for Real-Time Adaptive 360-Degree Video Streaming over 5G Networks. In *Proceed*ings of the 2019 on Wireless of the Students, by the Students, and for the Students*Workshop*. 6–8.

评估real-time 360度视频的端到端分发，并考虑从视频捕获到编码，交付和回放的所有方面，以及及时和适当的分析，重点是最终用户的**体验质量（QoE）**。这需要一个**度量框架**，该框架允许同时从多个维度收集度量。在这项工作中，我们提出了这样一种框架，用于评估实验性的第五代（5G）网络上的实时自适应360度视频流，该框架可用于研究端到端视频交付链的不同方面。



[27] Afshin Taghavi Nasrabadi, Anahita Mahzari, Joseph D Beshay, and Ravi Prakash.2017. Adaptive 360-degree video streaming using scalable video coding. InProceedings of the 25th ACM international conference on Multimedia*. ACM, 1689–1697.

虚拟现实和360度视频流正在快速增长，然而，由于对带宽的高要求，流式传输高质量360度视频仍然面临挑战。现有的解决方案通过仅为用户的视口流传输高质量视频来减少带宽消耗。但是，将空间域（视口）添加到视频适应空间会阻止现有解决方案将未来的视频块缓冲的时间长于用户视口可预测的间隔。由于重新缓冲，这使得回放更容易出现视频死机，这严重降低了用户的体验质量，尤其是在充满挑战的网络条件下。我们提出了一种新方法，该方法通过利用可伸缩视频编码来减轻对缓冲区持续时间的限制。与现有解决方案相比，我们的方法可显着**减少带宽变化的链路上重新缓冲的发生**，而不会影响回放质量或带宽效率。我们利用真实蜂窝网络带宽跟踪的实验结果证明了我们提出的方法的效率。



[29] Feng Qian, Lusheng Ji, Bo Han, and Vijay Gopalakrishnan. 2016. Optimizing 360 video delivery over cellular networks. In *Proceedings of the 5th Workshop on All* *Things Cellular: Operations, Applications and Challenges*. ACM, 1–6.

我们提出了一种基于头部运动预测的手机友好流媒体方案，仅提供360个视频的可视部分。下载子区域，



[30] Rodrigo Silva, Bruno Feijó, Pablo B Gomes, Thiago Frensh, and Daniel Monteiro.2016. Real time 360 video stitching and streaming. In *ACM SIGGRAPH 2016* *Posters*. ACM, 70.

在本文中，我们提出了一种针对GPU的实时360°视频拼接和流处理方法。该解决方案为高分辨率创建了可扩展的解决方案，例如每台摄像机4K和8K，并支持具有云体系结构的广播解决方案。该方法使用一组使用OpenGL（GLSL）处理的可变形网格，最终图像使用健壮的像素着色器组合输入。此外，可以使用带有nVEnc GPU编码的h.264编码将结果流式传输到云服务。最后，我们提出一些结果。



[31] Robert Skupin, Yago Sanchez, Cornelius Hellge, and Thomas Schierl. 2016. Tile-based HEVC video for head mounted displays. In *2016 IEEE International Sympol *sium on Multimedia (ISM)*. IEEE, 399–400.

实现视口自适应流的一种更有效的方法是促进运动受限的HEVC切片。保留用户视口中的原始内容分辨率，而当前未呈现给用户的内容以较低的分辨率传递。可以即时进行将不同分辨率的切片轻量级聚合到单个HEVC比特流中，并允许在**终端设备上使用单个解码器**实例。



[33] Liyang Sun, Fanyi Duanmu, Yong Liu, Yao Wang, Yinghua Ye, Hang Shi, and David Dai. 2019. A two-tier system for on-demand streaming of 360 degree video over dynamic networks. *IEEE Journal on Emerging and Selected Topics in Circuits* *and Systems* 9, 1 (2019), 43–57.

360°视频点播流，发送整个360°视频需要极高的网络带宽。另一方面，仅发送预测用户的视场（FoV）是不可行的，因为在点播流中很难实现完美的FoV预测，在这种情况下，最好提前几秒钟预取视频以吸收网络带宽波动。本文提出了一种两层解决方案，其中基本层以较低的质量通过较长的预取缓冲区提供整个360°跨度，而增强层使用较短的缓冲区以较高的质量提供预测的FoV。基本层为网络带宽变化和FoV预测错误提供了鲁棒性。如果及时交付且FoV预测准确，则增强层可提高视频质量。我们研究了两层之间的最佳速率分配以及增强层的缓冲区配置，以实现视频质量和流鲁棒性之间的最佳折衷。我们还设计了周期性和自适应优化框架，以实时适应带宽变化和FoV预测误差。通过由实际LTE和WiGig网络带宽轨迹以及用户FoV轨迹驱动的仿真，我们证明，面对网络带宽和用户FoV动态，所提出的两层系统可以实现较高的体验质量。如果及时交付且FoV预测准确，则增强层可提高视频质量。我们研究了两层之间的最佳速率分配以及增强层的缓冲区配置，以实现视频质量和流鲁棒性之间的最佳折衷。我们还设计了周期性和自适应优化框架，以实时适应带宽变化和FoV预测误差。通过由实际LTE和WiGig网络带宽轨迹以及用户FoV轨迹驱动的仿真，我们证明，面对网络带宽和用户FoV动态，所提出的两层系统可以实现较高的体验质量。如果及时交付且FoV预测准确，则增强层可提高视频质量。我们研究了两层之间的最佳速率分配以及增强层的缓冲区配置，以实现视频质量和流鲁棒性之间的最佳折衷。我们还设计了周期性和自适应优化框架，以实时适应带宽变化和FoV预测误差。通过由真实的LTE和WiGig网络带宽轨迹以及用户FoV轨迹驱动的仿真，我们证明了面对网络带宽和用户FoV动态，所提出的两层系统可以实现高水平的体验质量。我们研究了两层之间的最佳速率分配以及增强层的缓冲区配置，以实现视频质量和流鲁棒性之间的最佳折衷。我们还设计了周期性和自适应优化框架，以实时适应带宽变化和FoV预测误差。通过由实际LTE和WiGig网络带宽轨迹以及用户FoV轨迹驱动的仿真，我们证明，面对网络带宽和用户FoV动态，所提出的两层系统可以实现较高的体验质量。我们研究了两层之间的最佳速率分配以及增强层的缓冲区配置，以实现视频质量和流鲁棒性之间的最佳折衷。我们还设计了周期性和自适应优化框架，以实时适应带宽变化和FoV预测误差。通过由实际LTE和WiGig网络带宽轨迹以及用户FoV轨迹驱动的仿真，我们证明，面对网络带宽和用户FoV动态，所提出的两层系统可以实现较高的体验质量。



[35] Afshin TaghaviNasrabadi, Anahita Mahzari, Joseph D Beshay, and Ravi Prakash.2017. Adaptive 360-degree video streaming using layered video coding. In *2017 IEEE Virtual Reality (VR)*. IEEE, 347–348.

映射：现有的视频编码器无法直接对球形视频进行编码。在这方面，视频应在编码之前映射到2D平面。有多种地图投影方法，例如等角，金字塔和立方体投影。|| 编码：自适应360度视频流解决方案将**视频分成几秒**的持续时间，并将每个片段在空间域中切成**切片**。每个图块均以几种质量级别编码。然后，客户端根据视口预测和网络条件请求分段。



[40] Xiufeng Xie and Xinyu Zhang. 2017. Poi360: Panoramic mobile video telephony over lte cellular networks. In *Proceedings of the 13th International Conference on* *emerging Networking EXperiments and Technologies*. ACM, 336–349.

互动类视频电话系统



[42] Alireza Zare, Alireza Aminlou, Miska M Hannuksela, and Moncef Gabbouj. 2016.HEVC-compliant tile-based streaming of panoramic video for virtual reality applications. In *Proceedings of the 24th ACM international conference on Multimedia*.ACM, 601–605

交付广角和高分辨率的球形全景视频内容需要很高的流比特率。原因是HMD（头显）通常需要高的空间和时间保真度内容以及严格的低延迟才能保证用户在使用它们时的临场感。这篇论文**以不同的分辨率存储同一视频内容的两个版本**，每个版本都使用高效视频编码（HEVC）标准划分为多个图块。根据用户当前的视角，将以捕获的最高分辨率传输一组图块，而其余部分则从相同内容的低分辨率版本传输。为了能够随机选择不同的组合，将图块集编码为可独立解码。我们进一步研究了切片方案选择的权衡及其对压缩和流式比特率性能的影响。结果表明，与流式传输整个视频内容相比，根据所选的切片方案，流式传输的比特率节省了30％至40％。

## 3、挑战和未解决问题

### （1）缓存大小，缓存管理，计算成本

缓存大小仍然是一个挑战。

缓存管理：研究缓存哪些内容和缓存哪里。关于这个主题有大量的文献，通过分析响应延迟、缓存命中率、远程按需请求和能量消耗，利用各种策略来实现结果。然而，大多数的研究