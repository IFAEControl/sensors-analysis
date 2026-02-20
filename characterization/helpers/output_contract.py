from __future__ import annotations

from typing import Any, Mapping


def _is_mapping(value: Any) -> bool:
    return isinstance(value, Mapping)


def _path(base: str, key: str) -> str:
    return f"{base}.{key}" if base else key


def _append_missing(violations: list[str], base: str, required: list[str], node: Mapping[str, Any]) -> None:
    for key in required:
        if key not in node:
            violations.append(f"Missing key '{_path(base, key)}'")


def _require_mapping(violations: list[str], base: str, value: Any) -> Mapping[str, Any] | None:
    if not _is_mapping(value):
        violations.append(f"Expected mapping at '{base}'")
        return None
    return value


def validate_characterization_extended_contract(data: Mapping[str, Any]) -> list[str]:
    """Validate extended characterization summary contract (CR-01)."""
    violations: list[str] = []

    root = _require_mapping(violations, "", data)
    if root is None:
        return violations

    _append_missing(violations, "", ["meta", "analysis", "time_info", "plots"], root)

    analysis = _require_mapping(violations, "analysis", root.get("analysis"))
    plots = _require_mapping(violations, "plots", root.get("plots"))
    sanity = root.get("sanity_checks")
    generate_plots = bool(
        root.get("meta", {})
        .get("config", {})
        .get("generate_plots", True)
    )

    if analysis is None:
        return violations

    pd_map = _require_mapping(violations, "analysis.photodiodes", analysis.get("photodiodes"))
    if pd_map is None:
        return violations

    for pd_id, pd_node_raw in pd_map.items():
        pd_path = f"analysis.photodiodes.{pd_id}"
        pd_node = _require_mapping(violations, pd_path, pd_node_raw)
        if pd_node is None:
            continue
        _append_missing(violations, pd_path, ["meta", "time_info", "analysis", "filesets", "plots"], pd_node)

        filesets = _require_mapping(violations, f"{pd_path}.filesets", pd_node.get("filesets"))
        if filesets is None:
            continue

        for fs_key, fs_raw in filesets.items():
            fs_path = f"{pd_path}.filesets.{fs_key}"
            fs_node = _require_mapping(violations, fs_path, fs_raw)
            if fs_node is None:
                continue
            _append_missing(violations, fs_path, ["meta", "time_info", "analysis", "files", "plots"], fs_node)

            files = _require_mapping(violations, f"{fs_path}.files", fs_node.get("files"))
            if files is None:
                continue
            for file_key, file_raw in files.items():
                file_path = f"{fs_path}.files.{file_key}"
                file_node = _require_mapping(violations, file_path, file_raw)
                if file_node is None:
                    continue
                _append_missing(violations, file_path, ["file_info", "time_info", "analysis"], file_node)

    if generate_plots and plots is not None:
        plot_pd_map = _require_mapping(violations, "plots.photodiodes", plots.get("photodiodes"))
        if plot_pd_map is not None:
            for pd_id in pd_map.keys():
                if pd_id not in plot_pd_map:
                    violations.append(f"Missing key 'plots.photodiodes.{pd_id}'")

    if sanity is not None:
        sanity_root = _require_mapping(violations, "sanity_checks", sanity)
        if sanity_root is not None:
            for run_key, run_raw in sanity_root.items():
                if run_key in {"summary", "defined_checks"}:
                    continue
                run_path = f"sanity_checks.{run_key}"
                run_node = _require_mapping(violations, run_path, run_raw)
                if run_node is None:
                    continue
                _append_missing(violations, run_path, ["checks", "photodiodes"], run_node)
                run_pds = _require_mapping(violations, f"{run_path}.photodiodes", run_node.get("photodiodes"))
                if run_pds is None:
                    continue
                for pd_id, pd_sanity_raw in run_pds.items():
                    pd_sanity_path = f"{run_path}.photodiodes.{pd_id}"
                    pd_sanity = _require_mapping(violations, pd_sanity_path, pd_sanity_raw)
                    if pd_sanity is None:
                        continue
                    _append_missing(violations, pd_sanity_path, ["checks", "filesets"], pd_sanity)
                    fs_map = _require_mapping(violations, f"{pd_sanity_path}.filesets", pd_sanity.get("filesets"))
                    if fs_map is None:
                        continue
                    for fs_key, fs_sanity_raw in fs_map.items():
                        fs_sanity_path = f"{pd_sanity_path}.filesets.{fs_key}"
                        fs_sanity = _require_mapping(violations, fs_sanity_path, fs_sanity_raw)
                        if fs_sanity is None:
                            continue
                        _append_missing(violations, fs_sanity_path, ["checks", "sweepfiles"], fs_sanity)
                        sweep_map = _require_mapping(
                            violations,
                            f"{fs_sanity_path}.sweepfiles",
                            fs_sanity.get("sweepfiles"),
                        )
                        if sweep_map is None:
                            continue
                        for file_key, sweep_checks in sweep_map.items():
                            sweep_path = f"{fs_sanity_path}.sweepfiles.{file_key}"
                            if not _is_mapping(sweep_checks):
                                violations.append(f"Expected mapping at '{sweep_path}'")

    return violations


def validate_characterization_reduced_contract(data: Mapping[str, Any]) -> list[str]:
    """Validate reduced characterization summary has expected top-level keys."""
    violations: list[str] = []
    root = _require_mapping(violations, "", data)
    if root is None:
        return violations
    _append_missing(
        violations,
        "",
        ["characterization_id", "acquisition_time", "calibration", "photodiodes"],
        root,
    )
    if "photodiodes" in root and not _is_mapping(root.get("photodiodes")):
        violations.append("Expected mapping at 'photodiodes'")
    return violations


def format_contract_violations(violations: list[str], max_items: int = 20) -> str:
    if not violations:
        return ""
    visible = violations[:max_items]
    suffix = "" if len(violations) <= max_items else f"\n... and {len(violations) - max_items} more"
    return "\n".join(f"- {item}" for item in visible) + suffix
