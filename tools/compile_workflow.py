#!/usr/bin/env python3
"""
Compile spec YAML → workflow JSON.

Usage:
    python compile_workflow.py <spec_yaml_path> [--output <output_path>]
    python compile_workflow.py specs/ethernet/Ethernet_Func_002.yaml

Input:
    - spec YAML (e.g., specs/ethernet/Ethernet_Func_002.yaml)
    - environment YAML (referenced via spec.environment)
    - unique_apis.json (for API param schema lookup)

Output:
    - workflow JSON → atomic/workflows/auto_generate/<Module>_V*/<Category>/<CaseNo>.json
"""

import json
import sys
import yaml
from pathlib import Path
from typing import Any

# --- Path resolution ---

PROJECT_ROOT = Path(__file__).resolve().parents[2]  # ClaudeWorkSpace/tools -> project root
SPECS_DIR = Path(__file__).resolve().parent.parent / "specs"
ENVIRONMENTS_DIR = Path(__file__).resolve().parent.parent / "environments"
UNIQUE_APIS_PATH = PROJECT_ROOT / "scripts" / "python" / "atomic" / "tools" / "unique_apis.json"
WORKFLOWS_BASE = PROJECT_ROOT / "scripts" / "python" / "atomic" / "workflows" / "auto_generate"


def load_spec(spec_path: str) -> dict[str, Any]:
    """Load and validate a spec YAML file."""
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    return spec


def load_environment(env_id: str) -> dict[str, Any]:
    """Load an environment YAML by its id."""
    env_path = ENVIRONMENTS_DIR / f"{env_id}.yaml"
    if not env_path.exists():
        raise FileNotFoundError(f"Environment not found: {env_path}")
    with open(env_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_unique_apis() -> dict[str, dict[str, Any]]:
    """Load and index unique_apis.json by function_name."""
    raw = json.loads(UNIQUE_APIS_PATH.read_text(encoding="utf-8"))
    apis = {}
    for api in raw.get("unique_apis", []):
        name = api.get("function_name", "")
        if name:
            apis[name] = api
    return apis


# --- Defaults merging ---

def merge_defaults(env: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    """Merge spec.defaults over environment.defaults."""
    merged = dict(env.get("defaults", {}))
    merged.update(spec.get("defaults", {}))
    return merged


# --- API lookup ---

def lookup_params(api_name: str, unique_apis: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """
    Lookup param schema from unique_apis.json.
    Returns normalized param dict: {param_name: {name, type, required, default, description}}
    """
    api = unique_apis.get(api_name)
    if api is None:
        print(f"Warning: API '{api_name}' not found in unique_apis.json")
        return {}
    return api.get("params", {})


# --- Node generation ---

def _get_auto(item: dict) -> dict:
    """兼容新旧两种 automation 格式：
        新: {api: xxx, params: {...}}
        旧: {automation: {api: xxx, params: {...}}}
    """
    return item.get("automation") or item


def build_nodes(spec: dict[str, Any], unique_apis: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert spec.preconditions + spec.procedure to workflow nodes with unique IDs."""
    nodes = []
    counter: dict[str, int] = {}

    def unique_id(api_name: str) -> str:
        if api_name in counter:
            counter[api_name] += 1
            return f"{api_name}_{counter[api_name]}"
        else:
            counter[api_name] = 0
            return api_name

    x = 100

    # Precondition nodes — supports two formats:
    #   Format A (check-only): {description, automation: {api, params}}
    #   Format B (step+check):  {operation: {description, automation: {api, params}},
    #                             check:    {description, automation: {api, params}}}
    for precond in spec.get("preconditions", []):
        if "operation" in precond:
            # Format B: step (+ optional check)
            op = precond["operation"]
            op_api = _get_auto(op)["api"]
            op_id = unique_id(op_api)
            op_schema = lookup_params(op_api, unique_apis)
            op_values = _get_auto(op).get("params", {})

            nodes.append({
                "id": op_id,
                "type": "step",
                "label": op_id,
                "description": op.get("description", precond.get("description", "")),
                "position": {"x": x, "y": 200},
                "params": op_values,
                "param_config": op_schema,
                "step_id": op_api,
            })
            x += 200

            if "check" in precond:
                chk = precond["check"]
                chk_api = _get_auto(chk)["api"]
                chk_schema = lookup_params(chk_api, unique_apis)
                chk_values = _get_auto(chk).get("params", {})

                chk_id = unique_id(chk_api)
                nodes.append({
                    "id": chk_id,
                    "type": "check",
                    "label": chk_id,
                    "description": chk.get("description", precond.get("description", "")),
                    "position": {"x": x, "y": 200},
                    "params": chk_values,
                    "param_config": chk_schema,
                    "check_id": chk_api,
                })
                x += 200

        else:
            # Format A: check-only
            auto = _get_auto(precond)
            api_name = auto["api"]
            node_id = unique_id(api_name)
            precond_schema = lookup_params(api_name, unique_apis)
            precond_values = auto.get("params", {})

            nodes.append({
                "id": node_id,
                "type": "check",
                "label": node_id,
                "description": precond["description"],
                "position": {"x": x, "y": 200},
                "params": precond_values,
                "param_config": precond_schema,
                "check_id": api_name,
            })
            x += 200

    # Procedure items: supports step-only, check-only, and step+check pair
    for step_item in spec.get("procedure", spec.get("steps", [])):
        has_op = "operation" in step_item
        has_chk = "check" in step_item

        # ── Step node (if operation present) ──
        if has_op:
            op = step_item["operation"]
            op_api = _get_auto(op)["api"]
            op_id = unique_id(op_api)
            op_schema = lookup_params(op_api, unique_apis)
            op_values = _get_auto(op).get("params", {})

            nodes.append({
                "id": op_id,
                "type": "step",
                "label": op_id,
                "description": op.get("description", ""),
                "position": {"x": x, "y": 200},
                "params": op_values,
                "param_config": op_schema,
                "step_id": op_api,
            })
            x += 200

            # Insert wait node if wait_after specified (check both operation and automation level)
            wait_after = op.get("wait_after") or _get_auto(op).get("wait_after")
            if wait_after and wait_after > 0:
                wait_id = unique_id("step_wait_seconds")
                wait_schema = lookup_params("step_wait_seconds", unique_apis)
                nodes.append({
                    "id": wait_id,
                    "type": "step",
                    "label": wait_id,
                    "description": f"等待 {wait_after}s",
                    "position": {"x": x, "y": 200},
                    "params": {"seconds": wait_after},
                    "param_config": wait_schema,
                    "step_id": "step_wait_seconds",
                })
                x += 200

        # ── Check node (if check present) ──
        if has_chk:
            chk = step_item["check"]
            chk_api = _get_auto(chk)["api"]
            chk_id = unique_id(chk_api)
            chk_schema = lookup_params(chk_api, unique_apis)
            chk_values = _get_auto(chk).get("params", {})

            nodes.append({
                "id": chk_id,
                "type": "check",
                "label": chk_id,
                "description": chk.get("description", ""),
                "position": {"x": x, "y": 200},
                "params": chk_values,
                "param_config": chk_schema,
                "check_id": chk_api,
            })
            x += 200

    return nodes


# --- Edge generation ---

def build_edges(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generate edges connecting nodes in sequence."""
    edges = []
    for i in range(len(nodes) - 1):
        src = nodes[i]["id"]
        tgt = nodes[i + 1]["id"]
        edges.append({
            "id": f"edge_{src}_{tgt}",
            "source": src,
            "target": tgt,
            "condition": "pass",
            "label": None,
        })
    return edges


# --- Output path ---

_DOMAIN_DIR_MAP = {
    "ethernet": "Ethernet_V1.3_test_case/Function",
    "wifi": "wifi_BT_testcase_v1.1/Wifi_function",
}


def infer_output_path(spec: dict[str, Any]) -> Path:
    """
    Infer workflow JSON output path.
    Priority: _source.file > domain mapping.
    """
    case_id = spec["id"]

    # 1) _source.file → dir name
    source_file = spec.get("_source", {}).get("file", "")
    if source_file:
        dir_name = Path(source_file).stem
        sheet = spec.get("_source", {}).get("sheet", "Function")
        candidate = WORKFLOWS_BASE / dir_name / sheet
        if (WORKFLOWS_BASE / dir_name).exists():
            return candidate / f"{case_id}.json"
        sanitized = dir_name.replace("&", "_")
        if (WORKFLOWS_BASE / sanitized).exists():
            return WORKFLOWS_BASE / sanitized / sheet / f"{case_id}.json"

    # 2) domain mapping
    domain = spec.get("domain", "")
    mapped = _DOMAIN_DIR_MAP.get(domain)
    if mapped:
        return WORKFLOWS_BASE / mapped / f"{case_id}.json"

    # 3) Fallback
    return WORKFLOWS_BASE / "Function" / f"{case_id}.json"


# --- Main compilation ---

def build_precondition_text(spec: dict[str, Any]) -> str:
    """Build precondition string from preconditions list."""
    preconds = spec.get("preconditions", [])
    if not preconds:
        return ""
    parts = []
    for p in preconds:
        if "operation" in p:
            op_desc = p["operation"].get("description", "")
            if "check" in p:
                chk_desc = p["check"].get("description", "")
                parts.append(f"{op_desc} → {chk_desc}")
            else:
                parts.append(op_desc)
        else:
            parts.append(p.get("description", ""))
    return "; ".join(parts)


def build_steps_text(spec: dict[str, Any]) -> str:
    """Build original steps text for backwards compatibility."""
    lines = []
    for i, step_item in enumerate(spec.get("steps", []), 1):
        op = step_item["operation"]["description"]
        chk = step_item["check"]["description"]
        lines.append(f"{i}. {op}")
        lines.append(f"   → {chk}")
    return "\n".join(lines)


_CN_PUNCT_MAP = {
    '；': ';', '（': '(', '）': ')', '，': ',',
    '：': ':', '。': '.', '、': ', ',
}


def _sanitize_punctuation(obj: Any) -> Any:
    """Recursively replace Chinese punctuation with ASCII in all string values."""
    if isinstance(obj, str):
        for cn, en in _CN_PUNCT_MAP.items():
            obj = obj.replace(cn, en)
        return obj
    if isinstance(obj, dict):
        return {k: _sanitize_punctuation(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_punctuation(v) for v in obj]
    return obj


def compile_workflow(spec_path: str) -> dict[str, Any]:
    """Compile a spec YAML into a workflow JSON dict."""
    spec = load_spec(spec_path)
    env_id = spec.get("testbed") or spec.get("environment")
    if not env_id:
        raise ValueError("spec requires 'testbed' (or 'environment') field")
    env = load_environment(env_id)
    unique_apis = load_unique_apis()

    merge_defaults(env, spec)

    nodes = build_nodes(spec, unique_apis)
    edges = build_edges(nodes)

    source = spec.get("_source", {})

    mmd_file = env.get('topology_diagram', '')

    workflow = {
        "id": f"auto_generate/{Path(infer_output_path(spec)).relative_to(WORKFLOWS_BASE).as_posix().replace('.json', '')}",
        "name": spec["id"],
        "display_name": spec["name"],
        "environment": f"../environments/{env_id}.yaml",
        "topology_diagram": f"../environments/{mmd_file}" if mmd_file else "",
        "description": spec.get("description", "").strip(),
        "category": "network",
        "module": "network",
        "submodule": spec.get("domain", ""),
        "priority": spec.get("priority", "P1"),
        "precondition": build_precondition_text(spec),
        "steps": build_steps_text(spec),
        "expected": spec.get("description", "").strip(),
        "data": "",
        "author": "compile_workflow",
        "nodes": nodes,
        "edges": edges,
        "metadata": {},
        "_excel_metadata": {
            "source_file": str(source.get("file", "")),
            "source_sheet": str(source.get("sheet", "")),
            "source_row": source.get("row", ""),
            "case_id": spec["id"],
        },
    }
    return _sanitize_punctuation(workflow)


# --- CLI ---

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Compile spec YAML → workflow JSON")
    parser.add_argument("spec_path", help="Path to spec YAML file")
    parser.add_argument("--output", "-o", help="Output path (auto-inferred if omitted)")
    args = parser.parse_args()

    workflow = compile_workflow(args.spec_path)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = infer_output_path(yaml.safe_load(open(args.spec_path, "r", encoding="utf-8")))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)

    print(f"Workflow written to: {output_path}")


if __name__ == "__main__":
    main()
