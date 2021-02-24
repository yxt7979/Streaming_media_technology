## 0、特征

- 交互性：用户能够通过自由选择视角和观看方向来探索和导航视听场景。

## 1、目前进度和研究成果

### For Effective video rate（有效视频率）

就是用户实际视角内的视频码率

- Flock

### bandwidth-effective

### 码率效率（encoding efficiency）

##### VOD：



### **Live** 360◦ **video streaming**：



切片：基于贴图(tile - based)的视频编码和传输被广泛应用于视场自适应视频流，这样可以使用不同的编码方法。【1，42】采用不同分辨率

具有不同分辨率的图像块被实时聚合成一个高效视频编码(HEVC)位流，允许在终端设备上仅使用一个解码器【31】

编码平台，QoE评测系统：基于gpu的实时HEVC编码平台在[2]中开发，采用[25]中提出的5G网络环境下的测量框架进行评估

编码：文献[27,35]采用分层编码方案，在不影响视频质量和带宽效率的情况下减少视频冻结的发生。（35：映射和编码技术）



## 2、文献

[1] Patrice Rondao Alface, Jean-François Macq, and Nico Verzijp. 2012. Interactive omnidirectional video delivery: A bandwidth-effective approach. *Bell Labs* Technical Journal* 16, 4 (2012), 135–147.

很大一部分的带宽被浪费在了传输高质量视频的区域上，而这些区域并没有被显示出来。我们评估了个性化传输的相关性和最优性，其中质量在球形或圆柱形区域中呈结节状，这取决于在实时用户交互过程中它们被查看的可能性。我们基于交互延迟和带宽限制，如何平铺和预测方法可以改进现有的方法。



[2] Trevor Ballard, Carsten Griwodz, Ralf Steinmetz, and Amr Rizk. 2019. RATS:adaptive 360-degree live streaming. In *Proceedings of the 10th ACM Multimedia *Systems Conference*. 308–311.

当只有部分视频（例如当前和预测的视口）以高质量传输而其余的360°视频图块传输时，最新的平铺360°自适应比特率视频流传输方法可节省大量带宽，几乎不会出现停顿的风险质量较低。尽管目前这对于Vod视频方案是可行的，但由于缺乏现有硬件编码器中的切片支持，会产生相当大的开销，因此对于360°实时流提出了一个难题。

在本演示中，我们显示实时自适应360流，其中我们利用基于GPU的HEVC编码来实时平铺，编码和缝合不同质量的360°视频。



[25] Cise Midoglu, Özgü Alay, and Carsten Griwodz. 2019. Evaluation Framework for Real-Time Adaptive 360-Degree Video Streaming over 5G Networks. In *Proceed*ings of the 2019 on Wireless of the Students, by the Students, and for the Students*Workshop*. 6–8.

评估real-time 360度视频的端到端分发，并考虑从视频捕获到编码，交付和回放的所有方面，以及及时和适当的分析，重点是最终用户的**体验质量（QoE）**。这需要一个**度量框架**，该框架允许同时从多个维度收集度量。在这项工作中，我们提出了这样一种框架，用于评估实验性的第五代（5G）网络上的实时自适应360度视频流，该框架可用于研究端到端视频交付链的不同方面。



[27] Afshin Taghavi Nasrabadi, Anahita Mahzari, Joseph D Beshay, and Ravi Prakash.2017. Adaptive 360-degree video streaming using scalable video coding. InProceedings of the 25th ACM international conference on Multimedia*. ACM, 1689–1697.

虚拟现实和360度视频流正在快速增长，然而，由于对带宽的高要求，流式传输高质量360度视频仍然面临挑战。现有的解决方案通过仅为用户的视口流传输高质量视频来减少带宽消耗。但是，将空间域（视口）添加到视频适应空间会阻止现有解决方案将未来的视频块缓冲的时间长于用户视口可预测的间隔。由于重新缓冲，这使得回放更容易出现视频死机，这严重降低了用户的体验质量，尤其是在充满挑战的网络条件下。我们提出了一种新方法，该方法通过利用可伸缩视频编码来减轻对缓冲区持续时间的限制。与现有解决方案相比，我们的方法可显着**减少带宽变化的链路上重新缓冲的发生**，而不会影响回放质量或带宽效率。我们利用真实蜂窝网络带宽跟踪的实验结果证明了我们提出的方法的效率。



[31] Robert Skupin, Yago Sanchez, Cornelius Hellge, and Thomas Schierl. 2016. Tile-based HEVC video for head mounted displays. In *2016 IEEE International Sympol *sium on Multimedia (ISM)*. IEEE, 399–400.

实现视口自适应流的一种更有效的方法是促进运动受限的HEVC切片。保留用户视口中的原始内容分辨率，而当前未呈现给用户的内容以较低的分辨率传递。可以即时进行将不同分辨率的切片轻量级聚合到单个HEVC比特流中，并允许在**终端设备上使用单个解码器**实例。



[35] Afshin TaghaviNasrabadi, Anahita Mahzari, Joseph D Beshay, and Ravi Prakash.2017. Adaptive 360-degree video streaming using layered video coding. In *2017 IEEE Virtual Reality (VR)*. IEEE, 347–348.

映射：现有的视频编码器无法直接对球形视频进行编码。在这方面，视频应在编码之前映射到2D平面。有多种地图投影方法，例如等角，金字塔和立方体投影。|| 编码：自适应360度视频流解决方案将**视频分成几秒**的持续时间，并将每个片段在空间域中切成**切片**。每个图块均以几种质量级别编码。然后，客户端根据视口预测和网络条件请求分段。



[42] Alireza Zare, Alireza Aminlou, Miska M Hannuksela, and Moncef Gabbouj. 2016.HEVC-compliant tile-based streaming of panoramic video for virtual reality applications. In *Proceedings of the 24th ACM international conference on Multimedia*.ACM, 601–605

交付广角和高分辨率的球形全景视频内容需要很高的流比特率。原因是HMD（头显）通常需要高的空间和时间保真度内容以及严格的低延迟才能保证用户在使用它们时的临场感。这篇论文**以不同的分辨率存储同一视频内容的两个版本**，每个版本都使用高效视频编码（HEVC）标准划分为多个图块。根据用户当前的视角，将以捕获的最高分辨率传输一组图块，而其余部分则从相同内容的低分辨率版本传输。为了能够随机选择不同的组合，将图块集编码为可独立解码。我们进一步研究了切片方案选择的权衡及其对压缩和流式比特率性能的影响。结果表明，与流式传输整个视频内容相比，根据所选的切片方案，流式传输的比特率节省了30％至40％。

## 3、挑战和未解决问题

### （1）缓存大小，缓存管理，计算成本

缓存大小仍然是一个挑战。

缓存管理：研究缓存哪些内容和缓存哪里。关于这个主题有大量的文献，通过分析响应延迟、缓存命中率、远程按需请求和能量消耗，利用各种策略来实现结果。然而，大多数的研究