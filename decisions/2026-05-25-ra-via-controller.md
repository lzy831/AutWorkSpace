# 设计决策: 通过 Controller 发送 IPv6 RA

## 背景

测试 IPv6 双栈用例时，DUT 需要通过 SLAAC/DHCPv6 自动获取 global IPv6 地址。
当前路由器（ASUS RT-AX86U）固件缺少 RA（Router Advertisement）守护进程：
- dnsmasq 编译时未启用 RA 支持
- radvd 二进制不存在
- rc 二进制（闭源）仅在 WAN 口有真实 IPv6 时才会启动 RA

## 方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| A. 路由器装 radvd | 标准做法，兼容所有客户端 | 需交叉编译 aarch64 二进制；固件升级会丢失 |
| B. Controller 发 RA | 无需改动路由器固件；Python 可控 | 需 root 权限；非标准，依赖 Controller 在线 |
| C. DUT 静态 IPv6 | 最简单 | 无法测试 DHCPv6/SLAAC 自动获取场景 |
| D. 换支持 IPv6 的路由器 | 彻底解决 | 成本高 |

## 决定

选 **方案 B — Controller 发 RA**。

用 C 编译一个小工具 `send_ra_v2`，通过 `SO_BINDTODEVICE` 绑定 WiFi 接口 `wlp5s0`，构造 ICMPv6 RA 包发送到 `ff02::1`（链路所有节点），广播 `fd00::/64` 前缀。

## 后果

- **得到**: DUT 可通过 SLAAC 正常获取 IPv6 地址，IPv6 双栈用例可测试
- **牺牲**: RA 需要周期性发送（当前为一次性），后续需封装为自动化 step 或用 cron 定时
- **风险**: Controller 离线则 IPv6 不可用；在生产环境中此方案不可行，仅限测试
