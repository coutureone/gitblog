# [docker网络配置](https://github.com/coutureone/gitblog/issues/19)

  IPv4和IPv6都开启的情况

```json
{
  "registry-mirrors" : [
    "https:\/\/docker.1ms.run",
    "https:\/\/docker.m.daocloud.io"
  ],
  "insecure-registries" : [
    "https:\/\/docker.1ms.run",
    "https:\/\/docker.m.daocloud.io"
  ],
  "default-address-pools" : [
    {
      "base" : "172.16.0.0\/16",
      "size" : 24
    },
    {
      "base" : "fd07:b51a:cc66:d000::\/56",
      "size" : 64
    }
  ],
  "ipv6" : true,
  "fixed-cidr-v6" : "fd00:db8:1::\/64",
  "bip" : "172.16.0.1\/24"
}
```

