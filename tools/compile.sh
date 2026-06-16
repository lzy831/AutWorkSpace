#!/bin/bash
# compile.sh - 手动将 YAML spec 编译为 workflow JSON
# Usage:
#   ./compile.sh specs/ethernet/Ethernet_Func_001.yaml             # 自动推断输出路径
#   ./compile.sh specs/ethernet/Ethernet_Func_001.yaml -o out.json  # 指定输出路径
#   ./compile.sh specs/ethernet/                                    # 编译目录下所有 auto YAML

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPILE_PY="$SCRIPT_DIR/compile_workflow.py"
PYTHON_BIN="$PROJECT_ROOT/../scripts/python/.venv/bin/python3"

YAML_PATH=""
OUT_PATH=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output) OUT_PATH="$2"; shift 2 ;;
        -*) echo "Unknown option: $1"; exit 1 ;;
        *) YAML_PATH="$1"; shift ;;
    esac
done

if [ -z "$YAML_PATH" ]; then
    echo "Usage: compile.sh <yaml_file_or_dir> [-o output.json]"
    echo ""
    echo "Examples:"
    echo "  compile.sh specs/ethernet/Ethernet_Func_001.yaml"
    echo "  compile.sh specs/ethernet/Ethernet_Func_001.yaml -o /tmp/test.json"
    echo "  compile.sh specs/ethernet/"
    exit 1
fi

# Resolve to absolute path before cd
if [[ "$YAML_PATH" != /* ]]; then
    YAML_PATH="$(pwd)/$YAML_PATH"
fi
if [ ! -e "$YAML_PATH" ]; then
    echo "ERROR: $YAML_PATH not found"
    exit 1
fi

cd "$PROJECT_ROOT/../scripts/python"

if [ -d "$YAML_PATH" ]; then
    for yaml in "$YAML_PATH"/*.yaml; do
        if grep -q "auto_status: auto" "$yaml" 2>/dev/null; then
            fn=$(basename "$yaml" .yaml)
            if [ -n "$OUT_PATH" ]; then
                "$PYTHON_BIN" "$COMPILE_PY" "$yaml" -o "$OUT_PATH/${fn}.json" 2>&1 | tail -1
            else
                "$PYTHON_BIN" "$COMPILE_PY" "$yaml" 2>&1 | tail -1
            fi
        fi
    done
elif [ -n "$OUT_PATH" ]; then
    "$PYTHON_BIN" "$COMPILE_PY" "$YAML_PATH" -o "$OUT_PATH" 2>&1 | tail -1
else
    "$PYTHON_BIN" "$COMPILE_PY" "$YAML_PATH" 2>&1 | tail -1
fi
