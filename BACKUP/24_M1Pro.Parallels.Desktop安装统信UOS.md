# [M1Pro Parallels Desktop安装统信UOS](https://github.com/coutureone/gitblog/issues/24)

## 1.下载镜像

点击下载连接[[UOS](https://www.chinauos.com/resource/download-professional)](https://www.chinauos.com/resource/download-professional)，选择下面的镜像，其他版本无法安装。

![](https://s3.qjqq.cn/50/67471bafee086.webp!color)

## 2.安装系统

#### 2.1选择刚才下载好的镜像

![](https://s3.qjqq.cn/50/67471c071f117.webp!color)

#### 2.2手动选则

![](https://s3.qjqq.cn/50/67471c526a99c.webp!color)

#### 2.3出现下面这个选择`继续`

![](https://s3.qjqq.cn/50/67471c8576019.webp!color)

#### 2.5选择其他`Linux`

![image-20241127212100721](https://s3.qjqq.cn/50/67471cbdb6c07.webp!color)

#### 2.6 然后`继续`，创建，选择第一个安装即可，这里过程省略，过于简单

![](https://s3.qjqq.cn/50/67471d1a291fd.webp!color)

## 3.安装 `Parallels Tools`

这时候你需要进入`root`模式下，关于如何进入`root`模式请看我的另一篇文章

#### 3.1进入root模式以后，首先就挂载`Parallels Tools`，点击安装以后自动挂载。

![](https://s3.qjqq.cn/50/67471e2276470.webp!color)

#### 3.2在计算机里面可以看到挂载好的工具，双击打开，选择空白处，用终端打开。

![](https://s3.qjqq.cn/50/67471e7765012.webp!color)

下图所示：

![](https://s3.qjqq.cn/50/67471eb9557dd.webp!color)

#### 3.5设置里面安装任意应用需要打开，否则终端会报错

```bash
Coutrue@CoutrueUOS:/media/Coutrue/Parallels Tools$ 
Coutrue@CoutrueUOS:/media/Coutrue/Parallels Tools$ sudo -s
请输入密码:
验证成功
root@CoutrueUOS:/media/Coutrue/Parallels Tools# ./install
```

![](https://s3.qjqq.cn/50/67471f2d93011.webp!color)



#### 3.6执行完成以后一路next即可，一直到回车重启。

![](https://s3.qjqq.cn/50/67471f7ca4709.webp!color)

#### 3.7当桌面出现`Parallels Shared Folders`，说明安装成功，和Mac之间相互已经打通了。

![](https://s3.qjqq.cn/50/6747207594d96.webp!color)