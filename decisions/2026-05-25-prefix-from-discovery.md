# 设计决策: 网络参数必须动态发现

## 背景

早期以太网用例在 `--custom-params` 中传入 `eth_static_ip` 和 `eth_gateway` 等参数。
这种方式要求测试者提前知道可用的静态 IP、网关地址，且有 IP 冲突风险。

## 决定

所有网络参数（网关、子网、可用静态 IP、prefix 长度）**必须由 `step_discover_network_info` 动态发现**，禁止外部传入。

`step_discover_network_info` 的行为：
- 通过 `ip route` 发现当前网关
- 通过 `ip addr show eth0` 获取 prefix length
- 通过 `pick_static_ip()` ping 冲突检测选取可用静态 IP（从 .200 向上递增）

## 后果

- **得到**: 测试完全自包含，不需要外部环境知识；IP 冲突概率大幅降低
- **牺牲**: `pick_static_ip()` 的 ping 检测不是原子操作，极低概率的 TOCTOU 问题
