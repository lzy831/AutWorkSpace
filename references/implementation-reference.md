# 实现参考

## SettingsNavigator 方法清单

`get_navigator()` → `SettingsNavigatorATV`:

| 方法 | 说明 |
|------|------|
| `open_settings()` | HOME → force-stop Settings → `am start .MainSettings` |
| `open_network_page()` | Settings → DOWN×2 → ENTER → Network & Internet |
| `open_ethernet_ip_settings()` | Settings → Network & Internet → Ethernet → IP Settings |
| `open_wifi_ip_settings()` | HOME → WIFI_SETTINGS → 已连 AP → 详情 → IP Settings |
| `select_dhcp_mode()` | IP Settings 页面 ENTER（DHCP 默认焦点） |
| `is_ethernet_connected()` | Network & Internet 页面含 "ETHERNET" |
| `is_ethernet_disconnected()` | Network & Internet 页面不含 "ETHERNET" |

## RouterManager API

```python
mgr = RouterManager(ip, username, password, model)
mgr.disconnect_device(mac)    # LAN 口 PHY 断电
mgr.connect_device(mac)       # LAN 口 PHY 上电
mgr.reboot(timeout=120)       # SSH reboot + wait_down + wait_online
mgr.ensure_device_port_up(mac) # 自动发现端口并上电
```

## cmd wifi 子命令

| 命令 | 用途 |
|------|------|
| `cmd wifi status` | 查询 WiFi 状态 |
| `cmd wifi connect-network <ssid> wpa2 <psk>` | 连接 WiFi |
| `cmd wifi set-wifi-enabled enabled\|disabled` | 开关 WiFi |
| `cmd wifi list-scan-results` | 扫描结果 |
| `cmd wifi list-networks` | 已保存网络 |
| `cmd wifi forget-network <id>` | 遗忘网络 |

## 已知限制

| 限制 | 说明 | 替代方案 |
|------|------|----------|
| `cmd wifi disconnect` 不可用 | 此设备 Android 不支持 | `forget-network` + off→on |
| APK `is_enable()` / `connect_ssid()` rc=1 | AMLWifi APK 部分异常 | 用 CMD 方式 |
| `ip route add` 与 netd 冲突 | Android netd 管理路由 | UI 模式通过 Settings |
| WiFi `ip addr add` 不改变系统 IP | netd 管理 WiFi IP | `step_set_wifi_static_ip(method="ui")` |
| `su -c` 不可用 | 此设备 su 不支持 | `adb root` 后直接执行 |
| AOSP 平台 UI 未实现 | 仅适配 GTV/ATV | 后续扩展 |

## Router IPv6 RA 方案

Controller 通过 `send_ra_v2` 工具发送 ICMPv6 RA 包到 WiFi 链路，广播 `fd00::/64` ULA 前缀。
详见 [decisions/2026-05-25-ra-via-controller.md](../decisions/2026-05-25-ra-via-controller.md)
