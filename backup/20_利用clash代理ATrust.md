# [利用clash代理ATrust](https://github.com/coutureone/gitblog/issues/20)



> 折腾仅仅不是为了喜欢，而是更好的实现自己的需求。

&ensp;最近发现深信服`ATrust`这个软件有点变态，可能是因为网络隧道软件都需要拿去root权限，但是你拿到root权限我能理解，但是不让我关闭是什么意思，然后就开始让我产生了要给这个软件替换掉的想法，我找了很多方式好像都不能给这个软件给替换掉，既然无法替换，我就像能不能通过虚拟机的方式进行跑呢，开虚拟机也不是不可以，但是我的电脑内存只有16G,如果虚拟机开起来，看似解决问题，但是笔记本的电量疯狂的掉，于是去GitHub上面开始找解决方案，还真的有大佬给atrust这个软件打包好了docker的形式，然后就有了想法。

&ensp;看到issues里面有人提到了，通过clash代理访问校园网，那不正是我的业务需求吗，然后就开始用docker的形式，我的电脑是m1pro，docker我是通过OrbStack管理，通过OrbStack的好处就是占用很低，我的docker运行命令如下，必须要开启tun模式：

```bash
docker run --rm --device /dev/net/tun --cap-add NET_ADMIN -ti -e PASSWORD=xxxx -e URLWIN=1 -v $HOME/.atrust-data:/root -p 127.0.0.1:5901:5901 -p 127.0.0.1:1080:1080 -p 127.0.0.1:8888:8888 -p 127.0.0.1:54631:54631 --sysctl net.ipv4.conf.default.route_localnet=1 hagb/docker-atrust
```

&ensp;其实整个运行的命令就是参考[docker-easyconnect](https://github.com/docker-easyconnect/docker-easyconnect)项目的运行命令，具体参数就可以参考项目的文档，根据自己的需求改改，mac自带的有vnc链接，`vnc://127.0.0.1:5901`回车就行，密码是xxxx，这些都可以根据你的实际需求进行修改，然后需要在clash配置文件中这样修改：

```yml
- name: 内网
    type: socks5
    server: 127.0.0.1
    port: 1080
    udp: true
    
proxy-groups:
  - name: 内网代理
    type: select
    proxies: 
      - 直连
      - 内网
      
nameserver-policy:
   https:// xxx.xxx.xx:  # 这里就是你内外的sslvpn的地址
      - https://doh.pub/dns-query
    "xxxx.xxx.xxx":  # 访问域名
      - x.x.x.x     # 你内网dns，有的没有就不需要
      
rules:
  - DOMAIN,xx.xx.xx.xx,DIRECT
  - IP-CIDR,192.168.0.0/8,内网代理,no-resolve # 仅仅举例，根据实际内网网段进行修改
  - DOMAIN-SUFFIX,xx.xx.xx,内网代理       # 内网的域名 xx.xx.xx
```

&ensp;以上就是我内网的配置，我是按照我的实际需求进行修改的，可根据实际需求进行修改。

&ensp;代理工具我是[clash-party](https://github.com/mihomo-party-org/clash-party)，感觉还挺好用，推荐一下。

&ensp;最后鸣谢这[docker-easyconnect](https://github.com/docker-easyconnect/docker-easyconnect)、[clash-party](https://github.com/mihomo-party-org/clash-party)这两个开源项目，以及对项目所有贡献的开发者们。