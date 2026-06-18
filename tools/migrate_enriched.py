#!/usr/bin/env python3
"""
One-shot migration: old enriched JSON -> new spec YAML.

Usage:
    python migrate_enriched.py <enriched_cases_dir> [--output <specs_dir>] [--environment <env_id>]

    python migrate_enriched.py tsuite/Ethernet/Ethernet_MinTestSuite_cases/ \
        --environment ethernet_router_lan \
        --output specs/ethernet/

This script is intended to be run ONCE to migrate existing enriched JSONs.
After migration, new test cases should be written directly in spec YAML.
"""

import json
import sys
import yaml
from pathlib import Path
from typing import Any


def convert_enriched_to_spec(enriched: dict[str, Any], domain: str,
                              env_id: str) -> dict[str, Any]:
    """Convert a single enriched JSON to spec YAML dict."""
    spec: dict[str, Any] = {
        "_schema": "test_case_spec_v1",
        "id": enriched.get("No", ""),
        "name": enriched.get("display_name", enriched.get("No", "")),
        "priority": enriched.get("priority", "P1"),
        "domain": domain,
        "environment": env_id,
        "description": enriched.get("Test_Item", ""),
        "defaults": enriched.get("parameter_defaults", {}),
        "preconditions": [],
        "steps": [],
        "hardware": enriched.get("hardware_requirements", {}),
    }

    # --- preconditions from given ---
    given = enriched.get("given", {})
    given_desc = given.get("description", "")
    for chk in given.get("checks", []):
        spec["preconditions"].append({
            "description": given_desc or chk.get("description", ""),
            "manual": "QA 人工确认",
            "automation": {
                "api": chk["id"],
                "params": chk.get("params", {}),
            },
        })

    # --- steps from when ---
    when_items = enriched.get("when", [])

    i = 0
    while i < len(when_items):
        item = when_items[i]

        if item["action"] == "check":
            # Standalone check (no preceding step) — add to preconditions if not duplicate
            api_name = item["id"]
            already_in_precond = any(
                p["automation"]["api"] == api_name for p in spec["preconditions"]
            )
            if not already_in_precond:
                spec["preconditions"].append({
                    "description": item.get("description", ""),
                    "manual": "QA 人工确认",
                    "automation": {
                        "api": api_name,
                        "params": item.get("params", {}),
                    },
                })
            i += 1

        elif item["action"] == "step":
            # Collect consecutive steps
            steps_group = [item]
            i += 1
            while i < len(when_items) and when_items[i]["action"] == "step":
                steps_group.append(when_items[i])
                i += 1

            # The next item (if exists) should be a check
            chk_item = None
            if i < len(when_items) and when_items[i]["action"] == "check":
                chk_item = when_items[i]
                i += 1

            # Build operation from step group
            primary = steps_group[0]

            op_auto: dict[str, Any] = {
                "api": primary["id"],
                "params": primary.get("params", {}),
                "wait_after": primary.get("wait_after"),
            }

            # Remove None values
            if op_auto["wait_after"] is None:
                del op_auto["wait_after"]

            # Secondary steps become alternatives
            alternatives = []
            for sec in steps_group[1:]:
                alternatives.append({
                    "method": sec["id"],
                    "api": sec["id"],
                    "params": sec.get("params", {}),
                    "description": sec.get("description", ""),
                })
            if primary.get("note"):
                alternatives.append({
                    "method": "fallback",
                    "api": primary["id"],
                    "params": primary.get("params", {}),
                    "description": primary["note"],
                })
            if alternatives:
                op_auto["alternatives"] = alternatives

            step_entry: dict[str, Any] = {
                "operation": {
                    "description": primary.get("description", ""),
                    "manual": {
                        "actor": "QA",
                        "target": "DUT",
                        "action": primary.get("description", ""),
                    },
                    "automation": op_auto,
                },
            }

            # Build check if present
            if chk_item:
                chk_auto: dict[str, Any] = {
                    "api": chk_item["id"],
                    "params": chk_item.get("params", {}),
                    "timeout": chk_item.get("timeout"),
                    "on_failure": "abort",
                }
                if chk_auto["timeout"] is None:
                    del chk_auto["timeout"]

                step_entry["check"] = {
                    "description": chk_item.get("description", ""),
                    "manual": {
                        "actor": "QA",
                        "target": "DUT屏幕",
                        "action": chk_item.get("expect", chk_item.get("description", "")),
                    },
                    "automation": chk_auto,
                }

            spec["steps"].append(step_entry)

    # --- defaults: remove None values ---
    spec["defaults"] = {k: v for k, v in spec.get("defaults", {}).items() if v is not None}

    return spec


def spec_to_yaml_str(spec: dict[str, Any]) -> str:
    """Convert spec dict to YAML string with proper formatting."""

    class SpecDumper(yaml.Dumper):
        pass

    def str_representer(dumper, data):
        if "\n" in data:
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    SpecDumper.add_representer(str, str_representer)

    return yaml.dump(spec, Dumper=SpecDumper, allow_unicode=True, sort_keys=False, default_flow_style=False)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Migrate enriched JSON to spec YAML")
    parser.add_argument("enriched_dir", help="Directory with enriched JSON files")
    parser.add_argument("--output", "-o", default=None, help="Output directory for spec YAML files")
    parser.add_argument("--environment", "-e", default="ethernet_router_lan", help="Environment ID to use")
    args = parser.parse_args()

    enriched_dir = Path(args.enriched_dir)
    if not enriched_dir.exists():
        print(f"Error: directory not found: {enriched_dir}")
        sys.exit(1)

    domain = enriched_dir.parent.name.lower() if enriched_dir.parent.name != "." else "unknown"

    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = enriched_dir.parent.parent / "specs" / domain

    output_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for json_file in sorted(enriched_dir.glob("*.json")):
        if json_file.name.startswith("."):
            continue

        with open(json_file, "r", encoding="utf-8") as f:
            enriched = json.load(f)

        if enriched.get("_schema") != "enriched_test_case_v1":
            print(f"Skipping {json_file.name}: not enriched_test_case_v1")
            continue

        spec = convert_enriched_to_spec(enriched, domain, args.environment)
        yaml_str = spec_to_yaml_str(spec)

        yaml_file = output_dir / f"{spec['id']}.yaml"
        yaml_file.write_text(yaml_str, encoding="utf-8")
        print(f"Migrated: {json_file.name} -> {yaml_file}")
        count += 1

    print(f"\nMigrated {count} cases to {output_dir}")


if __name__ == "__main__":
    main()
