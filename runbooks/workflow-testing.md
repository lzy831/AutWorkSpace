# Workflow 测试操作手册

## 前置条件

1. DUT 已通过 USB-ADB 连接到服务器
2. 服务器已安装 .venv 虚拟环境
3. 路由器可 SSH 访问

## 编译 Spec YAML → Workflow JSON

```bash
cd /home/zhiyuan.liu/AutoTestRes/scripts/python
source .venv/bin/activate
python3 tsuite/tools/compile_workflow.py \
  tsuite/specs/<domain>/<case>.yaml \
  -o atomic/workflows/auto_generate/<domain>_V1.3_test_case/Function/<case>.json
```

## 运行 Workflow

```bash
cd /home/zhiyuan.liu/AutoTestRes/scripts/python
source .venv/bin/activate
python3 atomic/workflow_runner.py \
  --workflow-path atomic/workflows/auto_generate/<path>/<case>.json \
  --device-id <device_id> \
  --custom-params '<json>'
```

### custom-params 示例

以太网用例（仅需 router）：
```json
{"routers":{"main_router":{"model":"asus_rt_ax86u","ip":"192.168.50.1","ssh":{"username":"AX86U","password":"New!123456"}}}}
```

WiFi 用例（需 WiFi SSID + router）：
```json
{"target_ssid":"AX86U","target_password":"Home1357","routers":{"main_router":{"model":"asus_rt_ax86u","ip":"192.168.50.1","ssh":{"username":"AX86U","password":"New!123456"}}}}
```

## 查看结果

```bash
# 日志目录
ls results/<YYYY.MM.DD_HH.MM.SS>/workflows/

# HTML 报告
results/<YYYY.MM.DD_HH.MM.SS>/workflows/workflow_summary.html

# 单用例日志
results/<YYYY.MM.DD_HH.MM.SS>/workflows/workflow_<id>_<name>.log
```

## 常见问题

| 问题 | 排查 |
|------|------|
| venv 未激活 | `source .venv/bin/activate` |
| DUT 离线 | `adb devices`，检查 USB 连接 |
| Router SSH 不通 | `ping 192.168.50.1`，路由器可能需重启 |
| Redis 模块缺失 | `pip install redis` |
| step 执行失败 | 检查 `adb root` 是否有权限 |
