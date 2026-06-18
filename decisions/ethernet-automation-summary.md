# Ethernet 自动化用例汇总

## 环境设备
- AUT Server: 任务分发/结果收集
- Controller: USB-ADB 连接 DUT
- Router (ASUS RT-AX86U): 被测网络设备
- Aux Device (Router Client): AUX 模式远程控制 Router
- iperf Tester (Linux PC): 性能/稳定性测试

## auto (已实现) — 28 个

所有 auto 用例 precondition 统一为：`step_ensure_awake` → `step_enable_ethernet`(从异常恢复) → `step_ensure_router_lan_up` → `check_ethernet_connected`。

| # | 分类 | 内容 | 断连方式 | 设备依赖 | Minimal |
|---|------|------|----------|---------|---------|
| Func_001 | DHCP | DHCP 模式下获取 IPv4 地址 | — | AUT Server, Controller, Router, Aux | |
| Func_002 | DHCP | DHCP 模式下 DUT 侧 ip link 拔插后 IP 恢复 | `step_disable/enable_ethernet` | AUT Server, Controller, Router, Aux | ✅ |
| Func_003 | DHCP | DHCP 模式下 DUT 断电重启后 IP 自动恢复 | — | AUT Server, Controller, Router, Aux | ✅ |
| Func_004 | DHCP | DHCP 模式下路由器 LAN 口拔插后 IP 恢复 | `step_disconnect/connect_router_lan` | AUT Server, Controller, Router, Aux | |
| Func_005 | DHCP | DHCP 模式下路由器重启后 DUT 自动重连 | — | AUT Server, Controller, Router, Aux | |
| Func_006 | DHCP | DHCP 模式下待机唤醒后网络自动恢复 | — | AUT Server, Controller, Router, Aux, BT RCU | ✅ |
| Func_007 | Static | 静态 IP 模式设置成功 | — | AUT Server, Controller, Router, Aux | ✅ |
| Func_008 | Static | Static 模式下 DUT 侧 ip link 拔插后 IP 恢复 | `step_disable/enable_ethernet` | AUT Server, Controller, Router, Aux | |
| Func_009 | Static | Static 模式下 DUT 断电重启后 IP 保持不变 | — | AUT Server, Controller, Router, Aux | |
| Func_010 | Static | Static 模式下路由器 LAN 口拔插后 IP 恢复 | `step_disconnect/connect_router_lan` | AUT Server, Controller, Router, Aux | |
| Func_011 | Static | 静态 IP 模式下路由器重启后 DUT 恢复连接 | — | AUT Server, Controller, Router, Aux | ✅ |
| Func_012 | Static | Static 模式下待机唤醒后 IP 恢复 | — | AUT Server, Controller, Router, Aux, BT RCU | |
| Func_013 | Static | 设置无效静态 IP 时系统报错 | — | AUT Server, Controller | ✅ |
| Func_014 | Static | 以太网从 DHCP 切换到静态 IP | — | AUT Server, Controller, Router, Aux | ✅ |
| Func_040 | IPv6 | 双栈网络(IPv4 + IPv6)地址获取 | — | AUT Server, Controller, Router, Aux | ✅ |
| Func_041 | IPv6 | 双栈网络下热插拔网线后 IP 恢复 | `step_disconnect/connect_router_lan` | AUT Server, Controller, Router, Aux | ✅ |
| Func_042 | IPv6 | IPv6 双栈下 DUT 重启后 IP 恢复 | — | AUT Server, Controller, Router, Aux | ✅ |
| Func_043 | IPv6 | 双栈网络下路由器重启后 IP 恢复 | — | AUT Server, Controller, Router, Aux | ✅ |
| Func_044 | IPv6 | IPv6 双栈下待机唤醒后 IP 恢复 | — | AUT Server, Controller, Router, Aux, BT RCU | |
| new_007 | MDIX | Auto MDIX 直连线正常连接 | — | AUT Server, Controller, Router, Aux | |
| Throughout_001 | Perf | TCP 10M RX 吞吐量 | — | AUT Server, Controller, Router, iperf Tester | |
| Throughout_002 | Perf | TCP 10M TX 吞吐量 | — | AUT Server, Controller, Router, iperf Tester | |
| Throughout_003 | Perf | TCP 100M RX 吞吐量 | — | AUT Server, Controller, Router, iperf Tester | |
| Throughout_004 | Perf | TCP 100M TX 吞吐量 | — | AUT Server, Controller, Router, iperf Tester | |
| Throughout_007 | Perf | UDP 10M RX 吞吐量 | — | AUT Server, Controller, Router, iperf Tester | |
| Throughout_008 | Perf | UDP 10M TX 吞吐量 | — | AUT Server, Controller, Router, iperf Tester | |
| Throughout_009 | Perf | UDP 100M RX 吞吐量 | — | AUT Server, Controller, Router, iperf Tester | |
| Throughout_010 | Perf | UDP 100M TX 吞吐量 | — | AUT Server, Controller, Router, iperf Tester | |

## pending (待实现) — 4 个

| # | 分类 | 内容 | 设备依赖 | 待实现 step/check |
|---|------|------|---------|------------------|
| Stab_001 | Stability | iperf 测试 12h (10M) | AUT Server, Controller, Router, iperf Tester | iperf step/check |
| Stab_002 | Stability | 在线播放视频 12h (10M) | AUT Server, Controller, Router | 播放器 + 长跑框架 |
| Stab_003 | Stability | Ping 12h (Super 5 100M) | AUT Server, Controller, Router | 长跑框架 |
| Stab_004 | Stability | autosuspend + ping 12h | AUT Server, Controller, Router | autosuspend APK + 长跑框架 |

## manual (不实现) — 38 个
PPPOE 015-039 (25), Network switching 015-019 含 PPPOE, Compatibility (6), new_function_002 peer PC, new_function_006 MDIX crossover, Throughout_005/006/011/012 1000M (DUT 不支持千兆)
