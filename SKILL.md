# SKILL: 测试用例 → 自动化 Workflow 生成流程

> **适用场景**: 将人工测试用例（Excel/手动描述）转化为可执行的自动化测试 workflow。
> **适用范围**: Ethernet、WiFi、Bluetooth、Display 等任意模块。
> **前置条件**: 已有 `unique_apis.json` 中注册的 step/check API，或愿意新增。

---

## 目录

1. [整体流程概览](#1-整体流程概览)
2. [Phase 1: 补充完善测试用例](#2-phase-1-补充完善测试用例)
3. [Phase 2: 梳理 Step/Check 清单](#3-phase-2-梳理-stepcheck-清单)
4. [Phase 3: 实现缺失的 Step/Check](#4-phase-3-实现缺失的-stepcheck)
5. [Phase 4: 生成 Workflow JSON](#5-phase-4-生成-workflow-json)
6. [Phase 5: 验证与迭代](#6-phase-5-验证与迭代)
7. [附录: 约定与规范](#7-附录-约定与规范)

---

## 1. 整体流程概览

```
原始 Excel 用例
      │
      ▼
┌─────────────────────────────────────────────────────┐
│ Phase 1: 补充完善 (enrich)                            │
│   原始描述 → 结构化 JSON                              │
│   包含: 设备拓扑 + Given/When/Then + 参数 + 超时      │
│   输出: enriched/<CaseNo>.json                        │
└─────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────┐
│ Phase 2: 梳理 Step/Check 清单                         │
│   汇总当前模块需要的所有 step 和 check                  │
│   标注: 已有 / 需新增 / 需修改                         │
│   输出: <module>_step_check_inventory.md              │
└─────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────┐
│ Phase 3: 实现缺失的 Step/Check                        │
│   按清单中的"实现思路"编写代码                          │
│   - lib/<module>/<module>_step.py                    │
│   - lib/<module>/<module>_check.py                   │
│   - atomic/step_impl/.../<module>_steps.py           │
│   - atomic/check_impl/.../<module>_checks.py          │
│   更新 unique_apis.json                               │
└─────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────┐
│ Phase 4: 生成 Workflow JSON                          │
│   将 enriched case 中的 when 序列转换为 nodes + edges │
│   填充 params / param_config                          │
│   输出: <CaseNo>.json (可直接被 workflow engine 执行)  │
└─────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────┐
│ Phase 5: 验证                                        │
│   在真实 DUT 上执行 workflow                           │
│   修正超时、参数、导航偏移等问题                        │
└─────────────────────────────────────────────────────┘
```

---

## 2. Phase 1: 补充完善测试用例

### 2.1 输入

- 原始 Excel / 文本用例（通常只有简单的自然语言描述）
- 对测试环境的理解（有哪些设备、怎么连接）

### 2.2 输出

`specs/<domain>/<CaseNo>.yaml` — 结构化的 Test Case Spec YAML 文件。

完整的 schema 参见 `docs/superpowers/specs/2026-05-18-test-case-spec-format-design.md`。

### 2.3 关键设计

| 要点 | 说明 |
|------|------|
| **环境复用** | 物理拓扑定义在 `environments/<env_id>.yaml`，用例通过 `environment` 字段引用 |
| **双视图** | 每步同时描述 manual（QA 手动操作）和 automation（脚本实现），共同语言 |
| **Operation→Check 配对** | 测试步骤严格按 `operation → check` 成对出现 |
| **显式 API** | `automation.api` 必填，直接引用 step/check 函数名 |
| **Alternatives** | 难自动化操作列出替代方案（如继电器 vs 软件模拟） |
| **超时与失败** | 每个 check 指定 `timeout` 和 `on_failure`（abort/continue/retry） |

### 2.4 示例

参见: `specs/ethernet/Ethernet_Func_002.yaml`

---

## 3. Phase 2: 梳理 Step/Check 清单

### 3.1 目标

汇总当前模块所有用例需要的 step 和 check，生成一份清单文档，标注实现状态。

### 3.2 输出

`<module>_step_check_inventory.md`

### 3.3 清单模板

```markdown
# <Module> 测试用例 Step & Check 清单

## Steps

### step_<name>
- **实现文件**: <path>
- **实现思路**: UI Automation / ADB Shell / 日志分析 / 硬件控制
- **参数**: 表格列出参数名、类型、必填、默认值、说明
- **适用场景**: 哪些用例需要它
- **局限**: 已知限制

## Checks
（同上结构）

## 缺失/待实现
| 名称 | 类型 | 说明 |
```

### 3.4 实现思路分类

| 思路类型 | 说明 | 示例 |
|---------|------|------|
| **ADB Shell 命令** | 直接执行 shell 命令，解析输出 | `ip addr show eth0`、`ping`、`cat /sys/class/net/eth0/address` |
| **UI Automation** | 通过 `uiautomator dump` + `input keyevent/text/tap` 操作 Android Settings UI | 静态 IP 配置向导、检查错误提示 |
| **日志分析** | `adb logcat` 抓取并 grep 关键字 | 检查 DHCP 是否成功分配、网络异常日志 |
| **硬件控制** | 通过串口/HTTP API 控制继电器、电源、衰减器等 | 物理断电、拔网线、WiFi 衰减 |
| **PC 端操作** | 在 controller PC 上执行命令 | 设置 PC 网卡模式、从 PC 端 ping DUT |

### 3.5 示例

参见: `Function/ethernet_step_check_inventory.md`

---

## 4. Phase 3: 实现缺失的 Step/Check

### 4.1 三层架构

```
atomic/step_impl/<module>/<module>_steps.py   ← @composer_step 装饰器，返回结构化 dict
        │
        ▼
lib/common/<module>/<module>_step.py           ← 纯 Python 函数，raise 异常表示失败
        │
        ▼
lib/common/<module>/utils/<manager>.py         ← 底层 ADB/硬件操作封装
```

### 4.2 Step 实现规范

**lib 层函数签名**: 所有 step_ 函数第一个参数是业务参数，最后一个是 `device_id: Optional[str] = None`

```python
def step_set_static_ip(
    ip_address: str,
    gateway: str,
    dns: str = "8.8.8.8",
    prefix: int = 24,
    dns2: str = "",
    device_id: Optional[str] = None,
) -> None:
    """docstring"""
    # 1. 参数校验 → ValueError
    # 2. 获取 ADB 客户端
    # 3. 执行操作
    # 4. 失败时 raise RuntimeError / AssertionError
```

**Atomic 层**: 使用 `@composer_step` 装饰器，try/except 包装，返回标准 dict

```python
@composer_step(
    name="step_set_static_ip",
    description="...",
    category="peripheral.network.ethernet",
    params={ ... },
    tags=["kind:step", "domain:ethernet_static", ...],
)
def step_set_static_ip(ip_address, gateway, dns="8.8.8.8", prefix=24, dns2=""):
    try:
        _lib_set_static_ip(...)
        return {"step": "...", "status": True, "message": "...", "data": {}, "timestamp": ...}
    except Exception as e:
        return {"step": "...", "status": False, "message": f"...{e}", "data": {...}, "timestamp": ...}
```

### 4.3 Check 实现规范

同样的三层架构，但返回包含 `expected` 和 `actual`:

```python
return {
    "check": "check_xxx",
    "status": True,
    "result": True,
    "message": "...",
    "expected": "...",
    "actual": "...",
    "data": {},
    "timestamp": ...
}
```

### 4.4 注册到 unique_apis.json

每个新增 step/check 必须在 `atomic/tools/unique_apis.json` 中注册，包含 `function_name`、`description`、`params`、`tags` 等字段。

---

## 5. Phase 4: 生成 Workflow JSON

### 5.1 编译脚本

使用 `tools/compile_workflow.py` 将 spec YAML 编译为 workflow JSON：

```
python tools/compile_workflow.py specs/ethernet/Ethernet_Func_002.yaml
# → atomic/workflows/auto_generate/Ethernet_V1.3_test_case/Function/Ethernet_Func_002.json
```

编译规则：
- `steps[].operation.automation.api` → `nodes[].step_id`
- `steps[].check.automation.api` → `nodes[].check_id`
- `automation.params` → `nodes[].param_config`
- `preconditions[].automation` → 作为首个 check node 插入 nodes
- 重复 API 自动加后缀（`check_network_connected` → `check_network_connected_1`）
- `node.params` 从 `unique_apis.json` 查表获取完整 schema
- 输出路径由 `_source.file` + `_source.sheet` 推断

---

## 6. Phase 5: 验证与迭代

### 6.1 验证清单

- [ ] `unique_apis.json` 中存在 workflow 引用的所有 step_id / check_id
- [ ] 所有 nodes 的 `params` 与 API 定义的 schema 一致
- [ ] 所有 edges 的 source/target 指向存在的 node id
- [ ] `param_config` 中的值类型与 params schema 中的 type 匹配
- [ ] 每个 step 节点后面有对应的 check 节点（或明确标注不需要）
- [ ] timeout 和 wait 参数在合理范围内

### 6.2 DUT 实测

在真实设备上运行 workflow，记录:
- 导航偏移（需要调整 DOWN/UP 次数）
- 超时不足（DHCP 慢、UI 加载慢）
- 未预期的 UI 状态（弹窗、toast）

### 6.3 回写 Enriched Case

DUT 测试中发现的修正应回写到 `enriched/*.json`，保持文档与代码一致。

---

## 7. 附录: 约定与规范

### 7.1 目录结构

```
scripts/python/tsuite/
├── SKILL.md                              ← 本文档
├── environments/
│   └── <env_id>.yaml                     ← 物理环境定义
├── specs/
│   └── <domain>/
│       └── <CaseNo>.yaml                 ← Test Case Spec YAML
├── tools/
│   ├── compile_workflow.py              ← spec YAML → workflow JSON
│   ├── generate_inventory.py            ← spec YAML → step/check 清单
│   └── migrate_enriched.py             ← 一次性：旧 enriched JSON → spec YAML
└── <domain>/
    └── <domain>_step_check_inventory.md  ← 自生成清单
```

Workflow JSON 输出目录（不变）：
```
scripts/python/atomic/workflows/auto_generate/
```

### 7.2 Step/Check 命名规范

| 元素 | 规范 | 示例 |
|------|------|------|
| step 函数 | `step_<动词>_<对象>` | `step_set_static_ip`, `step_connect_ethernet_dhcp` |
| check 函数 | `check_<对象>_<状态>` | `check_network_connected`, `check_prompt_invalid_ip` |
| 参数名 | snake_case | `ip_address`, `gateway_ip`, `dns2` |
| device_id | 总是放在最后，默认 None | `def step_xxx(..., device_id=None)` |

### 7.3 参数灵活性原则

1. **同类操作合并**: `step_disconnect_network(type)` 通过 `type` 参数支持 wifi/ethernet，避免各写一个
2. **可选参数默认安全值**: DNS 默认 `8.8.8.8`，prefix 默认 `24`
3. **空值表示跳过**: `dns2=""` 表示跳过 DNS2 字段
4. **新增参数向后兼容**: 新参数必须有默认值

### 7.4 硬件依赖分级

| 级别 | 说明 | 示例 |
|------|------|------|
| **A - 不需要** | 纯软件操作 | DHCP 连接、静态 IP 配置、ping |
| **B - 需要但可模拟** | 有软件替代方案 | 拔网线 → ip link down；断电 → input keyevent 26 |
| **C - 必须有硬件** | 无法软件替代 | 交叉线 MDIX 测试、HDMI 输出检测 |
| **D - 需要外部控制** | 需要控制 PC/路由器 | 设置 PC 网卡模式、重启路由器 |

### 7.5 Spec YAML Schema 版本

当前版本: `test_case_spec_v1`

未来如需扩展（如增加 log 分析步骤、条件分支等），应更新 `_schema` 版本号并在此处记录变更。

旧格式: `enriched_test_case_v1`（已废弃，通过 `migrate_enriched.py` 迁移至 spec YAML）
