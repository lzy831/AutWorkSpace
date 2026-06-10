# 通用编码规范

适用于所有源码文件（Python、YAML、JSON、Markdown、Shell 等）。与 `spec-yaml-format.md`、`step-check-design.md` 等专用规范互补，本文件只收录跨域通用规则。

## 换行符

所有源码、YAML、workflow JSON、Markdown、Shell 文件必须使用 LF 换行符（Unix 格式）。

- 开发环境 Windows + Samba 同步，极易引入 CRLF，导致 git diff 出现大量无意义改动
- AutoTestRes 仓库根目录 `.gitattributes` 已强制 LF，新建文件自动 LF
- 已有 CRLF 文件需手动修复

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
