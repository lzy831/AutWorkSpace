# Ethernet Performance (iperf) 用例设计决策

## 环境

```
DUT(GTV/ATV) ──eth0── Router(AX86U) ──LAN── Linux PC(enx00e04b165e48, 192.168.50.85)
     │                        │                        │
     │ USB-ADB                │ SSH(AUX)               │ SSH(AUX, iperf_aux_id)
     ▼                        ▼                        ▼
Controller(Android)    Router Client(AUX)        iperf Tester(AUX)
```

- DUT ARM32, iperf bin: `iperf2`（ARM32, v2.0.5, 动态链接）, push 到 `/data/local/tmp/iperf`
- Linux PC x86_64, iperf: `/usr/bin/iperf`（v2.1.9）
- iperf Tester 和 Router Client 共用同一台 Linux PC，通过不同的 AUX role 区分

## 用例角色

| 类型 | DUT 角色 | iperf Tester 角色 |
|------|----------|-------------------|
| RX (001/003/005/007/009/011) | server | client |
| TX (002/004/006/008/010/012) | client | server |

## 控制通道

| 设备 | 控制方式 |
|------|----------|
| DUT | Controller USB-ADB |
| iperf Tester (Linux PC) | AUX `run_shell` action（`subprocess.Popen` 本地执行），通过 `iperf_aux_id` 标识 |
| Router | AUX `execute` action → `Router.execute()` → SSH router |

### AUX 框架通信路径

```
DevMgrUtil API           DevMgr (WebSocket)         AUX Client on Linux PC
═══════════              ═══════════════            ════════════════════════
execute()    ──→  action:"execute"    ──→  __on_action_execute → g_router.execute() → SSH router
run_shell_via() ──→  action:"run_shell"  ──→  __on_action_run_shell → run_command() → subprocess.Popen() 本地
```

- `execute`: RouterClient 专用，用于路由器管理命令
- `run_shell`: 所有 AUX client 通用，用于在 AUX 设备本地执行 shell 命令
- iperf 控制走 `run_shell`，`iperf_aux_id` 暂用 `Router_nanjing_aut_laptop`

### iperf 启动方式（daemon 模式）

`run_shell_via` 的 `wsc.recv()` 是同步阻塞的（等待命令执行完），而 iperf 测试时长 300s，必须使用 `_daemon=True`：

```bash
# Server: daemon 启动，立即返回 PID
iperf -s -p 5001  &>/dev/null     # 后台运行

# Client: daemon 启动，输出重定向到文件
iperf -c <IP> -w 10M -t 300 > /tmp/iperf_result.txt 2>&1  # 后台运行
```

测试结束后从 `/tmp/iperf_result.txt` 解析吞吐量，用 `aux_command_stop` 按 PID 杀掉进程。

iperf_aux_id 暂用 `Router_nanjing_aut_laptop`（与 Router Client 共用 PC），通过 custom_params 传入。

## 用例清单 (12 个)

| # | 协议 | 带宽 | 方向 | DUT 角色 | 期望阈值 |
|---|------|------|------|----------|----------|
| Throughput_001 | TCP | 10M | RX | server | 9Mbits/sec |
| Throughput_002 | TCP | 10M | TX | client | 9Mbits/sec |
| Throughput_003 | TCP | 100M | RX | server | 90Mbits/sec |
| Throughput_004 | TCP | 100M | TX | client | 90Mbits/sec |
| Throughput_005 | TCP | 1000M | RX | server | 900Mbits/sec |
| Throughput_006 | TCP | 1000M | TX | client | 800Mbits/sec |
| Throughput_007 | UDP | 10M | RX | server | 9Mbits/sec |
| Throughput_008 | UDP | 10M | TX | client | 9Mbits/sec |
| Throughput_009 | UDP | 100M | RX | server | 90Mbits/sec |
| Throughput_010 | UDP | 100M | TX | client | 90Mbits/sec |
| Throughput_011 | UDP | 1000M | RX | server | 800Mbits/sec |
| Throughput_012 | UDP | 1000M | TX | client | 600Mbits/sec |

测试时长: 300s (5min)

## 已验证

- [x] DUT iperf: push `iperf2` → `/data/local/tmp/iperf`, v2.0.5 ARM32 ✅
- [x] PC iperf: `/usr/bin/iperf` v2.1.9, 兼容 `-w`/`-u`/`-b` 参数 ✅
- [x] AUX `run_shell` daemon 模式启动/停止 iperf ✅
- [x] AUX `run_shell` 同步模式获取 client 输出（3-30s 短测试）✅
- [x] 双方向 (TX/RX) 端到端 iperf 通信 ✅
- [x] `sh -c "..."` 包裹复杂 shell 命令（重定向、管道）✅
- [x] `kill <PID>` 停止进程（`stop_shell` 超时限制）✅
- [x] **TX 长时（30s）**: ADB iperf client 同步阻塞，stdout 捕获输出 ✅
- [x] **RX 长时（30s）**: AUX daemon client 写文件，定时 `cat` 读取 ✅

### 最终执行方案

**TX (DUT client, PC server)**: ADB 直接同步阻塞，无需 daemon
```
1. AUX daemon → iperf -s on PC (后台)
2. ADB → iperf -c PC_IP -t 300 on DUT (阻塞 300s, 捕获 stdout)
3. Parse stdout → check_iperf_throughput
4. AUX → kill <PID>
```

**RX (DUT server, PC client)**: AUX daemon client 写文件
```
1. ADB → iperf -s on DUT (后台)
2. AUX daemon → sh -c "iperf -c DUT_IP -t 300 > /tmp/iperf_rx.txt" on PC
3. Step: wait 310s
4. AUX → cat /tmp/iperf_rx.txt → check_iperf_throughput
5. ADB → killall iperf
```

## 待实现

- [ ] step_iperf_start / step_iperf_stop (lib + atomic)
- [ ] check_iperf_throughput (lib + atomic)
- [ ] 12 个 Throughput YAML spec
- [ ] 环境定义更新（iperf_tester role）
