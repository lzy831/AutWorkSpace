# AutoTestRes 项目指引

## 项目概述

Amlogic 自动化测试框架。

- **开发环境**：Windows，通过 Samba 挂载 `Y:\AutoTestRes`（对应服务器 `/home/zhiyuan.liu/AutoTestRes`）
- **运行测试**：需 SSH 到服务器执行
- 主要开发工作在 `scripts/python/` 下

## 服务器连接

| 项目 | 值 |
|------|-----|
| 以太网 IP（优先） | 10.138.8.178 |
| WiFi IP（备选） | 192.168.50.152 |
| 用户名 | zhiyuan.liu |
| 密码 | Linux2025 |
| 服务器路径 | `/home/zhiyuan.liu/AutoTestRes` |
| Samba 路径 | `Y:\AutoTestRes` |

## 目录结构

```
scripts/python/
├── atomic/                  # 原子化 step & check 核心（workflow 视角的接口层）
│   ├── step_impl/           # step 接口（按模块分目录）
│   ├── check_impl/          # check 接口（按模块分目录）
│   └── atomic_debugger.py   # 调试工具
├── lib/                     # 实现层（atomic 层调用）
│   └── common/peripheral/network/
│       ├── ethernet/        # ethernet step/check 实现
│       ├── wifi/            # wifi step/check 实现
│       └── router/          # 路由器 SSH 操作, RA 二进制
├── tsuite/                  # 已废弃，内容迁移到 ClaudeWorkSpace
│   └── tools/               # compile_workflow.py 等（原位置，保留兼容）
├── tests/                   # 测试用例
└── localtest_runner.py      # 本地测试入口
```

## 架构约定

- **atomic 层** = workflow JSON 直接引用的接口，`scripts/python/atomic/step_impl/` + `check_impl/`
- **实现层** = atomic 层调用的具体实现，`scripts/python/lib/common/`
- **ClaudeWorkSpace** = 项目规范、用例、参考的规范源（独立 git 仓）

## 工作范围

允许修改的目录，超出需提示：

- `scripts/python/atomic/step_impl/peripheral/network`
- `scripts/python/atomic/check_impl/peripheral/network`
- `scripts/python/lib/common/peripheral/network`
- `scripts/python/lib/common/system/settings_navigator*.py`
- `scripts/python/atomic/workflows/auto_generate/Ethernet_V1.3_test_case/`
- `scripts/python/atomic/workflows/auto_generate/wifi_BT_testcase_v1.1/`
- `ClaudeWorkSpace/`

## DUT & Router

| 项目 | 值 |
|------|-----|
| Device ID | `qurradc1816d12f3c1a` |
| 平台 | GTV/ATV，服务器 USB 直连 |
| Router | ASUS RT-AX86U @ 192.168.50.1 |
| Router SSH | AX86U / New!123456 |

## 运行 Workflow

```bash
cd /home/zhiyuan.liu/AutoTestRes/scripts/python
source .venv/bin/activate

# 编译
python3 tsuite/tools/compile_workflow.py \
  ClaudeWorkSpace/specs/<domain>/<case>.yaml \
  -o atomic/workflows/auto_generate/<path>/<case>.json

# 运行
python3 atomic/workflow_runner.py \
  --workflow-path atomic/workflows/auto_generate/<path>/<case>.json \
  --device-id <device_id> \
  --custom-params '{"routers":{...}}'
```

## 代码约定

- 所有文件 Linux 换行格式（LF）
- Step/Check 通过 `__init__.py` 暴露
- `composer.py` 不在维护范围
- 环境参数通过 `--custom-params` 注入，不硬编码到 spec
- Step/Check 新增修改 → 同步更新 `references/ethernet-step-check-inventory.md`
