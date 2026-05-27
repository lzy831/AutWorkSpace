# 用例 Spec YAML

此目录与 `tsuite/specs/` 同步，按 domain 分子目录。

## 目录

```
specs/
├── ethernet/               # 以太网相关用例
│   ├── Ethernet_Func_001.yaml   DHCP 模式下获取 IPv4 地址
│   ├── Ethernet_Func_002.yaml   插拔网线后重新连接
│   ├── Ethernet_Func_006.yaml   DHCP 待机唤醒后自动重连
│   ├── Ethernet_Func_007.yaml   连接静态 IP
│   ├── Ethernet_Func_011.yaml   静态 IP 模式下路由器重启后恢复
│   ├── Ethernet_Func_013.yaml   输入无效静态 IP 时系统报错
│   ├── Ethernet_Func_014.yaml   DHCP 切换到静态 IP
│   ├── Ethernet_Func_040.yaml   双栈网络（IPv4 + IPv6）地址获取
│   ├── Ethernet_Func_041.yaml   双栈网络下热插拔网线后 IP 恢复
│   ├── Ethernet_Func_043.yaml   双栈网络下路由器重启后 IP 恢复
│   └── Ethernet_new_function_002.yaml   10M FDX 互 Ping（TODO）
│
└── wifi/                    # WiFi 相关用例
    ├── Wifi_Func_004.yaml
    ├── Wifi_Func_006.yaml
    ├── Wifi_Func_007.yaml
    ├── Wifi_Func_008.yaml
    ├── Wifi_Func_009.yaml
    └── ...
```

## 状态标记

| 标记 | 说明 |
|------|------|
| ✅ 已验证 | workflow 测试通过 |
| 🔧 待优化 | spec 需要调整 |
| 🔜 TODO | 尚未开始 |

## 格式规范

见 [conventions/spec-yaml-format.md](../conventions/spec-yaml-format.md)

## 编译

```bash
cd /home/zhiyuan.liu/AutoTestRes/scripts/python
source .venv/bin/activate
python3 tsuite/tools/compile_workflow.py \
  ClaudeWorkSpace/specs/<domain>/<case>.yaml \
  -o atomic/workflows/auto_generate/<path>/<case>.json
```
