# [关于MosDNS没有轮转机制解决方案](https://github.com/coutureone/gitblog/issues/47)

> 最近在折腾网络过程中，因为采用了`mosdns`进行分流，但是发现突然发现终端设备突然获取不到`IP`地址了，排查了好几天，才发现`MosDNS`没有轮转机,导致我软路由的内存直接溢出，然后借用`codex`写了一个删除日志的机制，摆脱内存溢出的问题。

当前安装的日志保护脚本位于：

```bash
/usr/sbin/mosdns-log-guard
```

内容如下：

```shell
#!/bin/sh

LOG_FILE="${LOG_FILE:-/var/log/mosdns.log}"
MAX_SIZE="${MAX_SIZE:-5242880}"
INTERVAL="${INTERVAL:-30}"

check_log() {
	[ -f "$LOG_FILE" ] || return 0

	SIZE="$(wc -c < "$LOG_FILE" 2>/dev/null)"
	case "$SIZE" in
		''|*[!0-9]*) return 0 ;;
	esac

	if [ "$SIZE" -gt "$MAX_SIZE" ]; then
		logger -t mosdns-log-guard \
			"mosdns log reached ${SIZE} bytes; truncating at limit ${MAX_SIZE}"
		: > "$LOG_FILE"
	fi
}

if [ "$1" = "--once" ]; then
	check_log
	exit 0
fi

while true; do
	check_log
	sleep "$INTERVAL"
done
```

参数含义：

```
日志文件：/var/log/mosdns.log
日志上限：5242880字节，即5 MiB
检查间隔：30秒
```

对应的开机服务位于：

```
/etc/init.d/mosdns-log-guard
```

内容如下：

```bash
#!/bin/sh /etc/rc.common

START=76
STOP=10
USE_PROCD=1

PROG=/usr/sbin/mosdns-log-guard

start_service() {
	procd_open_instance
	procd_set_param command "$PROG"
	procd_set_param respawn 3600 5 5
	procd_set_param file "$PROG"
	procd_close_instance
}
```

手动检查一次可以运行：

```bash
/usr/sbin/mosdns-log-guard --once
```

查看服务状态：

```bash
ubus call service list '{"name":"mosdns-log-guard"}'
```

查看是否开机启用：

```bash
/etc/init.d/mosdns-log-guard enabled
```

查看保护服务产生的系统日志：

```bash
logread | grep mosdns-log-guard
```