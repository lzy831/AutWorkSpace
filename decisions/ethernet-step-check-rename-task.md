# Ethernet Step/Check 重命名任务

## 背景
当前命名存在对象不明确、不对称、冗余等问题。

## 方案

### DUT 侧（不变）
- step_enable_ethernet / step_disable_ethernet

### 路由器 LAN 口
- step_ensure_ethernet_link      → step_ensure_router_lan_up
- step_disconnect_ethernet       → step_disconnect_router_lan
- step_connect_ethernet          → step_connect_router_lan

### 路由器 WAN 口（新增）
- step_disconnect_router_wan / step_connect_router_wan

### 路由器操作（不变）
- step_reboot_router
- step_enable_router_ipv6 / step_disable_router_ipv6

### Check
- check_ethernet_connected       → 保留
- check_ethernet_disconnected    → 保留
- check_network_connected         → 废弃（仅 WiFi 用）
- check_network_disconnected      → 废弃（仅 WiFi 用）

## 影响范围
- ethernet_steps.py: 3 个 decorator name 改动
- ethernet_step.py: 3 个函数名改动，3 个 @log_args 装饰
- 所有 YAML spec: api 引用批量替换
- 所有 workflow JSON: 重新编译

## 影响范围检查
- WiFi 用例：不引用这些 step，不受影响 ✓

## 执行状态
- [x] atomic 层 decorator name + def 函数名
- [x] lib 层函数名
- [x] YAML api 引用替换
- [x] 重新编译 JSON
- [x] WiFi 交叉检查（无引用）
