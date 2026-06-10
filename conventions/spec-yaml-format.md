# Spec YAML 格式规范

所有 `tsuite/specs/<domain>/*.yaml` 文件遵守此规范。

## 顶层字段

| 字段 | 必须 | 说明 | 不应包含 |
|------|:--:|------|----------|
| `domain` | ✅ | 测试域: ethernet / wifi | — |
| `id` | ✅ | 唯一标识，如 `Ethernet_Func_011` | — |
| `name` | ✅ | 简短用例名称 | 参数值、实现细节 |
| `testbed` | ✅ | 引用 `tsuite/environments/<id>.yaml` | — |
| `description` | ✅ | 测试目的和场景的宏观描述 | SSID、密码、IP、cmd wifi status、Supplicant、错误字符串、实现方式 |

## hooks

`setup_hooks` 和 `teardown_hooks` 放在 `description` 之后、`preconditions` 之前，与 `description` 用空行分隔。两个字段必须同时存在，无内容时写空数组 `[]`，保持结构完整性。

```yaml
description: xxx

setup_hooks: []
teardown_hooks:
  - step_disable_router_ipv6

preconditions:
  ...
```

属于概述部分（description）和流程部分（preconditions/procedure）之间的桥梁。

## preconditions

每个 precondition 支持两种格式：

**Format A（check-only）：**
```yaml
- description: 检查项描述
  automation:
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

## procedure

每个 procedure 步骤**仅支持 Format B**（operation + check pair）：

```yaml
- operation:
    description: 步骤描述
    automation:
      api: step_xxx
      params: {}
      wait_after: 5   # 可选，步骤完成后等待秒数
  check:
    description: 验证描述
    automation:
      api: check_xxx
      params: {}
      timeout: 30     # 可选，check 超时秒数
      on_failure: abort  # 可选，失败时的行为
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
- `cmd wifi status` 等实现命令 — 宏观看"WiFi 已连接"
- `Supplicant state COMPLETED` 等技术细节 — 用 check 封装
- 中文标点符号 — 一律使用 ASCII 标点（`;` 替代 `；`，`()` 替代 `（）`，`,` 替代 `，` 等），确保 workflow JSON 和 YAML 在任何环境下兼容
