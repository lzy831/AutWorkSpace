# 硬件清单

## DUT

| 项目 | 值 |
|------|-----|
| Device ID | `qurradc1816d12f3c1a` |
| 平台 | GTV/ATV |
| 系统 | Android TV (`com.android.tv.settings`) |
| 以太网接口 | eth0, MAC 02:ad:46:01:db:82 |
| 连接方式 | USB-ADB 直连 Controller |

## Controller

Controller 是通过 USB-ADB 直接连接 DUT 的设备，负责执行测试指令。

| 项目 | 当前值 | 后续可能 |
|------|--------|---------|
| 设备类型 | Linux PC (Ubuntu 24.04) | Android 设备 |
| 有线网卡 | enp0s31f6, 10.138.8.178 | — |
| 无线网卡 | wlp5s0, 192.168.50.136 | — |
| 职责 | ADB 控制 DUT、发 IPv6 RA、SSH 操作路由器 | ADB 控制 DUT、蓝牙遥控 DUT |
| 连接自动化系统 | 以太网 (10.138.8.178) | 以太网 |

> send_ra_v2 依赖 Linux raw socket + sudo，无法在 Android Controller 上运行。IPv6 RA 方案需要重新设计。

## Router

| 项目 | 值 |
|------|-----|
| 型号 | ASUS RT-AX86U |
| 固件 | ASUSWRT (Buildroot 2017.11.1, Linux 4.1.52, aarch64) |
| IP | 192.168.50.1 |
| SSH | AX86U / New!123456 |
| WiFi SSID | AX86U / Home1357 (5GHz) |
| IPv6 | 当前 ipv6pt (passthrough)，手动添加 ULA fd00::1/64 |

## 网线

| 连接 | 说明 |
|------|------|
| DUT eth0 ↔ Router LAN eth2 | 测试主链路 |
| Controller ↔ 公司网络 | enp0s31f6 |
