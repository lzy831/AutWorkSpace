# Ethernet Step & Check 清单

> **维护规则**：新增或修改 step/check 时同步更新本文档。

## 架构层次

| 层次 | 路径 | 面向对象 |
|------|------|----------|
| **atomic 层**（接口） | `scripts/python/atomic/step_impl/peripheral/network/ethernet/` | workflow JSON 引用 |
| **atomic 层**（接口） | `scripts/python/atomic/check_impl/peripheral/network/ethernet/` | workflow JSON 引用 |
| **实现层** | `scripts/python/lib/common/peripheral/network/ethernet/` | atomic 层调用 |

> 提及 "step" / "check" 默认指 atomic 层。

---

## Step 清单

| Step | 功能 | 用例数 | 实现方式 | 默认 |
|------|------|:--:|------|:--:|
| `step_ensure_ethernet_link` | 确保 DUT 以太网物理链路连通（路由器 LAN 口上电） | 11 | SSH (RouterManager) | — |
| `step_set_ip_settings_to_dhcp` | Settings UI → IP Settings → DHCP | 6 | UI | — |
| `step_discover_network_info` | 采集 gateway/subnet/dns/static_ip/prefix | 5 | CMD (EthernetManager) | — |
| `step_set_static_ip` | Settings UI → IP Settings → Static → Wizard 填写 5 步 | 3 | UI | — |
| `step_disconnect_ethernet` | 路由器 SSH → 对 DUT LAN 口 PHY 断电 | 2 | SSH (RouterManager) | — |
| `step_connect_ethernet` | 路由器 SSH → 对 DUT LAN 口 PHY 上电 | 2 | SSH (RouterManager) | — |
| `step_reboot_router` | SSH reboot + wait_down + wait_online | 1 | SSH (RouterManager) | — |
| `step_set_static_ip_invalid` | Settings UI → 输入无效 IP，触发系统校验 | 1 | UI | — |
| `step_connect_ethernet_dhcp` | `ip link up eth0` + DHCP 获取 IP | 1 | CMD (EthernetManager) | — |
| `step_enable_ethernet` | `ip link set eth0 up` | 0 | CMD (EthernetManager) | — |
| `step_disable_ethernet` | `ip link set eth0 down` | 0 | CMD (EthernetManager) | — |
| `step_verify_ethernet` | 升级后验证（link + IP + ping 8.8.8.8） | 0 | CMD | — |
| `step_clear_pppoe_password_field` | 清除 PPPoE 密码输入框内容 | 0 | CMD (keyevent) | — |
| `step_download_apk_from_network` | Controller 下载 APK → adb push | 0 | CMD + adb | — |

## Check 清单

| Check | 功能 | 用例数 | 实现方式 | 默认 |
|------|------|:--:|------|:--:|
| `check_ethernet_connected` | 验证以太网已连接 | 18 | cmd / **ui** | ui |
| `check_ethernet_dual_stack_ip_obtained` | 验证 eth0 同时有 IPv4 + IPv6（非 link-local） | 4 | CMD | — |
| `check_ethernet_disconnected` | 验证以太网已断开 | 2 | cmd / **ui** | ui |
| `check_ethernet_ip_mode` | 验证 IP 模式（dhcp/static），可选校验具体 IP | 2 | UI + CMD | — |
| `check_network_connected` | 通用验证网络已连（ethernet/wifi） | 2 | cmd / **ui** | ui |
| `check_network_accessible` | ping 目标验证网络可达 | 2 | CMD | — |
| `check_network_disconnected` | 通用验证网络已断（ethernet/wifi） | 1 | cmd / **ui** | ui |
| `check_prompt_invalid_ip` | 验证 UI 显示 "IP settings not valid" 错误提示 | 1 | UI | — |
| `check_ethernet_ip_assigned` | 验证 eth0 已分配 IPv4 地址 | 0 | CMD | — |
| `check_mac_address` | 验证 eth0 MAC 地址格式合法 | 0 | CMD | — |
| `check_network_connect_failed` | 验证网络连接失败（无 IP） | 0 | CMD | — |
