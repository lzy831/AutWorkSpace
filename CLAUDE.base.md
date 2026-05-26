# CLAUDE.md

## 项目概述

Amlogic 自动化测试框架。

- **开发环境**：Windows，通过 Samba 挂载 `Y:\AutoTestRes`（对应服务器 `/home/zhiyuan.liu/AutoTestRes`）
- **运行测试**：需 SSH 到服务器执行（服务器性能较差，Claude Code 在 Windows 上运行较快）
- 主要开发工作在 `scripts/python/` 下，实现自动化测试中各个模块的 **原子化操作**（step 和 check）

## 服务器连接

| 项目 | 值 |
|------|-----|
| 以太网 IP（优先） | 10.138.8.178 |
| WiFi IP（备选） | 192.168.50.152 |
| 用户名 | zhiyuan.liu |
| 密码 | Linux2025 |
| 服务器路径 | `/home/zhiyuan.liu/AutoTestRes` |
| Samba 路径 | `Y:\AutoTestRes` |

> 代码编辑在 Windows 本地，运行测试通过 SSH 到服务器执行。

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
│       └── router/          # 路由器 SSH 操作
├── tsuite/                  # 用例 Spec YAML 和 Workflow 编译
│   ├── specs/               # 用例 spec YAML（同步到 AutoTestDocs/specs/）
│   ├── tools/compile_workflow.py
│   └── environments/        # 测试环境定义
├── tests/                   # 测试用例
└── localtest_runner.py      # 本地测试入口
```

## 架构约定

- **atomic 层** = workflow JSON 直接引用的接口，位于 `scripts/python/atomic/step_impl/` 和 `scripts/python/atomic/check_impl/`。提到 "step" / "check" 默认指这层
- **实现层** = atomic 层调用的具体实现，位于 `scripts/python/lib/common/`

## 工作范围

我目前的主要工作在以下目录内。超出范围的修改需及时提示。

- `scripts/python/atomic/step_impl/peripheral/network`
- `scripts/python/atomic/check_impl/peripheral/network`
- `scripts/python/lib/common/peripheral/network`
- `scripts/python/lib/common/system/settings_navigator*.py`
- `scripts/python/tsuite/specs/`
- `scripts/python/atomic/workflows/auto_generate/Ethernet_V1.3_test_case/`
- `scripts/python/atomic/workflows/auto_generate/wifi_BT_testcase_v1.1/`

## 规范文档 & 参考

所有规范、参考、环境描述独立维护在 [AutoTestDocs](Y:\AutoTestDocs)：

| 文档 | 说明 |
|------|------|
| [runbooks/workflow-testing.md](Y:\AutoTestDocs\runbooks\workflow-testing.md) | Workflow 测试操作手册 |
| [runbooks/setup-env.md](Y:\AutoTestDocs\runbooks\setup-env.md) | 首次环境搭建 |
| [conventions/architecture.md](Y:\AutoTestDocs\conventions\architecture.md) | 架构分层约定 |
| [conventions/spec-yaml-format.md](Y:\AutoTestDocs\conventions\spec-yaml-format.md) | Spec YAML 格式规范 |
| [conventions/step-check-design.md](Y:\AutoTestDocs\conventions\step-check-design.md) | Step/Check 开发规范 |
| [references/ethernet-step-check-inventory.md](Y:\AutoTestDocs\references\ethernet-step-check-inventory.md) | Step & Check 清单 |
| [references/implementation-reference.md](Y:\AutoTestDocs\references\implementation-reference.md) | 实现参考与已知限制 |
| [environments/topology.md](Y:\AutoTestDocs\environments\topology.md) | 网络拓扑 |
| [environments/hardware.md](Y:\AutoTestDocs\environments\hardware.md) | 硬件清单 |
| [environments/params.json](Y:\AutoTestDocs\environments\params.json) | 环境参数 |
| [specs/](Y:\AutoTestDocs\specs\) | 用例 Spec YAML（与 tsuite/specs/ 同步） |

## 核心规则

- Step/Check 修改后 → 更新 [inventory](Y:\AutoTestDocs\references\ethernet-step-check-inventory.md)
- 测试必须 SSH 到服务器执行，不在 Windows 本地跑
- 代码使用 LF 换行，Python 文件通过 `__init__.py` 暴露
- 环境参数通过 `--custom-params` 注入，不硬编码到 spec
- `composer.py` 不在我的维护范围，不可修改

## DUT 信息

- Device ID: `qurradc1816d12f3c1a`
- 平台: GTV/ATV，通过服务器 USB 直连

## 路由器信息

- 型号: ASUS RT-AX86U @ 192.168.50.1
- SSH: AX86U / New!123456
