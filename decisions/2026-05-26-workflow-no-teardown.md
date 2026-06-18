# 设计决策: Workflow 暂无 Teardown 机制

## 背景

workflow 执行模型只有 step → check 链，没有 `finally` / `teardown` / `always_run` 语义。
如果某步失败且设置了 `on_failure: abort`，后续所有节点（包括恢复性步骤）会被跳过。

## 影响

对于会改变物理环境状态的用例（如 `Ethernet_new_function_002` 改 PC 网卡为 10M FDX），
中途失败可能导致环境无法自动恢复。

## 临时方案

恢复性步骤放在 procedure 末尾，且前面步骤不使用 `on_failure: abort`。
即使中间有小失败，restore 也会执行。

## 长期方向

已与 workflow owner 沟通，后续增加 teardown 概念。
