from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional


@dataclass
class CallingArguments:
    calib_files_path: Optional[str]
    plot_format: Optional[str]
    output_path: Optional[str]
    log_file: bool
    overwrite: bool
    no_plots: bool

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CallingArguments":
        return cls(
            calib_files_path=data.get("calib_files_path"),
            plot_format=data.get("plot_format"),
            output_path=data.get("output_path"),
            log_file=bool(data.get("log_file", False)),
            overwrite=bool(data.get("overwrite", False)),
            no_plots=bool(data.get("no_plots", False)),
        )


@dataclass
class SystemInfo:
    username: Optional[str]
    cwd: Optional[str]
    os: Optional[str]
    os_release: Optional[str]
    os_version: Optional[str]
    machine: Optional[str]
    architecture: Optional[str]
    python_version: Optional[str]
    hostname: Optional[str]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SystemInfo":
        return cls(
            username=data.get("username"),
            cwd=data.get("cwd"),
            os=data.get("os"),
            os_release=data.get("os_release"),
            os_version=data.get("os_version"),
            machine=data.get("machine"),
            architecture=data.get("architecture"),
            python_version=data.get("python_version"),
            hostname=data.get("hostname"),
        )


@dataclass
class UsedConfig:
    plot_output_format: Optional[str]
    generate_plots: bool

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "UsedConfig":
        return cls(
            plot_output_format=data.get("plot_output_format"),
            generate_plots=bool(data.get("generate_plots", False)),
        )


@dataclass
class Meta:
    calling_arguments: CallingArguments
    calib_id: Optional[str]
    calib_files_path: Optional[str]
    root_output_path: Optional[str]
    calibration_outputs_path: Optional[str]
    reports_path: Optional[str]
    execution_date: Optional[str]
    system: SystemInfo
    config: UsedConfig

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Meta":
        return cls(
            calling_arguments=CallingArguments.from_dict(
                data.get("calling_arguments", {})),
            calib_id=data.get("calib_id"),
            calib_files_path=data.get("calib_files_path"),
            root_output_path=data.get("root_output_path"),
            calibration_outputs_path=data.get("calibration_outputs_path"),
            reports_path=data.get("reports_path"),
            execution_date=data.get("execution_date"),
            system=SystemInfo.from_dict(data.get("system", {})),
            config=UsedConfig.from_dict(data.get("config", {})),
        )


@dataclass
class TimeAnalysis:
    min_ts: Optional[int]
    max_ts: Optional[int]
    elapsed_time_s: Optional[int]
    min_dt: Optional[str]
    max_dt: Optional[str]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "TimeAnalysis":
        return cls(
            min_ts=data.get("min_ts"),
            max_ts=data.get("max_ts"),
            elapsed_time_s=data.get("elapsed_time_s"),
            min_dt=data.get("min_dt"),
            max_dt=data.get("max_dt"),
        )


@dataclass
class ResultsAnalysis:
    time: TimeAnalysis
    file_sets: Dict[str, List[str]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ResultsAnalysis":
        time = TimeAnalysis.from_dict(data.get("time", {}))
        file_sets_raw = data.get("file_sets", {}) or {}
        file_sets = {key: list(value) for key, value in file_sets_raw.items()}
        return cls(time=time, file_sets=file_sets)


@dataclass
class LinRegValues:
    x_var: Optional[str]
    y_var: Optional[str]
    slope: Optional[float]
    intercept: Optional[float]
    r_value: Optional[float]
    p_value: Optional[float]
    stderr: Optional[float]
    intercept_stderr: Optional[float]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "LinRegValues":
        return cls(
            x_var=data.get("x_var"),
            y_var=data.get("y_var"),
            slope=data.get("slope"),
            intercept=data.get("intercept"),
            r_value=data.get("r_value"),
            p_value=data.get("p_value"),
            stderr=data.get("stderr"),
            intercept_stderr=data.get("intercept_stderr"),
        )


@dataclass
class PedestalStats:
    mean: Optional[float]
    std: Optional[float]
    weighted: bool
    ndof: Optional[int]
    chi2: Optional[float]
    chi2_reduced: Optional[float]
    exec_error: bool

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PedestalStats":
        return cls(
            mean=data.get("mean"),
            std=data.get("std"),
            weighted=bool(data.get("weighted", False)),
            ndof=data.get("ndof"),
            chi2=data.get("chi2"),
            chi2_reduced=data.get("chi2_reduced"),
            exec_error=bool(data.get("exec_error", False)),
        )


@dataclass
class Pedestals:
    pm: PedestalStats
    refpd: PedestalStats

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Pedestals":
        return cls(
            pm=PedestalStats.from_dict(data.get("pm", {})),
            refpd=PedestalStats.from_dict(data.get("refpd", {})),
        )


@dataclass
class SetAnalysis:
    lr_refpd_vs_pm: LinRegValues
    pedestals: Pedestals

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SetAnalysis":
        return cls(
            lr_refpd_vs_pm=LinRegValues.from_dict(
                data.get("lr_refpd_vs_pm", {})),
            pedestals=Pedestals.from_dict(data.get("pedestals", {})),
        )


@dataclass
class CalibSet:
    wave_length: Optional[str]
    filter_wheel: Optional[str]
    analysis: SetAnalysis

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CalibSet":
        return cls(
            wave_length=data.get("wave_length"),
            filter_wheel=data.get("filter_wheel"),
            analysis=SetAnalysis.from_dict(data.get("analysis", {})),
        )


@dataclass
class Plots:
    timeseries: Optional[str] = None
    temperature_hist: Optional[str] = None
    humidity_hist: Optional[str] = None
    extra_plots: Dict[str, Optional[str]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Plots":
        """Parse plots from dict, capturing both known and dynamic plot entries."""
        extra_plots = {}
        known_keys = {"timeseries", "temperature_hist", "humidity_hist"}
        for key, value in (data or {}).items():
            if key not in known_keys:
                extra_plots[key] = value
        return cls(
            timeseries=data.get("timeseries"),
            temperature_hist=data.get("temperature_hist"),
            humidity_hist=data.get("humidity_hist"),
            extra_plots=extra_plots,
        )


@dataclass
class SanityCheckEntry:
    check_name: Optional[str]
    check_args: Optional[str]
    passed: bool
    info: Optional[str]
    severity: Optional[str]
    exec_error: bool
    internal: bool
    check_explanation: Optional[str]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SanityCheckEntry":
        return cls(
            check_name=data.get("check_name"),
            check_args=data.get("check_args"),
            passed=bool(data.get("passed", False)),
            info=data.get("info"),
            severity=data.get("severity"),
            exec_error=bool(data.get("exec_error", False)),
            internal=bool(data.get("internal", False)),
            check_explanation=data.get("check_explanation"),
        )


@dataclass
class SanityChecksSummaryDetails:
    errors_passed: int
    warnings_passed: int
    warnings_failed: int

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SanityChecksSummaryDetails":
        return cls(
            errors_passed=int(data.get("errors_passed", 0)),
            warnings_passed=int(data.get("warnings_passed", 0)),
            warnings_failed=int(data.get("warnings_failed", 0)),
        )


@dataclass
class SanityChecksSummary:
    total_passed: int
    total_failed: int
    total_checks: int
    details: SanityChecksSummaryDetails

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SanityChecksSummary":
        return cls(
            total_passed=int(data.get("total_passed", 0)),
            total_failed=int(data.get("total_failed", 0)),
            total_checks=int(data.get("total_checks", 0)),
            details=SanityChecksSummaryDetails.from_dict(
                data.get("details", {})),
        )


@dataclass
class SanityChecks:
    groups: Dict[str, Dict[str, SanityCheckEntry]] = field(default_factory=dict)
    summary: Optional[SanityChecksSummary] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SanityChecks":
        """Parse sanity checks from dict, organizing by group name.
        
        The structure supports arbitrary group names (calibration_10122025, 1064_FW5, etc.)
        Each group contains multiple check entries, with 'summary' being special.
        """
        summary_data = data.get("summary")
        summary = SanityChecksSummary.from_dict(
            summary_data) if summary_data else None

        groups: Dict[str, Dict[str, SanityCheckEntry]] = {}
        for group_name, group_checks in (data or {}).items():
            if group_name == "summary":
                continue
            if not isinstance(group_checks, dict):
                continue
            checks_dict = {
                check_name: SanityCheckEntry.from_dict(check_data)
                for check_name, check_data in group_checks.items()
                if isinstance(check_data, dict)
            }
            groups[group_name] = checks_dict

        return cls(groups=groups, summary=summary)


@dataclass
class Results:
    analysis: ResultsAnalysis
    sets: Dict[str, CalibSet] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Results":
        analysis = ResultsAnalysis.from_dict(data.get("analysis", {}))
        sets_raw = data.get("sets", {}) or {}
        sets = {key: CalibSet.from_dict(value)
                for key, value in sets_raw.items()}
        return cls(analysis=analysis, sets=sets)


@dataclass
class ReportData:
    meta: Meta
    results: Results
    plots: Plots
    sanity_checks: SanityChecks

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ReportData":
        return cls(
            meta=Meta.from_dict(data.get("meta", {})),
            results=Results.from_dict(data.get("results", {})),
            plots=Plots.from_dict(data.get("plots", {})),
            sanity_checks=SanityChecks.from_dict(data.get("sanity_checks", {})),
        )



if __name__ == "__main__":
    # Example usage
    import json
    import os
    json_example = os.path.join(os.path.dirname(__file__), "example", "calibration_summary.json")
    # Load a sample JSON report summary
    with open(json_example, "r") as f:
        data = json.load(f)

    report_data = ReportData.from_dict(data)

    # Access some fields
    print("Calibration ID:", report_data.meta.calib_id)
    print("Number of sets analyzed:", len(report_data.results.sets))