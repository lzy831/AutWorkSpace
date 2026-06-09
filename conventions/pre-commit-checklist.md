# Pre-Commit Checklist

提交前自动执行的检查清单。调用方式：用户说"生成 commit"或"提交前检查"时自动逐项执行。

---

## 1. 汇总文档同步

检查 `ClaudeWorkSpace/decisions/ethernet-automation-summary.md` 与实际是否一致：

- [ ] auto/pending/manual 各分类的用例数量正确（数 `auto_status` 字段）
- [ ] 每个 auto 用例的描述与 YAML `name` 一致
- [ ] pending 用例的"待实现 step/check"列已更新（如果新增了 step）
- [ ] manual 列表不包含已移至 auto 的用例

脚本：
```bash
# 统计各状态数量
grep -r "auto_status:" ClaudeWorkSpace/specs/ethernet/ | sed 's/.*: //'
```

---

## 2. 中文标点符号

检查 YAML、JSON、Python 源码中不包含中文标点：

**禁止的中文标点**：`，` `；` `：` `！` `？` `（` `）` `。` `、` `“` `”`

**允许的场景**：
- YAML `description` 字段中的中文描述文本（仅限 `。` 用于多句描述）
- Python docstring 中的中文描述文本
- Markdown 文档

**必须检查的文件**：
- YAML spec 中的 `api`、`params`、`name`（不含 description）字段
- JSON workflow 中的 `label`、`step_id`、`check_id` 字段
- Python 源码中的日志字符串、异常消息、step/check 名称内联字符串

脚本：
```bash
# 检查 Python 源码中的中文标点（排除 docstring 和注释）
grep -rPn '[，；：！？（）、]' scripts/python/atomic/step_impl/peripheral/network/ethernet/ \
  scripts/python/atomic/check_impl/peripheral/network/ethernet/ \
  scripts/python/lib/common/peripheral/network/ethernet/ \
  scripts/python/lib/common/peripheral/network/router/ \
  scripts/python/lib/common/system/settings_navigator_eth.py \
  2>/dev/null | grep -v '^\s*#' | grep -v '"""' | grep -v "description"
```

---

## 3. 变更范围审计

检查 git diff 是否包含不应该本分支修改的文件：

**允许修改的目录**（与 PROJECT.md 一致）：
- `scripts/python/atomic/step_impl/peripheral/network/`
- `scripts/python/atomic/check_impl/peripheral/network/`
- `scripts/python/lib/common/peripheral/network/`
- `scripts/python/lib/common/system/settings_navigator*.py`
- `scripts/python/atomic/workflows/auto_generate/Ethernet_V1.3_test_case/`
- `ClaudeWorkSpace/`

**特别关注**：
- [ ] `bin/` 目录是否有二进制文件变动（Samba 同步导致的时间戳变更）
- [ ] `scripts/aut_service_server/`、`scripts/aut_ws_server/` 是否有变动
- [ ] `scripts/python/config/` 是否有非预期的配置变更
- [ ] `report/` 目录是否有变动

脚本：
```bash
git diff --stat --name-only HEAD
# 人工审核：每个文件路径是否在上方允许列表内
```

---

## 4. Step/Check 清单同步

### 4.1 __init__.py 同步

`scripts/python/lib/common/peripheral/network/ethernet/__init__.py` 必须与实际 step/check 函数列表一致：

- [ ] `from .ethernet_step import (...)` 包含所有 lib 层 step 函数
- [ ] `from .ethernet_check import (...)` 包含所有 lib 层 check 函数
- [ ] `__all__` 列表与 import 一致
- [ ] docstring 中的 API 清单与 `__all__` 一致

### 4.2 未使用的 step/check

- [ ] 新增的 step/check 至少被一个 YAML spec 引用
- [ ] 未被任何 YAML 引用的 step/check 应标记或删除
- [ ] atomic 层装饰器 `name` 与函数名一致

脚本：
```bash
# 列出 atomic step/check 装饰器名称
grep -A1 '@composer_step' scripts/python/atomic/step_impl/peripheral/network/ethernet/ethernet_steps.py | grep 'name=' 
grep -A1 '@composer_check' scripts/python/atomic/check_impl/peripheral/network/ethernet/ethernet_checks.py | grep 'name='

# 列出 YAML 中引用的 api
grep -rh 'api:' ClaudeWorkSpace/specs/ethernet/ | grep -v '^[[:space:]]*#' | sort -u

# 对比差异
```

### 4.3 Inventory 更新

如果新增或删除 step/check，检查：
- [ ] `ClaudeWorkSpace/references/ethernet-step-check-inventory.md` 已同步更新

---

## 5. YAML → JSON 编译验证

- [ ] 所有 `auto_status: auto` 的 YAML 都有对应的 workflow JSON
- [ ] JSON 文件生成时间与 YAML 最后修改时间接近（未过期）

脚本：
```bash
# 检查 auto YAML 是否都有对应 JSON
for yaml in ClaudeWorkSpace/specs/ethernet/Ethernet_*.yaml; do
  if grep -q 'auto_status: auto' "$yaml"; then
    json="scripts/python/atomic/workflows/auto_generate/Ethernet_V1.3_test_case/Function/$(basename ${yaml%.yaml}.json)"
    [ -f "$json" ] || echo "MISSING: $json (from $yaml)"
  fi
done
```

---

## 6. Python 语法

- [ ] 所有修改的 Python 文件通过 `py_compile` 语法检查
- [ ] `__init__.py` 的 import 路径在服务器环境中可解析

脚本：
```bash
python -c "
import py_compile, sys
files = ['...']  # git diff 中修改的 Python 文件列表
for f in files:
    try:
        py_compile.compile(f, doraise=True)
        print(f'OK {f}')
    except py_compile.PyCompileError as e:
        print(f'FAIL {f}: {e}')
        sys.exit(1)
"
```

---

## 7. 换行符

- [ ] 所有文件使用 LF 换行符（非 CRLF）
- [ ] 文件末尾有且仅有一个换行符

脚本：
```bash
git diff --stat HEAD | grep -v 'Bin ' | awk '{print $1}' | while read f; do
  file "$f" | grep -q 'CRLF' && echo "CRLF: $f"
done
```

---

## 检查顺序

执行时按 1→7 依次检查，遇失败停止并报告。全部通过后再生成 commit。

## 自动修复

以下检查可自动修复：
- 检查 2（中文标点）→ 自动替换为英文标点
- 检查 7（换行符）→ 自动 `dos2unix`

其余检查需要人工确认后再修复。
