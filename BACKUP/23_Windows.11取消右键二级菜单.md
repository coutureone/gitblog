# [Windows 11取消右键二级菜单](https://github.com/coutureone/gitblog/issues/23)

因为不习惯`Windows11`鼠标右键反人类的二级菜单方式，采用命令的方式给屏蔽掉

修改成`Windows10`样式

**搜索`CMD`，然后点击管理员运行**

```改win10：
reg add "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /f /ve
```

<!--more-->
**然后回车执行，会提示`successful`**

**然后去任务管理里面去重启`Windows资源管理器`**

![](https://s2.loli.net/2023/07/21/p3aCJT6njeslfFH.png)

**重启完成以后打开，鼠标右键如下，成功**

![](https://s2.loli.net/2023/07/21/vxnXSlNf8Hp7zsk.png)

如果想改回原始的，命令如下，重复上面一样的操，作执行`命令`->`重启Windows资源管理器`

`Windows11`命令：

```bash
reg delete "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" /f
```

