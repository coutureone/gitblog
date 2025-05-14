# [IPv6的一个小TIP](https://github.com/coutureone/gitblog/issues/13)

>纸上得来终觉浅，绝知此事要躬行

&ensp;今天和一个工程师探讨了一个IPv6的问题，IPV6对于设备分为两种的状态：

* IPV6有状态
* IPv6无状态

&ensp;有状态：安卓手机是不支持有状态的，手机无法直接获取到IPv6地址，但是iOS可以。

&ensp;无状态：安卓和苹果都是支持的，隔一段时间IPv6地址就会变。

&ensp;有状态可以理解为固定IP地址，无状态可以理解为不固定IP地址，IPv6地址会变动。

&ensp;如果想所有设备出局都走IPv6，可以无线做IPV4隧道，在AC做4 to 6就可以。

