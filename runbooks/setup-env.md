# 首次环境搭建

## 1. 代码获取

```bash
git clone <repo-url>
cd AutoTestRes/scripts/python
```

## 2. 安装 Python 虚拟环境

```bash
python3 localtest_runner.py --setup-env
```

生成 `.venv/` 并安装所有依赖。后续有新增库时只安装增量。

## 3. 进入虚拟环境

```bash
source .venv/bin/activate
```

## 4. 验证环境

```bash
pytest tests/ -v
```

## 5. 确认 DUT 连接

```bash
adb devices
```

应显示目标 DUT 的 device_id。

## 6. 路由器连接确认

```bash
ping 192.168.50.1
```

确保 Controller 能 ping 通路由器。

## 7. 创建环境参数文件

在 `.claude/test_env.json` 中配置：

```json
{
  "device_id": "<DUT device_id>",
  "routers": {
    "main_router": {
      "model": "asus_rt_ax86u",
      "ip": "192.168.50.1",
      "ssh": { "username": "AX86U", "password": "<password>" }
    }
  },
  "wifi": {
    "target_ssid": "<SSID>",
    "target_password": "<password>"
  }
}
```
