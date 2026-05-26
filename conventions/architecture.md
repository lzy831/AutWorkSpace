# 架构约定

## 分层

```
workflow JSON (tsuite/atomic/workflows/)
    │
    ▼ 引用
atomic 层 (scripts/python/atomic/step_impl/ & check_impl/)
    │  ┌ @composer_step / @composer_check 装饰器
    │  └ 封装异常处理、返回值标准化
    │
    ▼ 调用
实现层 (scripts/python/lib/common/peripheral/network/)
    │  ┌ 真正的业务逻辑
    │  └ ADB Shell / Settings UI / Router SSH
    │
    ▼ 调用
底层工具 (AndroidUi, EthernetManager, RouterManager, ADBClient)
```

## 各层职责

| 层 | 职责 | 示例 |
|------|------|------|
| **workflow JSON** | 测试流程编排（节点 + 边） | `Ethernet_Func_011.json` |
| **atomic step** | 标准化返回值 `{status, message, result, data, timestamp}` | `step_set_static_ip()` |
| **atomic check** | 同上，抛异常表示 failure | `check_ethernet_connected()` |
| **lib 实现** | 纯业务逻辑，raise 异常 | `check_ethernet_connected(method)` |
| **EthernetManager** | eth0 底层操作（ip link / ip addr） | `enable()`, `get_gateway()` |
| **RouterManager** | 路由器 SSH 操作 | `reboot()`, `disconnect_device()` |

## 调用链示例

```
step_set_static_ip                     ← atomic/step_impl/ethernet/ethernet_steps.py
  └ step_set_static_ip                 ← lib/ethernet/ethernet_step.py
       └ get_navigator()               ← SettingsNavigatorATV
            ├ open_settings()           ← HOME → force-stop → am start
            ├ open_ethernet_ip_settings() ← DOWN×2 → ENTER → DOWN×4 → ENTER
            └ _navigate_to_static_ip_wizard() ← Static → Wizard 5 pages
```

## ConfigManager / custom_params

```
workflow_runner.py --custom-params '{"key":"value"}'
  → ConfigManager.init_session_config(custom_params={...})
    → context['custom_params'] = {...}
      → prepare_params() 解析 ${custom_params.key} → "value"
```
