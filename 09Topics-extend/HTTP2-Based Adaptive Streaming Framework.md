# An HTTP/2-Based Adaptive Streaming Framework for 360° Virtual Reality Videos

## 1、Related work：

(1) 360° video streaming

- 低分辨率的整个视频的tile总被下载，防止黑屏。
- 多播传输，提出算法来确定要多播的贴图的分辨率并使所有用户的效用最大化。

但是都是基于H.264平铺的，但其实H.264不支持平铺，导致每个瓦片都必须独立解码。

- 用H.265对视频空间进行分割。
- 提出了一种基于可用带宽和用户视口的速率分配算法来决定每个贴图的质量。（不足：HTTP1.1且没有考虑用户的移动）
- Gaddam et al. use tiling and viewport prediction to stream interactive panoramic videos, where part of the panorama can be used to extract a virtual view.（不知道是在干啥，不足：HTTP1.1，H.264）

(2)  HTTP/2-Based Adaptive Streaming

HTTP/2引入的一个新特性是服务器可以推送客户端没有直接请求的资源，以减少web和多媒体交付的延迟。

- Wei等人关注了服务器推送如何改善HAS流的交付。（减少相机到显示器的延迟，且在客户端发出一个HTTP GET请求后推送k个段）
- Xiao等人通过根据网络条件和电能效率动态改变k值，优化移动设备上的电池寿命。
- van der Hooft等人研究了H.265视频在4G网络上的服务器推送的优点。
- Cherif等人将服务器推送与WebSocket结合使用，以减少DASH流会话的启动延迟。

我们利用k-push机制且利用服务器推送功能，以减少由于将视频空间划分为单独的块而引入的网络开销。

## 2、框架提议

### 框架的三大亮点：

- 使用H.265标准对VR内容进行编码，并将其划分为空间贴图，每个贴图的编码质量水平不同。

- 视频客户端配备了一种算法，可以根据当前和预测的未来视点以及可用的网络带宽等信息为每个贴图选择**最佳的视频质量**，持续减少360°视频流所需的带宽。

- HTTP/2协议的服务器推送k-push功能允许消除由于平铺视频而导致的HTTP GET请求的显著增加，从而提高了所实现的吞吐量，特别是在高RTT网络中。

### （1）H.265 Video Tiling





