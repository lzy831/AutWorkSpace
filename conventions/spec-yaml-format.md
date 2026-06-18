# Spec YAML 格式规范

所有 `ClaudeWorkSpace/specs/<domain>/*.yaml` 文件遵守此规范。

## 顶层字段

| 字段 | 必须 | 说明 | 不应包含 |
|------|:--:|------|----------|
| `domain` | ✅ | 测试域: ethernet / wifi | — |
| `id` | ✅ | 唯一标识，如 `Ethernet_Func_011` | — |
| `auto_status` | ✅ | `auto`(已实现) / `pending`(可行未做) / `manual`(不实现) | — |
| `name` | ✅ | 简短用例名称 | 参数值、实现细节 |
| `testbed` | ✅ | 引用 `ClaudeWorkSpace/environments/<id>.yaml` | — |
| `description` | ✅ | 测试目的和场景的宏观描述，遵守 description 模板规则 | SSID、密码、IP、cmd wifi status、Supplicant、错误字符串、实现方式 |

### description 模板

`description` 由 `[状态]`,`[动作(含主体)]`,`检测[结果(含主体)]` 三要素组成，多步骤时串联 `动作→检测` 链条。

格式：`[状态]下, [动作(含主体)], 检测[结果(含主体)], [动作(含主体)], 检测[结果(含主体)]`

规则：
```yaml
# ✅ 正确
description: DHCP模式下, 拔掉DUT端网线, 检测DUT IP消失, 重新插入网线, 检测DUT通过DHCP重新获取IP
description: Static IP模式下, DUT配置静态IP, 检测DUT IP mode为Static且网络连通

# ❌ 错误（缺少主体）
description: DHCP模式下, 拔掉网线, 检测IP消失

# ❌ 错误（含实现细节）
description: DHCP模式下, 通过ip link down模拟拔掉DUT端网线, 检测DUT IP消失

# ❌ 错误（动作后有多余的"后"）
description: DHCP模式下, 拔掉网线后, 检测IP消失
```

- **状态**：网络模式(DHCP/Static IP/双栈)或前置条件(DUT连接IPv6路由器并正常获取双栈IP地址)
- **动作**：须含明确主体(DUT/路由器/系统)
- **检测**：验证点，用 `检测` 关键词，结果须含主体
- 动作与检测间用 `,` 分隔，不用 `后,`
- 不含实现细节(ip link、ADB、SSH)

## 段落结构

YAML 文件分为 5 个段落，**段间空 1 行，段内不空行**：

| 段落 | 字段 |
|------|------|
| 1 | `domain`, `id`, `auto_status`, `name`, `testbed` |
| 2 | `description`, `excel_preset`, `excel_steps`, `excel_expected` |
| 3 | `setup_hooks`, `teardown_hooks` |
| 4 | `preconditions` |
| 5 | `procedure` |

`setup_hooks` 和 `teardown_hooks` 必须同时存在，无内容时写 `[]`。excel_* 字段使用双引号单行格式，换行用 `\n` 表示。

```yaml
domain: ethernet
id: Ethernet_Func_001
auto_status: auto
name: xxx
testbed: ethernet_router_lan

description: xxx
excel_preset: "xxx"
excel_steps: "1. xxx\n2. xxx"
excel_expected: "xxx"

setup_hooks: []
teardown_hooks:
  - step_disable_router_ipv6

preconditions:
  - description: xxx
    operation:
      api: step_xxx
...

procedure:
  - operation:
      api: step_xxx
...
```

## preconditions

每个 precondition 支持两种格式：

**Format A（check-only）：**
```yaml
- description: 检查项描述
  check:
    api: check_xxx
    params: {}
```

**Format B（step + check pair）：**
```yaml
- description: 前置步骤描述
  operation:
    api: step_xxx
    params: {}
  check:
    api: check_xxx
    params: {}
```

**precondition 中 check 的 `method` 规则：**

precondition 的 `check_ethernet_connected` 必须使用 `method: cmd`，避免打开 Settings UI 浪费时间（每个 check 节省 ~30s）。procedure 中的 check 按需选择 method。

```yaml
# ✅ precondition: 用 cmd
- description: DUT 以太网物理链路已连通
  operation:
    api: step_ensure_router_lan_up
  check:
    api: check_ethernet_connected
    params:
      method: cmd

# ❌ precondition: 用 ui（浪费时间）
- description: DUT 以太网物理链路已连通
  operation:
    api: step_ensure_router_lan_up
  check:
    api: check_ethernet_connected
```

## procedure

每个 procedure 步骤**仅支持 Format B**（operation + check pair）：

```yaml
- operation:
    description: 步骤描述
    api: step_xxx
    params: {}
    wait_after: 5   # 可选，步骤完成后等待秒数
  check:
    description: 验证描述
    api: check_xxx
    params: {}
    timeout: 30     # 可选，check 超时秒数
    on_failure: abort  # 可选，失败时的行为（compile_workflow 是否支持以实际为准）
```

## 参数模板变量

环境特定参数使用 `${...}` 引用，运行时由 workflow 框架 `_resolve_simple_variable()` 解析。

### 引用规则

**1. 引用前序 step 的 data 输出（必须经过 `.data.`）：**

step 返回值结构固定为：
```python
{"step": "step_xxx", "status": True, "data": {"field": "value"}, "timestamp": "..."}
```

解析器从 `context[step_id]` 取整个返回值 dict，再逐级访问属性。因此：

```yaml
# ✅ 正确：经过 .data. 访问实际业务字段
${step_discover_network_info.data.gateway}
${step_disconnect_router_lan.data.port}
${step_create_rc_by_device_id.data.bluetooth_device}

# ❌ 错误：跳过 .data.，解析器会在返回值顶层找 field，结果为 <未知变量>
${step_discover_network_info.gateway}
${step_create_rc_by_device_id.bluetooth_device}
```

**2. 引用 custom_params（无中间层）：**
```yaml
${custom_params.xxx}    # 来自 --custom-params 的 key
```

**3. 判断引用层级的快速方法：**

凡是从 step 函数的 `data` 字典中取值，路径中必须有 `.data.`。检查方式：
```bash
# 找出所有跳过 .data. 的错误引用（排除 custom_params）
grep -rn '\${step_[^}]*}' specs/ | grep -v '\.data\.' | grep -v 'custom_params'
```

## 不应出现在 spec 中的内容

- `hardware` 字段 — 硬件信息在 environments/*.yaml
- 具体 IP 地址、SSID、密码 — 用 `${custom_params.xxx}`
- `cmd wifi status` 等实现命令 — 用 check 封装，宏观描述即可
- `Supplicant state COMPLETED` 等技术细节 — 用 check 封装
- 中文标点符号 — 见 `code-style.md` 统一规范
- `yaml.dump` 直接修改 YAML — 会破坏原始格式。修改后必须检查：
  - `hooks` 前后与 description/preconditions 间有空行
  - `excel_preset/steps/expected` 和上下文字段间有空行
  - `preconditions` 和 `procedure` 与前后段落间有空行
  - 中文标点未被引入
