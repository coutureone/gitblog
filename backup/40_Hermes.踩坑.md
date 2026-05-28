# [Hermes 踩坑](https://github.com/coutureone/gitblog/issues/40)


连续对话提示：

```bash
Error: Session continuation requires API key authentication. Configure API_SERVER_KEY to enable this feature.
```

解决方式：

在Hermes的环境变量中需要添加两条配置文件

```bash
# 路径
.hermes/.env

API_SERVER_ENABLED=true
API_SERVER_KEY=你自己设置的密钥 # 最好是8为数字字符
```

然后重启网关，如果有桌面端就重启桌面端

```bash
hermes gateway restart
```





