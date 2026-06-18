# 通用编码规范

适用于所有源码文件（Python、YAML、JSON、Markdown、Shell 等）。与 `spec-yaml-format.md`、`step-check-design.md` 等专用规范互补，本文件只收录跨域通用规则。

## 换行符

所有源码、YAML、workflow JSON、Markdown、Shell 文件必须使用 LF 换行符（Unix 格式）。

- 开发环境 Windows + Samba 同步，极易引入 CRLF，导致 git diff 出现大量无意义改动

检查方式：
```bash
# 扫描 CRLF 文件
file scripts/python/lib/common/peripheral/network/ethernet/*.py | grep CRLF
```

修复方式：
```bash
sed -i 's/\r$//' <file>
```

## 文件编码

所有文件使用 UTF-8 编码（无 BOM）。

## 文件末尾

文件末尾有且仅有一个换行符（POSIX 标准）。

## 中文标点符号

除 atomic 层外，所有源码（Python、YAML、JSON）、workflow JSON、decorator 元数据中禁止使用中文标点符号。

**适用范围：**
- lib 层 Python：注释、docstring、日志消息
- YAML spec：所有字段（`description`、`name`、precondition 描述等）
- JSON workflow：所有字符串值

**豁免：**
- `scripts/python/atomic/step_impl/` 和 `scripts/python/atomic/check_impl/` 下的文件允许使用中文标点（decorator description 等字段可能用于页面端展示，中文标点更合适）

**替换表：**

| 中文 | ASCII |
|------|-------|
| `，` | `,` |
| `；` | `;` |
| `：` | `:` |
| `！` | `!` |
| `？` | `?` |
| `（` | `(` |
| `）` | `)` |
| `。` | `.` |
| `、` | `,` |
| `—` | `-` |

**检查方式：**
```bash
# 扫描 Python/YAML/JSON 文件中的中文标点
python -c "
import os
cn = set(',;:!?()')
for root, dirs, files in os.walk('.'):
    for fn in files:
        if not fn.endswith(('.py','.yaml','.json')): continue
        path = os.path.join(root, fn)
        for i, line in enumerate(open(path, encoding='utf-8'), 1):
            if any(c in cn for c in line):
                print(f'{path}:{i}: {line.rstrip()[:100]}')
"
```

**修复方式：**
```bash
# 批量替换（需确认范围）
python -c "
table = str.maketrans({',':',',';':';',':':':','!':'!','?':'?','(':'(',')':')','.':'.','、':','})
# 对目标文件执行替换
"
```
