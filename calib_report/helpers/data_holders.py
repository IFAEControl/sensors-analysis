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
    do_not_sub_pedestals: bool
    do_not_replace_zero_pm_stds: bool
    use_first_ped_in_linreag: bool
    use_W_as_power_units: bool

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CallingArguments":
        return cls(
            calib_files_path=data.get("calib_files_path"),
            plot_format=data.get("plot_format"),
            output_path=data.get("output_path"),
            log_file=bool(data.get("log_file", False)),
            overwrite=bool(data.get("overwrite", False)),
            no_plots=bool(data.get("no_plots", False)),
            do_not_sub_pedestals=bool(data.get("do_not_sub_pedestals", False)),
            do_not_replace_zero_pm_stds=bool(
                data.get("do_not_replace_zero_pm_stds", False)
            ),
            use_first_ped_in_linreag=bool(
                data.get("use_first_ped_in_linreag", False)
            ),
            use_W_as_power_units=bool(data.get("use_W_as_power_units", False)),
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
class MetaConfig:
    plot_output_format: Optional[str]
    generate_plots: bool
    subtract_pedestals: bool
    replace_zero_pm_stds: bool
    power_meter_resolutions: Dict[str, float] = field(default_factory=dict)
    use_first_pedestal_in_linreg: bool = False
    use_uW_as_power_units: bool = False

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "MetaConfig":
        return cls(
            plot_output_format=data.get("plot_output_format"),
            generate_plots=bool(data.get("generate_plots", False)),
            subtract_pedestals=bool(data.get("subtract_pedestals", False)),
            replace_zero_pm_stds=bool(data.get("replace_zero_pm_stds", False)),
            power_meter_resolutions=data.get(
                "power_meter_resolutions", {}) or {},
            use_first_pedestal_in_linreg=bool(
                data.get("use_first_pedestal_in_linreg", False)
            ),
            use_uW_as_power_units=bool(
                data.get("use_uW_as_power_units", False)),
        )


@dataclass
class Meta:
    calling_arguments: CallingArguments
    calib_id: Optional[str]
    calib_files_path: Optional[str]
    root_output_path: Optional[str]
    calibration_plots_path: Optional[str]
    reports_path: Optional[str]
    execution_date: Optional[str]
    system: SystemInfo
    config: MetaConfig

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Meta":
        return cls(
            calling_arguments=CallingArguments.from_dict(
                data.get("calling_arguments", {})),
            calib_id=data.get("calib_id"),
            calib_files_path=data.get("calib_files_path"),
            root_output_path=data.get("root_output_path"),
            calibration_plots_path=data.get("calibration_plots_path"),
            reports_path=data.get("reports_path"),
            execution_date=data.get("execution_date"),
            system=SystemInfo.from_dict(data.get("system", {})),
            config=MetaConfig.from_dict(data.get("config", {})),
        )


@dataclass
class TimeInfo:
    """Represents time-related metadata."""
    min_ts: Optional[int]
    max_ts: Optional[int]
    elapsed_time_s: Optional[int]
    min_dt: Optional[str]
    max_dt: Optional[str]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "TimeInfo":
        return cls(
            min_ts=data.get("min_ts"),
            max_ts=data.get("max_ts"),
            elapsed_time_s=data.get("elapsed_time_s"),
            min_dt=data.get("min_dt"),
            max_dt=data.get("max_dt"),
        )


@dataclass
class LinearRegression:
    """Represents a single linear regression analysis."""
    x_var: Optional[str]
    y_var: Optional[str]
    slope: Optional[float]
    intercept: Optional[float]
    r_value: Optional[float]
    p_value: Optional[float]
    stderr: Optional[float]
    intercept_stderr: Optional[float]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "LinearRegression":
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
    """Statistics for pedestal measurements."""
    mean: Optional[float]
    std: Optional[float]
    samples: Optional[int]
    weighted: bool
    w_mean: Optional[float]
    w_stderr: Optional[float]
    ndof: Optional[int]
    chi2: Optional[float]
    chi2_reduced: Optional[float]
    exec_error: bool

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PedestalStats":
        return cls(
            mean=data.get("mean"),
            std=data.get("std"),
            samples=data.get("samples"),
            weighted=bool(data.get("weighted", False)),
            w_mean=data.get("w_mean"),
            w_stderr=data.get("w_stderr"),
            ndof=data.get("ndof"),
            chi2=data.get("chi2"),
            chi2_reduced=data.get("chi2_reduced"),
            exec_error=bool(data.get("exec_error", False)),
        )


@dataclass
class FileInfo:
    """Metadata extracted from calibration filename."""
    filename: Optional[str]
    day: Optional[str]
    month: Optional[str]
    year: Optional[str]
    wavelength: Optional[str]
    power: Optional[str]
    filterwheel: Optional[str]
    run: Optional[str]
    num_points: Optional[int]
    file_size_bytes: Optional[int]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "FileInfo":
        return cls(
            filename=data.get("filename"),
            day=data.get("day"),
            month=data.get("month"),
            year=data.get("year"),
            wavelength=data.get("wavelength"),
            power=data.get("power"),
            filterwheel=data.get("filterwheel"),
            run=data.get("run"),
            num_points=data.get("num_points"),
            file_size_bytes=data.get("file_size_bytes")
        )


@dataclass
class FileAnalysis:
    """Analysis results for a single calibration file."""
    used_columns: Optional[Dict[str, str]] = None
    linregs: Dict[str, LinearRegression] = field(default_factory=dict)
    pedestal_stats: Dict[str, PedestalStats] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "FileAnalysis":
        linregs_raw = data.get("linregs", {}) or {}
        used_columns = None
        used_columns_raw = linregs_raw.pop("used_columns", None)
        if isinstance(used_columns_raw, dict):
            used_columns = {
                key: str(value)
                for key, value in used_columns_raw.items()
            }
        linregs = {
            key: LinearRegression.from_dict(value)
            for key, value in linregs_raw.items()
        }
        pedestal_stats_raw = data.get("pedestal_stats", {}) or {}
        pedestal_stats = {
            key: PedestalStats.from_dict(value)
            for key, value in pedestal_stats_raw.items()
        }
        return cls(
            used_columns=used_columns,
            linregs=linregs,
            pedestal_stats=pedestal_stats,
        )


@dataclass
class PedestalSubtraction:
    pm_pedestal: Optional[float]
    refpd_pedestal: Optional[float]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PedestalSubtraction":
        return cls(
            pm_pedestal=data.get("pm_pedestal"),
            refpd_pedestal=data.get("refpd_pedestal"),
        )


@dataclass
class DataPreparation:
    original_num_rows: Optional[int]
    use_uW_as_power_units: bool
    original_pm_std_zero_count: Optional[int]
    replace_zero_pm_std: bool
    num_pm_std_replaced: Optional[int]
    pm_std_replacement_value: Optional[float]
    original_num_pedestals: Optional[int]
    pedestal_subtraction: Optional[PedestalSubtraction] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "DataPreparation":
        return cls(
            original_num_rows=data.get("original_num_rows"),
            use_uW_as_power_units=bool(data.get("use_uW_as_power_units", False)),
            original_pm_std_zero_count=data.get("original_pm_std_zero_count"),
            replace_zero_pm_std=bool(data.get("replace_zero_pm_std", False)),
            num_pm_std_replaced=data.get("num_pm_std_replaced"),
            pm_std_replacement_value=data.get("pm_std_replacement_value"),
            original_num_pedestals=data.get("original_num_pedestals"),
            pedestal_subtraction=PedestalSubtraction.from_dict(
                data.get("pedestal_subtraction", {})
            ) if data.get("pedestal_subtraction") else None,
        )


@dataclass
class CalibFile:
    """Complete representation of a single calibration file."""
    file_info: FileInfo
    time_info: TimeInfo
    analysis: FileAnalysis
    data_preparation: Optional[DataPreparation] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CalibFile":
        return cls(
            file_info=FileInfo.from_dict(data.get("file_info", {})),
            time_info=TimeInfo.from_dict(data.get("time_info", {})),
            analysis=FileAnalysis.from_dict(data.get("analysis", {})),
            data_preparation=DataPreparation.from_dict(
                data.get("data_preparation", {})
            ) if data.get("data_preparation") else None,
        )


@dataclass
class FilesetMeta:
    """Metadata for a fileset."""
    wave_length: Optional[str]
    filter_wheel: Optional[str]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "FilesetMeta":
        return cls(
            wave_length=data.get("wave_length"),
            filter_wheel=data.get("filter_wheel"),
        )


@dataclass
class FilesetAnalysis:
    """Aggregated analysis results for a fileset."""
    lr_refpd_vs_pm: LinearRegression
    pedestals: Dict[str, PedestalStats] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "FilesetAnalysis":
        pedestals_raw = data.get("pedestals", {}) or {}
        pedestals = {
            key: PedestalStats.from_dict(value)
            for key, value in pedestals_raw.items()
        }
        return cls(
            lr_refpd_vs_pm=LinearRegression.from_dict(
                data.get("lr_refpd_vs_pm", {})
            ),
            pedestals=pedestals,
        )


@dataclass
class Fileset:
    """Complete representation of a fileset (e.g., 1064_FW5)."""
    meta: FilesetMeta
    analysis: FilesetAnalysis
    time_info: TimeInfo
    files: Dict[str, CalibFile] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Fileset":
        files_raw = data.get("files", {}) or {}
        files = {
            key: CalibFile.from_dict(value)
            for key, value in files_raw.items()
        }
        return cls(
            meta=FilesetMeta.from_dict(data.get("meta", {})),
            analysis=FilesetAnalysis.from_dict(data.get("analysis", {})),
            time_info=TimeInfo.from_dict(data.get("time_info", {})),
            files=files,
        )


@dataclass
class Analysis:
    """Top-level analysis containing all filesets."""
    time_info: TimeInfo
    filesets: Dict[str, Fileset] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Analysis":
        filesets_raw = data.get("filesets", {}) or {}
        filesets = {
            key: Fileset.from_dict(value)
            for key, value in filesets_raw.items()
        }
        return cls(
            time_info=TimeInfo.from_dict(data.get("time_info", {})),
            filesets=filesets,
        )


@dataclass
class FilePlots:
    """Plot file references for a single calibration file."""
    temperature_hist: Optional[str] = None
    humidity_hist: Optional[str] = None
    timeseries: Optional[str] = None
    pm_samples_full: Optional[str] = None
    pm_samples_pedestals: Optional[str] = None
    pm_vs_L: Optional[str] = None
    refPD_vs_L: Optional[str] = None
    pm_vs_refPD: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "FilePlots":
        return cls(
            temperature_hist=data.get("temperature_hist"),
            humidity_hist=data.get("humidity_hist"),
            timeseries=data.get("timeseries"),
            pm_samples_full=data.get("pm_samples_full"),
            pm_samples_pedestals=data.get("pm_samples_pedestals"),
            pm_vs_L=data.get("pm_vs_L"),
            refPD_vs_L=data.get("refPD_vs_L"),
            pm_vs_refPD=data.get("pm_vs_refPD"),
        )


@dataclass
class FileSetPlots:
    """Plot file references for a fileset, including its files."""
    files: Dict[str, FilePlots] = field(default_factory=dict)
    temperature_hist: Optional[str] = None
    humidity_hist: Optional[str] = None
    timeseries: Optional[str] = None
    pm_samples_full: Optional[str] = None
    pm_samples_pedestals: Optional[str] = None
    calibrations_evolution: Optional[str] = None
    ConvFactorSlopes_Comparison: Optional[str] = None
    ConvFactorIntercepts_Comparison: Optional[str] = None
    pmVsRefPD_fitSlope_vs_Temperature: Optional[str] = None
    pmVsRefPD_fitSlopes_and_Intercepts_vs_Run: Optional[str] = None
    pmVsRefPD_fitSlopes_and_Intercepts_vs_Run_vert: Optional[str] = None
    pm_vs_RefPD: Optional[str] = None
    pm_vs_RefPD_runs: Optional[str] = None
    pm_vs_LaserSetting: Optional[str] = None
    RefPD_vs_LaserSetting: Optional[str] = None
    Pedestals_Histogram: Optional[str] = None
    Pedestals_vs_runindex: Optional[str] = None
    pedestals_timeseries: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "FileSetPlots":
        files_raw = data.get("files", {}) or {}
        files = {
            key: FilePlots.from_dict(value)
            for key, value in files_raw.items()
        }
        return cls(
            files=files,
            temperature_hist=data.get("temperature_hist"),
            humidity_hist=data.get("humidity_hist"),
            timeseries=data.get("timeseries"),
            pm_samples_full=data.get("pm_samples_full"),
            pm_samples_pedestals=data.get("pm_samples_pedestals"),
            calibrations_evolution=data.get("calibrations_evolution"),
            ConvFactorSlopes_Comparison=data.get(
                "ConvFactorSlopes_Comparison"),
            ConvFactorIntercepts_Comparison=data.get(
                "ConvFactorIntercepts_Comparison"),
            pmVsRefPD_fitSlope_vs_Temperature=data.get(
                "pmVsRefPD_fitSlope_vs_Temperature"),
            pmVsRefPD_fitSlopes_and_Intercepts_vs_Run=data.get(
                "pmVsRefPD_fitSlopes_and_Intercepts_vs_Run"
            ),
            pmVsRefPD_fitSlopes_and_Intercepts_vs_Run_vert=data.get(
                "pmVsRefPD_fitSlopes_and_Intercepts_vs_Run_vert"
            ),
            pm_vs_RefPD=data.get("pm_vs_RefPD"),
            pm_vs_RefPD_runs=data.get("pm_vs_RefPD_runs"),
            pm_vs_LaserSetting=data.get("pm_vs_LaserSetting"),
            RefPD_vs_LaserSetting=data.get("RefPD_vs_LaserSetting"),
            Pedestals_Histogram=data.get("Pedestals_Histogram"),
            Pedestals_vs_runindex=data.get("Pedestals_vs_runindex"),
            pedestals_timeseries=data.get("pedestals_timeseries"),
        )


@dataclass
class Plots:
    """Plot file references at calibration level."""
    filesets: Dict[str, FileSetPlots] = field(default_factory=dict)
    timeseries: Optional[str] = None
    temperature_hist: Optional[str] = None
    humidity_hist: Optional[str] = None
    pm_samples_full: Optional[str] = None
    pm_samples_pedestals: Optional[str] = None
    pedestals_timeseries: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Plots":
        filesets_raw = data.get("filesets", {}) or {}
        filesets = {
            key: FileSetPlots.from_dict(value)
            for key, value in filesets_raw.items()
        }
        return cls(
            filesets=filesets,
            timeseries=data.get("timeseries"),
            temperature_hist=data.get("temperature_hist"),
            humidity_hist=data.get("humidity_hist"),
            pm_samples_full=data.get("pm_samples_full"),
            pm_samples_pedestals=data.get("pm_samples_pedestals"),
            pedestals_timeseries=data.get("pedestals_timeseries"),
        )


@dataclass
class SanityCheckEntry:
    """A single sanity check result."""
    check_name: Optional[str]
    check_args: Optional[Any]
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
    """Breakdown of check results by severity."""
    error_passed: int
    warning_passed: int
    warning_failed: int

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SanityChecksSummaryDetails":
        return cls(
            error_passed=int(data.get("error_passed", data.get("errors_passed", 0))),
            warning_passed=int(data.get("warning_passed", data.get("warnings_passed", 0))),
            warning_failed=int(data.get("warning_failed", data.get("warnings_failed", 0))),
        )

    # Backward-compatible aliases
    @property
    def errors_passed(self) -> int:
        return self.error_passed

    @property
    def warnings_passed(self) -> int:
        return self.warning_passed

    @property
    def warnings_failed(self) -> int:
        return self.warning_failed


@dataclass
class SanityChecksSummary:
    """Summary statistics for all sanity checks."""
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
class SanityCheckDefinition:
    """A sanity check definition entry from sanity_checks.defined_checks."""
    check_name: Optional[str]
    check_args: Optional[Any]
    severity: Optional[str]
    check_explanation: Optional[str]
    exec_error: bool = False

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SanityCheckDefinition":
        return cls(
            check_name=data.get("check_name"),
            check_args=data.get("check_args"),
            severity=data.get("severity"),
            check_explanation=data.get("check_explanation"),
            exec_error=bool(data.get("exec_error", False)),
        )


@dataclass
class SanityChecksDefined:
    """Configured sanity checks metadata grouped by level."""
    calibration_checks: Dict[str, SanityCheckDefinition] = field(default_factory=dict)
    fileset_checks: Dict[str, SanityCheckDefinition] = field(default_factory=dict)
    file_checks: Dict[str, SanityCheckDefinition] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SanityChecksDefined":
        return cls(
            calibration_checks={
                check_name: SanityCheckDefinition.from_dict(check_data)
                for check_name, check_data in (data.get("calibration_checks", {}) or {}).items()
                if isinstance(check_data, dict)
            },
            fileset_checks={
                check_name: SanityCheckDefinition.from_dict(check_data)
                for check_name, check_data in (data.get("fileset_checks", {}) or {}).items()
                if isinstance(check_data, dict)
            },
            file_checks={
                check_name: SanityCheckDefinition.from_dict(check_data)
                for check_name, check_data in (data.get("file_checks", {}) or {}).items()
                if isinstance(check_data, dict)
            },
        )


@dataclass
class SanityChecks:
    """All sanity check results organized by calibration, fileset, and file."""
    calibration_checks: Dict[str, SanityCheckEntry] = field(
        default_factory=dict)
    fileset_checks: Dict[str, Dict[str, SanityCheckEntry]
                         ] = field(default_factory=dict)
    file_checks: Dict[str, Dict[str, SanityCheckEntry]
                         ] = field(default_factory=dict)
    summary: Optional[SanityChecksSummary] = None
    defined_checks: Optional[SanityChecksDefined] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SanityChecks":
        """Parse sanity checks from dict, supporting nested calibration/fileset/file."""
        summary_data = data.get("summary")
        summary = SanityChecksSummary.from_dict(
            summary_data) if summary_data else None
        defined_checks_data = data.get("defined_checks")
        defined_checks = SanityChecksDefined.from_dict(
            defined_checks_data) if isinstance(defined_checks_data, dict) else None

        calibration_checks: Dict[str, SanityCheckEntry] = {}
        fileset_checks: Dict[str, Dict[str, SanityCheckEntry]] = {}
        file_checks: Dict[str, Dict[str, SanityCheckEntry]] = {}

        for group_name, group_data in (data or {}).items():
            if group_name in {"summary", "defined_checks"} or not isinstance(group_data, dict):
                continue

            checks_block = group_data.get("checks")
            if isinstance(checks_block, dict):
                calibration_checks = {
                    check_name: SanityCheckEntry.from_dict(check_data)
                    for check_name, check_data in checks_block.items()
                    if isinstance(check_data, dict)
                }

            filesets_block = group_data.get("filesets")
            if isinstance(filesets_block, dict):
                for fs_name, fs_data in filesets_block.items():
                    if not isinstance(fs_data, dict):
                        continue
                    fs_checks = fs_data.get("checks")
                    if isinstance(fs_checks, dict):
                        fileset_checks[fs_name] = {
                            check_name: SanityCheckEntry.from_dict(check_data)
                            for check_name, check_data in fs_checks.items()
                            if isinstance(check_data, dict)
                        }
                    fs_files = fs_data.get("files")
                    if isinstance(fs_files, dict):
                        # file_checks.setdefault(fs_name, {})
                        for file_name, file_checks_block in fs_files.items():
                            if not isinstance(file_checks_block, dict):
                                continue
                            file_checks[file_name] = {
                                check_name: SanityCheckEntry.from_dict(check_data)
                                for check_name, check_data in file_checks_block.items()
                                if isinstance(check_data, dict)
                            }

        return cls(
            calibration_checks=calibration_checks,
            fileset_checks=fileset_checks,
            file_checks=file_checks,
            summary=summary,
            defined_checks=defined_checks,
        )


@dataclass
class ReportData:
    """Complete calibration report data structure."""
    meta: Meta
    analysis: Analysis
    time_info: TimeInfo
    plots: Plots = field(default_factory=Plots)
    sanity_checks: SanityChecks = field(default_factory=SanityChecks)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ReportData":
        return cls(
            meta=Meta.from_dict(data.get("meta", {})),
            analysis=Analysis.from_dict(data.get("analysis", {})),
            time_info=TimeInfo.from_dict(data.get("time_info", {})),
            plots=Plots.from_dict(data.get("plots", {})),
            sanity_checks=SanityChecks.from_dict(
                data.get("sanity_checks", {})),
        )


if __name__ == "__main__":
    # Example usage
    import json
    import os

    json_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..",
        "output",
        "calibration_10122025",
        "calibration_10122025-summary.json"
    )

    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            data = json.load(f)

        report_data = ReportData.from_dict(data)

        # Access some fields
        print("Calibration ID:", report_data.meta.calib_id)
        print("Number of filesets:", len(report_data.analysis.filesets))
        print("Time span: {0} to {1}".format(
            report_data.analysis.time_info.min_dt,
            report_data.analysis.time_info.max_dt
        ))
        print("Sanity checks passed:",
              report_data.sanity_checks.summary.total_passed if report_data.sanity_checks.summary else "N/A")
