# 本地测试运行指南

本文档说明在 Linux PC 本地服务器 (10.138.8.178) 上运行 ethernet/iperf 测试用例的方法。

## 测试环境拓扑

```
┌──────────────────────────────────────────────────────────┐
│ AUT 云 (10.58.120.88:8002)                               │
│  - DevMgr: 设备注册/调度                                  │
│  - 正式测试通过 web 页面操作                               │
└────────────┬─────────────────────────────────────────────┘
             │ 公司内网
┌────────────┴─────────────────────────────────────────────┐
│ Linux PC 本地服务器 (10.138.8.178)                        │
│  - Samba: Y:\AutoTestRes                                 │
│  - 角色1: 本地测试服务器 (运行 workflow_runner)             │
│  - 角色2: AUX Router Client (did=Router_nanjing_aut_laptop)│
│  - 角色3: AUX iperf Tester (did=Router_nanjing_aut_laptop) │
└──────┬────────────────────┬──────────────────────────────┘
       │ USB (直连模式)      │ 公司内网
       ▼                    ▼
     DUT              Controller (Android)
   (qurradc...)       USB-ADB ── DUT (Controller 模式)
         │                 │
         └──── 以太网 ─────┘
                  │
              Router (AX86U, 192.168.50.1)
                  │ LAN
         Linux PC enx00e04b165e48 (192.168.50.85, iperf 测试)
```

## DUT 连接模式

### 模式 A: 直连 (DUT USB → Linux PC)

DUT 通过 USB 线直接插在 Linux PC 上。ADB 直接可用。

```bash
ssh zhiyuan.liu@10.138.8.178
cd /home/zhiyuan.liu/AutoTestRes/scripts/python
source .venv/bin/activate

# --device-id = ADB serial (adb devices 显示的)
python3 atomic/workflow_runner.py \
  --workflow-path atomic/workflows/auto_generate/Ethernet_V1.3_test_case/Function/<case>.json \
  --device-id qurradc1816d12f3c1a \
  --custom-params '{...}'
```

### 模式 B: Controller 模式 (DUT USB → Controller)

DUT 通过 USB 线插在 Controller(Android 设备)上。Linux PC 通过 DevMgr 获取 ADB 端口映射。

```bash
# --device-id = AUT 云中的 ControllerID-DutHWID 组合
python3 atomic/workflow_runner.py \
  --workflow-path ... \
  --device-id 360c010100000000091e01862a009990-460b0204000000001a3c2fd11618dc00 \
  --custom-params '{...}'
```

**DUT 在 AUT 云中的身份：**

| 设备 | AUT 云标识 |
|------|-----------|
| DUT `qurradc1816d12f3c1a` (HW) | `460b0204000000001a3c2fd11618dc00` |
| Controller | `360c010100000000091e01862a009990` |
| **AUT 云 did** | `360c010100000000091e01862a009990-460b0204000000001a3c2fd11618dc00` |

查询方式: `curl -s http://10.58.120.88:8002/devices | grep qurra`

## custom-params

```json
{
  "router_ip": "192.168.50.1",
  "router_ssh_user": "AX86U",
  "router_ssh_pwd": "New!123456",
  "router_model": "asus_rt_ax86u",
  "router_controller_aux_id": "Router_nanjing_aut_laptop",
  "iperf_aux_id": "Router_nanjing_aut_laptop"
}
```

- `router_controller_aux_id`: AUX Router Client 设备标识
- `iperf_aux_id`: AUX iperf Tester 设备标识
- 两者指向同一台 Linux PC (`Router_nanjing_aut_laptop`)，但走不同 AUX action（Router=execute，iperf=run_shell）

## AUX 设备

| 设备 | did | 部署位置 | 功能 |
|------|-----|---------|------|
| Router Client | `Router_nanjing_aut_laptop` | Linux PC (10.138.8.178) | SSH 路由器 → execute action |
| iperf Tester | `Router_nanjing_aut_laptop` | Linux PC (10.138.8.178) | 本地 shell → run_shell action |

## iperf 二进制

| 设备 | 路径 | 来源 |
|------|------|------|
| DUT (ARM32) | `/data/local/tmp/iperf` | ResManager HTTP 下载 → adb push |
| Linux PC (x86_64) | `/usr/bin/iperf` | apt install iperf |

ResManager 下载 URL: `http://qa-sh.amlogic.com:8881/chfs/shared/Test_File/AUT/test_bin/iperf2`
