# [OpenClash+Mosdns+AdGuard+Atrust网络全打通](https://github.com/coutureone/gitblog/issues/35)


&ensp;因为自己的种种需求，所以产生了这个想法，在家实现内外网都是自由，而且不需要挂VPN软件，这个想法终于在经过自己不断折腾，终于落地了。

&ensp;基础操作就不说，怎么安装插件也不说，这些都是可以自行GitHub上面就可以的，都是开源的，主要是说一下自己的配置：

### OpenClash

运行模式肯定是tun模式，我个人也比较推荐这个模式

![](https://cdn.jsdelivr.net/gh/coutureone/gitblog@main/img/image-20260308144907897.png)

&ensp;本地DNS劫持选择禁用

![](https://cdn.jsdelivr.net/gh/coutureone/gitblog@main/img/image-20260308145009618.png)

&ensp;覆写设置里面就是自定义dns上游服务器勾选上，Nameserve和Fallback都是 127.0.0.1 端口号是你的mosdns端口号，我是默认5335，取决于你自己的设置。

![](https://cdn.jsdelivr.net/gh/coutureone/gitblog@main/img/image-20260308145625537.png)

&ensp;OpenClash的设置到这里基本差不多，订阅自行导入，这里不做过多赘述。

### MosDns

&ensp;我的建议是大家直接根据自己的需求配置，用AI进行补充调整，下面我的配置也只是仅供参考，因为我加了学校的内网配置，以及我的订阅代理代理需要解析，进行调整，否则tls加密无法解析到。

```yml
log:
  level: info
  file: /var/log/mosdns.log

api:
  http: 0.0.0.0:9091

include: []

plugins:
  # --- 1. 资源集定义 ---
  - tag: zjjs_domain
    type: domain_set
    args:
      files: ["/etc/mosdns/rule/zjjs_domain.txt"]
  - tag: geosite_cn
    type: domain_set
    args:
      files: ["/var/mosdns/geosite_cn.txt"]
  - tag: geoip_cn
    type: ip_set
    args:
      files: ["/var/mosdns/geoip_cn.txt"]
  - tag: geosite_apple
    type: domain_set
    args:
      files: ["/var/mosdns/geosite_apple.txt"]
  - tag: geosite_no_cn
    type: domain_set
    args:
      files: ["/var/mosdns/geosite_geolocation-!cn.txt"]
  - tag: whitelist
    type: domain_set
    args:
      files: ["/etc/mosdns/rule/whitelist.txt"]
  - tag: blocklist
    type: domain_set
    args:
      files: ["/etc/mosdns/rule/blocklist.txt"]
  - tag: greylist
    type: domain_set
    args:
      files: ["/etc/mosdns/rule/greylist.txt"]
  - tag: ddnslist
    type: domain_set
    args:
      files: ["/etc/mosdns/rule/ddnslist.txt"]
  - tag: hosts
    type: hosts
    args:
      files: ["/etc/mosdns/rule/hosts.txt"]
  - tag: redirect
    type: redirect
    args:
      files: ["/etc/mosdns/rule/redirect.txt"]
  - tag: adlist
    type: domain_set
    args:
      files: ["/etc/mosdns/rule/disable-ads.txt"]
  - tag: local_ptr
    type: domain_set
    args:
      files: ["/etc/mosdns/rule/local-ptr.txt"]
  - tag: stream_media
    type: domain_set
    args:
      files:
        - /var/mosdns/geosite_disney.txt
        - /var/mosdns/geosite_netflix.txt
        - /var/mosdns/geosite_hulu.txt
        - /etc/mosdns/rule/streaming.txt
  - tag: cloudflare_cidr
    type: ip_set
    args:
      files: ["/etc/mosdns/rule/cloudflare-cidr.txt"]
  - tag: proxy_node_domain
    type: domain_set
    args:
      files: ["/etc/mosdns/rule/proxy_nodes.txt"]

  # --- 2. 缓存与转发插件 ---
  - tag: lazy_cache
    type: cache
    args:
      size: 30000
      lazy_cache_ttl: 0
      dump_file: /etc/mosdns/cache.dump
      dump_interval: 3600

  # 教育网内网转发：通过 aTrust 容器 1080 端口
  - tag: forward_zjjs
    type: forward
    args:
      concurrent: 1
      upstreams:
        - addr: "tcp://10.10.1.236:53"
          socks5: "127.0.0.1:1080"

  # 国内转发：含纯 IP 引导破解 TLS 超时
  - tag: forward_local
    type: forward
    args:
      concurrent: 3
      upstreams:
        - addr: 223.5.5.5
        - addr: https://doh.pub/dns-query
          bootstrap: 119.29.29.29
        - addr: https://dns.alidns.com/dns-query
          bootstrap: 119.29.29.29

  # 国外转发：Socks5 7891 (Clash)
  - tag: forward_remote
    type: forward
    args:
      concurrent: 1
      upstreams:
        - addr: "https://dns.google/dns-query"
          bootstrap: "8.8.8.8"
          socks5: "127.0.0.1:7891"

  # --- 3. 响应处理序列 ---
  - tag: modify_ttl
    type: sequence
    args:
      - exec: ttl 5-600 # 优化缓存提升性能

  - tag: has_resp_sequence
    type: sequence
    args:
      - matches: has_resp
        exec: accept

  # --- 4. 核心主逻辑序列 ---
  - tag: main_sequence
    type: sequence
    args:
      - exec: $hosts
      - exec: jump has_resp_sequence
      # 破解代理节点死循环
      - matches: qname $proxy_node_domain
        exec: $forward_local
      - exec: jump has_resp_sequence

      # 缓存逻辑
      - matches:
          - "!qname $blocklist"
          - "!qname $adlist"
        exec: $lazy_cache
      - exec: jump has_resp_sequence

      # 分流判定
      - matches: qname $geosite_cn
        exec: $forward_local
      - exec: jump has_resp_sequence

      - matches: qname $geosite_no_cn
        exec: $forward_remote
      - exec: jump has_resp_sequence

      # 兜底
      - exec: $forward_local

  # --- 5. 服务监听 ---
  - tag: udp_server
    type: udp_server
    args:
      entry: main_sequence
      listen: ":5335"
  - tag: tcp_server
    type: tcp_server
    args:
      entry: main_sequence
      listen: ":5335"
```

&ensp;设置具体如下：

![](https://cdn.jsdelivr.net/gh/coutureone/gitblog@main/img/image-20260308150339538.png)



![](https://cdn.jsdelivr.net/gh/coutureone/gitblog@main/img/image-20260308150400040.png)

根据自己实际需求进行填写，我这也只是参考作用，给自己做一个备份。

### AdGuard

&ensp;主要是防止自己的端口冲突，这里可以自己设置，我是这样设置的，最主要的设置在内部的 DNS设置里面，不能写错了，下面是我的作为参考。

![](https://cdn.jsdelivr.net/gh/coutureone/gitblog@main/img/image-20260308150728839.png)

&ensp;DNS设置

![](https://cdn.jsdelivr.net/gh/coutureone/gitblog@main/img/image-20260308150910859.png)

&ensp;到这里其实设置的基本差不多了，还有一个最主要的没有设置，那就是网络里面的DCHP/DNS

### DHCP/DNS

![](https://cdn.jsdelivr.net/gh/coutureone/gitblog@main/img/image-20260308151225689.png)

&ensp;转发端口是AdGuard监听端口

![](https://cdn.jsdelivr.net/gh/coutureone/gitblog@main/img/image-20260308151451931.png)

&ensp;到这里基本就没啥问题了，ATrust其实我就不多介绍了，按照自己的实际需求来，参考GitHub项目[[docker-easyconnect](https://github.com/docker-easyconnect/docker-easyconnect)](https://github.com/docker-easyconnect/docker-easyconnect)，这个就可以了。

#### 特别鸣谢：

感谢[[乌龙蜜桃来一打](https://space.bilibili.com/244390800?spm_id_from=333.337.0.0)](https://space.bilibili.com/244390800?spm_id_from=333.337.0.0)
