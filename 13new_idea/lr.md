[TOC]

## Part One -- 理解强化学习术语

RL：通过奖励来更新模型参数让模型越来越好。

### 1、一些名词：

**Agent**：智能体，做动作的主体

**State** ：状态

**Action**：

**Policy**：根据观测到的状态做出决策来控制运动 Π(a|s) = P(A = a | S = s) ，就是给定状态S做出动作A的概率密度。强化学习学的就是policy函数。游戏中：策略随机

**State transition**：S1 -> action1 -> S2 (获得r1) -> 做action2,得到s1 a1 r1,s2 a2 r2 ... st at rt.

**Reward**：奖励（定义的好坏非常影响结果）

**Return**: 由于未来的奖励没有现在的值钱，使用折扣回报(discounted return γ) 
$$
\vec{U}_{t}=R_{t}+\gamma R_{t+1}+\gamma^{2} R_{t+2}+\gamma^{3} R_{t+3}+...
$$

γ为0，1之间，越久远的未来折扣越大权重越低

Ut是随机变量（在t时刻不知道是什么），可以求期望。如抛硬币知道正反有一半概率而不知道下一个会得到什么。

**Action Value Function**：
$$
Action\ Value \ Function: \ Q_{\pi}\left(s_{t}, a_{t}\right)=\mathbb{E}\left[U_{t} \mid S_{t}=s_{t}, A_{t}=a_{t}\right]
$$
意义：如果用Policy函数Π，在St状态下at是好还是坏。QΠ 会给当前状态下的所有action打分。

**Optimal action-value function**：

将上一个式子中的Π去掉：（有无数种policy函数，将此函数最大化）
$$
Q^{\star}\left(s_{t}, a_{t}\right)=\max _{ \pi} Q_{\pi}\left(s_{t}, a_{t}\right)
$$
意义：St状态下，评价at动作的好坏。

**State-value function**:
$$
\begin{array}{l}
V_{\pi}\left(s_{t}\right)=\mathbb{E}_{A}\left[Q_{\pi}\left(s_{t}, A\right)\right]=\sum_{a} \pi\left(a \mid s_{t}\right) \cdot Q_{\pi}\left(s_{t}, a\right) . \quad \text { (discrete.) }\\
V_{\pi}\left(s_{t}\right)=\mathbb{E}_{A}\left[Q_{\pi}\left(s_{t}, A\right)\right]=\int \pi\left(a \mid s_{t}\right) \cdot Q_{\pi}\left(s_{t}, a\right) d a \cdot \text { (continuous.) }
\end{array}
$$
意义：可以表达出当前的局势好不好，局势越好VΠ越大；也可以评价Π的好坏，Π越好，VΠ的平均值越大。（VΠ和policy和状态有关，对a做运算）

<img src="https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210511195545028.png" alt="常用符号" style="zoom: 50%;" />

### 2、结合我们：
我们的目标：提升用户QoE

写程序让AI控制cache系统决定：1. whether to cache 2. which object to evict

两种办法：

- **Policy-based-learning** 学习一个policy函数Π，用policy控制agent做动作，每观测到一个状态st，作为Π函数的输入，会输出每一个动作的概率，按照概率做随机抽样得到at控制agent做动作。

- **Value-based-learning**，学习的是Optimal action-value ：Q*(s,a)。将当前状态St作为输入，对于每一个动作action都做一个评价，选择Q值最大的来做：
  $$
  a_{t}=\operatorname{argmax}_{a} Q^{\star}\left(s_{t}, a\right)
  $$

## Part Two -- Value-based learning (DQN + TD)

其实就是用神经网络近似Q*函数。
$$
Q^{\star}\left(s_{t}, a_{t}\right)=\max _{\pi} \mathbb{E}\left[U_{t} \mid S_{t}=s_{t}, A_{t}=a_{t}\right]
$$

### 1、Deep Q-Network (DQN)

神经网络Q(s,a;w)：输入为状态，参数是w，输出是对每一个动作的打分。

state -Conv卷积层-> feature 特征向量 - Dense全连接层-> 输出打分

利用DQN算法的过程：

![image-20210512223412039](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210512223412039.png)

### 2、如何训练DQN -- 用TD算法(Temporal Difference)

整体流程：

a. 当前状态St和当前动作At

b. Qt = Q(s,a;w), Qt 是神经网络的输出，是对每个状态的打分

c. 反向传播求导，PyTorch和TF都可以自动求梯度：
$$
\mathbf{d}_{t}=\left.\frac{\partial Q\left(s_{t}, a_{t} ; \mathbf{w}\right)}{\partial \mathbf{w}}\right|_{\mathbf{w}=\mathbf{w}_{t}}
$$
d. 环境更新成状态St+1和奖励Rt

e. 求TD target：
$$
TD \ target:
\begin{aligned}
y_{t} &=r_{t}+\gamma \cdot Q\left(s_{t+1}, a_{t+1} ; \mathbf{w}_{t}\right) \\
&=r_{t}+\gamma \cdot \max _{a} Q\left(s_{t+1}, a ; \mathbf{w}_{t}\right)
\end{aligned}
$$
f. 梯度下降更新权重
$$
\text { Gradient descent: } \mathbf{w}_{t+1}=\mathbf{w}_{t}-\left.\alpha \cdot \frac{\partial L_{t}}{\partial \mathbf{w}}\right|_{\mathbf{w}=\mathbf{w}_{t}}
$$

整个过程 = 两个过程相加(TD)
$$
Q\left(s_{t}, a_{t} ; \mathbf{w}\right) \approx r_{t}+\gamma \cdot Q\left(s_{t+1}, a_{t+1} ; \mathbf{w}\right)
$$

## Part Three-- Policy-based learning (Policy network + Policy gradient)

### 1、policy network

**Π(a|s)**：概率密度函数，表示当前状态时某一个action的概率（输入是s)

用**神经网络**近似policy函数**Π(a|s)**，神经网络记作：**Π(a|s;θ)**

state -Conv卷积层-> feature 特征向量 -Dense全连接层-> action个数的向量 -> Softmax激活函数 -> 每一个action的概率

通过神经网络学习的Π可以得到V：
$$
V\left(s_{t} ; \boldsymbol{\theta}\right)=\sum_{a} \pi\left(a \mid s_{t} ; \boldsymbol{\theta}\right) \cdot Q_{\pi}\left(s_{t}, a\right)
$$
策略学习的主要思想：改进模型参数θ让V变大，使得**J(θ)越大越好**。-> policy gradient ascent
$$
J(\boldsymbol{\theta})=\mathbb{E}_{S}[V(S ; \boldsymbol{\theta})]
$$

- state s

- $$
  Update \ policy \ \boldsymbol{\theta} \leftarrow \boldsymbol{\theta}+\beta \cdot \frac{\partial V(s ; \boldsymbol{\theta})}{\partial \boldsymbol{\theta}}
  $$

### 2、Policy Gradient

### 3、Update policy network using policy gradient

a. t时间的状态St

b. 用Π(a|s;θ)随机抽取得到action At

c. 计算价值函数Qt = QΠ(St,At)

- 策略网络控制agent运动，记录agent的轨迹和reward，得到Ut来近似QΠ
- 或者用神经网络来进行函数近似。

d. 求导得到d_θt

e. 近似计算策略梯度

f. 用近似的策略梯度更新策略网络的参数

![image-20210513224336282](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210513224336282.png)



## Part Four -- Actor-critic method

actor：策略网络，相当于运动员

critic：value network，相当于裁判员

输出的实数q是裁判对运动员打的分数。s的情况下，做action A 是好还是坏。

![image-20210515102228710](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210515102228710.png)

### Train the networks

学习两个神经网络的目的：

- policy network：让运动员得到更高的平均分，更新Π函数，让V函数的值更大。
  $$
  V(s ; \boldsymbol{\theta}, \mathbf{w})=\sum_{a} \pi(a \mid s ; \boldsymbol{\theta}) \cdot q(s, a ; \mathbf{w})
  $$

- value network：q函数当作裁判，给运动员打分越来越精准。

训练中，q函数辅助训练Π，训练后，q函数就没用了，通过Π来操作agent运动。

训练两个神经网络的更新方法：

1. 观察当前状态s
2. 根据策略函数对action进行概率分布，随机取得action
3. 做action更新当前状态St+1得到reward Rt
4. TD 算法更新value network的w。（裁判更准确）
5. policy gradient算法更新policy network 中的θ。

算法的总体流程：（每一轮只做一个动作，更新一次神经网络）

![image-20210515105723769](https://littlefisher.oss-cn-beijing.aliyuncs.com/images/image-20210515105723769.png)

## Part Five -- AlphaGo

主要设计思路：

- behavior cloning（模仿学习，非强化学习，监督学习，多分类/回归，将361个状态看成361个类别，计算每种类别的概率，人真实的动作就是标签）
- police gradient算法训练策略网络（策略网络做自我博弈）
- 训练一个价值网络评价状态的好坏（先训练策略网络，再用他训练价值网络）
- 蒙泰卡罗搜索树，用两个网络指导搜索来剪枝（策略函数算概率值，排除概率值低的，自我博弈通过胜负和reward给动作打分，选择分数高的）

其他了解：


强化学习和监督学习、无监督学习 最大的不同就是不需要大量的“数据喂养”。而是通过自己不停的尝试来学会某些技能。[链接](https://easyai.tech/ai-definition/reinforcement-learning/)

两种强化学习的主流算法：

1. 有模型学习（Model-Based）对环境有提前的认知，可以提前考虑规划，但是缺点是如果模型跟真实世界不一致，那么在实际使用场景下会表现的不好。
2. 免模型学习（Model-Free）放弃了模型学习，在效率上不如前者，但是这种方式更加容易实现，也容易在真实场景下调整到很好的状态。所以**免模型学习方法更受欢迎，得到更加广泛的开发和测试。**



