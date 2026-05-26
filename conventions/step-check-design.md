# Step/Check 开发规范

## 命名规范

- Step: `step_<动作>_<对象>`，如 `step_set_static_ip`, `step_discover_network_info`
- Check: `check_<对象>_<属性>`，如 `check_ethernet_connected`, `check_wifi_ip_mode`

## 装饰器

### @composer_step

```python
@composer_step(
    name="step_xxx",
    description="功能描述",
    category="peripheral.network.ethernet",
    params={
        "param_name": {
            "name": "参数显示名",
            "type": "str",
            "required": True,
            "default": None,
            "description": "参数说明",
            "enum": ["opt1", "opt2"],  # 可选
        },
    },
    pre_conditions=[],     # 前置 step 依赖
    post_conditions=[],    # 后置 effect
    tags=["kind:step", "domain:xxx", "module:xxx"],
)
def step_xxx(param1, param2="default"):
    ...
```

### @composer_check

```python
@composer_check(
    name="check_xxx",
    description="功能描述",
    category="peripheral.network.ethernet",
    params={...},
    pre_conditions=[],
    post_conditions=[],
    tags=["kind:check", "domain:xxx", "module:xxx"],
)
def check_xxx(param1, param2="default"):
    ...
```

## 返回值格式

### Step 成功
```python
{
    "step": "step_xxx",
    "status": True,
    "message": "操作成功描述",
    "data": { "key": "value" },    # 供后续 step 通过 ${step_xxx.data.key} 引用
    "timestamp": "2026-05-25 12:00:00"
}
```

### Step 失败
```python
{
    "step": "step_xxx",
    "status": False,
    "message": "失败原因描述",
    "data": { "error": "..." },
    "timestamp": "2026-05-25 12:00:00"
}
```

### Check 成功 / 失败
```python
# 成功
{ "check": "check_xxx", "status": True, "result": True, "message": "...", "expected": "...", "actual": "..." }

# 失败
{ "check": "check_xxx", "status": False, "result": False, "message": "...", "expected": "...", "actual": "..." }
```

## method 参数约定

支持多种实现方式的 step/check 使用 `method` 参数：

| method | 说明 | 适用范围 |
|--------|------|----------|
| `cmd` | ADB shell 命令 | 所有无 UI 依赖的操作 |
| `ui` | Settings UI 自动化 (uiautomator + keyevent) | 需操作 Settings 界面的场景 |
| `apk` | APK (WifiAmControl) | WiFi 特有操作 |

默认值统一为最稳定/常用的方式。

## 错误处理

- **lib 实现层**: 用 `raise RuntimeError()` / `raise AssertionError()` 表达失败
- **atomic 层**: try/except 捕获异常，构造标准化失败返回值
- **check 在 procedure 中**: `on_failure: abort` 可终止整个 workflow
