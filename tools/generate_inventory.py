#!/usr/bin/env python3
"""
Generate step/check inventory Markdown from spec YAML files.

Usage:
    python generate_inventory.py <domain> [--output <output_path>]

    python generate_inventory.py ethernet
    # -> tsuite/ethernet/ethernet_step_check_inventory.md
"""

import sys
import json
import yaml
from pathlib import Path
from typing import Any
from collections import defaultdict


PROJECT_ROOT = Path(__file__).resolve().parents[4]  # scripts/python/tsuite/tools -> project root
SPECS_DIR = Path(__file__).resolve().parent.parent / "specs"
UNIQUE_APIS_PATH = PROJECT_ROOT / "scripts" / "python" / "atomic" / "tools" / "unique_apis.json"
TSUITE_DIR = Path(__file__).resolve().parent.parent


def load_unique_apis() -> dict[str, dict[str, Any]]:
    """Load and index unique_apis.json by function_name."""
    raw = json.loads(UNIQUE_APIS_PATH.read_text(encoding="utf-8"))
    apis = {}
    for api in raw.get("unique_apis", []):
        name = api.get("function_name", "")
        if name:
            apis[name] = api
    return apis


def collect_api_usage(domain: str) -> dict[str, dict[str, Any]]:
    """Scan all spec YAML files in domain, return {api_name: {kind, cases, params}}."""
    usage: dict[str, dict[str, Any]] = defaultdict(lambda: {"kind": None, "cases": [], "params": None})

    domain_dir = SPECS_DIR / domain
    if not domain_dir.exists():
        print(f"No specs directory found for domain: {domain}")
        return {}

    for spec_file in sorted(domain_dir.glob("*.yaml")):
        with open(spec_file, "r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)

        case_id = spec.get("id", spec_file.stem)

        # Collect from preconditions
        for precond in spec.get("preconditions", []):
            auto = precond.get("automation", {})
            api = auto.get("api")
            if api:
                entry = usage[api]
                entry["kind"] = "check"
                if case_id not in entry["cases"]:
                    entry["cases"].append(case_id)
                if entry["params"] is None:
                    entry["params"] = auto.get("params", {})

        # Collect from steps
        for step_item in spec.get("steps", []):
            op = step_item.get("operation", {}).get("automation", {})
            chk = step_item.get("check", {}).get("automation", {})

            # Operation (step)
            op_api = op.get("api")
            if op_api:
                entry = usage[op_api]
                entry["kind"] = "step"
                if case_id not in entry["cases"]:
                    entry["cases"].append(case_id)
                if entry["params"] is None:
                    entry["params"] = op.get("params", {})

                # Also collect alternatives
                for alt in op.get("alternatives", []):
                    alt_api = alt.get("api")
                    if alt_api:
                        alt_entry = usage[alt_api]
                        alt_entry["kind"] = "step"
                        if case_id not in alt_entry["cases"]:
                            alt_entry["cases"].append(case_id)

            # Check
            chk_api = chk.get("api")
            if chk_api:
                entry = usage[chk_api]
                entry["kind"] = "check"
                if case_id not in entry["cases"]:
                    entry["cases"].append(case_id)
                if entry["params"] is None:
                    entry["params"] = chk.get("params", {})

    return dict(usage)


def generate_inventory_markdown(domain: str, usage: dict[str, dict[str, Any]],
                                unique_apis: dict[str, dict[str, Any]]) -> str:
    """Generate inventory Markdown."""
    steps = {k: v for k, v in usage.items() if v["kind"] == "step"}
    checks = {k: v for k, v in usage.items() if v["kind"] == "check"}

    lines = [
        f"# {domain.capitalize()} 测试用例 Step & Check 清单",
        "",
        f"> 自动生成自 `specs/{domain}/`。列出当前模块所需的所有 step 和 check，并标注实现状态。",
        "",
        "---",
        "",
        "## Steps（操作）",
        "",
    ]

    if steps:
        for name, info in sorted(steps.items()):
            api = unique_apis.get(name, {})
            status = "已实现" if name in unique_apis else "缺失"

            lines.append(f"### {name}")
            lines.append("")
            lines.append(f"- **状态**: {status}")
            lines.append(f"- **实现文件**: {api.get('source_file', '—')}")
            lines.append(f"- **描述**: {info.get('description', '—')}")
            lines.append(f"- **适用用例**: {', '.join(info['cases'])}")
            lines.append(f"- **参数**: {json.dumps(info['params'], ensure_ascii=False) if info['params'] else '无'}")
            lines.append("")
    else:
        lines.append("_无 step_\n")

    lines.append("## Checks（检查）")
    lines.append("")

    if checks:
        for name, info in sorted(checks.items()):
            api = unique_apis.get(name, {})
            status = "已实现" if name in unique_apis else "缺失"

            lines.append(f"### {name}")
            lines.append("")
            lines.append(f"- **状态**: {status}")
            lines.append(f"- **实现文件**: {api.get('source_file', '—')}")
            lines.append(f"- **描述**: {info.get('description', '—')}")
            lines.append(f"- **适用用例**: {', '.join(info['cases'])}")
            lines.append(f"- **参数**: {json.dumps(info['params'], ensure_ascii=False) if info['params'] else '无'}")
            lines.append("")
    else:
        lines.append("_无 check_\n")

    # Missing summary table
    missing_steps = [k for k in steps if k not in unique_apis]
    missing_checks = [k for k in checks if k not in unique_apis]
    if missing_steps or missing_checks:
        lines.append("---")
        lines.append("")
        lines.append("## 缺失/待实现")
        lines.append("")
        lines.append("| 名称 | 类型 | 状态 |")
        lines.append("|------|------|------|")
        for name in sorted(missing_steps):
            lines.append(f"| {name} | step | 缺失 |")
        for name in sorted(missing_checks):
            lines.append(f"| {name} | check | 缺失 |")
        lines.append("")

    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate step/check inventory from spec YAML")
    parser.add_argument("domain", help="Domain name (e.g., ethernet)")
    parser.add_argument("--output", "-o", help="Output path (auto-inferred if omitted)")
    args = parser.parse_args()

    usage = collect_api_usage(args.domain)
    unique_apis = load_unique_apis()
    markdown = generate_inventory_markdown(args.domain, usage, unique_apis)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = TSUITE_DIR / args.domain / f"{args.domain}_step_check_inventory.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")

    print(f"Inventory written to: {output_path}")


if __name__ == "__main__":
    main()
