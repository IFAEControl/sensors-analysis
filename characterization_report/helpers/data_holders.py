from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional


@dataclass
class CallingArguments:
    char_files_path: Optional[str]
    calibration_json_path: Optional[str]
    plot_format: Optional[str]
    output_path: Optional[str]
    log_file: bool
    overwrite: bool
    zip: bool
    no_plots: bool
    no_gen_report: bool

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CallingArguments":
        return cls(
            char_files_path=data.get("char_files_path"),
            calibration_json_path=data.get("calibration_json_path"),
            plot_format=data.get("plot_format"),
            output_path=data.get("output_path"),
            log_file=bool(data.get("log_file", False)),
            overwrite=bool(data.get("overwrite", False)),
            zip=bool(data.get("zip", False)),
            no_plots=bool(data.get("no_plots", False)),
            no_gen_report=bool(data.get("no_gen_report", False)),
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
class Configuration:
    plot_output_format: Optional[str]
    generate_plots: bool
    saturation_derivative_threshold: Optional[float]
    summary_file_name: Optional[str]
    sensor_config: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Configuration":
        return cls(
            plot_output_format=data.get("plot_output_format"),
            generate_plots=bool(data.get("generate_plots", False)),
            saturation_derivative_threshold=data.get("saturation_derivative_threshold"),
            summary_file_name=data.get("summary_file_name"),
            sensor_config=data.get("sensor_config", {}) or {},
        )


@dataclass
class CalibrationLinReg:
    slope: Optional[float]
    intercept: Optional[float]
    stderr: Optional[float]
    intercept_stderr: Optional[float]
    r_value: Optional[float]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CalibrationLinReg":
        return cls(
            slope=data.get("slope"),
            intercept=data.get("intercept"),
            stderr=data.get("stderr"),
            intercept_stderr=data.get("intercept_stderr"),
            r_value=data.get("r_value"),
        )


@dataclass
class CalibrationReference:
    id: Optional[str]
    execution_date: Optional[str]
    power_unit: Optional[str]
    summary_path: Optional[str]
    used_configurations: list[str] = field(default_factory=list)
    available_configurations: list[str] = field(default_factory=list)
    linreg_by_configuration: Dict[str, CalibrationLinReg] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CalibrationReference":
        raw_linreg = data.get("linreg_by_configuration", {}) or {}
        return cls(
            id=data.get("id") or data.get("calibration_id"),
            execution_date=data.get("execution_date") or data.get("calibration_execution_date"),
            power_unit=data.get("power_unit"),
            summary_path=data.get("summary_path"),
            used_configurations=list(data.get("used_configurations", []) or []),
            available_configurations=list(data.get("available_configurations", []) or []),
            linreg_by_configuration={
                key: CalibrationLinReg.from_dict(value)
                for key, value in raw_linreg.items()
                if isinstance(value, dict)
            },
        )


@dataclass
class Meta:
    calling_arguments: CallingArguments
    charact_id: Optional[str]
    charact_files_path: Optional[str]
    root_output_path: Optional[str]
    characterization_folder_path: Optional[str]
    plots_path: Optional[str]
    reports_path: Optional[str]
    execution_date: Optional[str]
    system: SystemInfo
    config: Configuration
    calibration: Optional[CalibrationReference]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Meta":
        calibration = data.get("calibration")
        return cls(
            calling_arguments=CallingArguments.from_dict(data.get("calling_arguments", {})),
            charact_id=data.get("charact_id"),
            charact_files_path=data.get("charact_files_path"),
            root_output_path=data.get("root_output_path"),
            characterization_folder_path=data.get("characterization_folder_path"),
            plots_path=data.get("plots_path"),
            reports_path=data.get("reports_path"),
            execution_date=data.get("execution_date"),
            system=SystemInfo.from_dict(data.get("system", {})),
            config=Configuration.from_dict(data.get("config", {})),
            calibration=CalibrationReference.from_dict(calibration) if isinstance(calibration, dict) else None,
        )


@dataclass
class TimeInfo:
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
class MeanStats:
    mean: Optional[float]
    std: Optional[float]
    samples: Optional[int]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "MeanStats":
        return cls(
            mean=data.get("mean"),
            std=data.get("std"),
            samples=data.get("samples"),
        )


@dataclass
class LinearRegression:
    x_var: Optional[str]
    y_var: Optional[str]
    slope: Optional[float]
    intercept: Optional[float]
    r_value: Optional[float]
    p_value: Optional[float]
    stderr: Optional[float]
    intercept_stderr: Optional[float]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> Optional["LinearRegression"]:
        if not isinstance(data, Mapping):
            return None
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
class SaturationStats:
    threshold: Optional[float]
    num_saturated: Optional[int]
    total_points: Optional[int]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> Optional["SaturationStats"]:
        if not isinstance(data, Mapping):
            return None
        return cls(
            threshold=data.get("threshold"),
            num_saturated=data.get("num_saturated"),
            total_points=data.get("total_points"),
        )


@dataclass
class ConversionFactor:
    model: Optional[str]
    slope: Optional[float]
    intercept: Optional[float]
    slope_err: Optional[float]
    intercept_err: Optional[float]
    configuration: Optional[str]
    sensor_id: Optional[str]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> Optional["ConversionFactor"]:
        if not isinstance(data, Mapping):
            return None
        return cls(
            model=data.get("model"),
            slope=data.get("slope"),
            intercept=data.get("intercept"),
            slope_err=data.get("slope_err"),
            intercept_err=data.get("intercept_err"),
            configuration=data.get("configuration"),
            sensor_id=data.get("sensor_id"),
        )


@dataclass
class FileAnalysis:
    linreg_refpd_vs_adc: Optional[LinearRegression]
    pedestal_stats: Dict[str, MeanStats] = field(default_factory=dict)
    saturation_stats: Optional[SaturationStats] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "FileAnalysis":
        ped = data.get("pedestal_stats", {}) or {}
        return cls(
            linreg_refpd_vs_adc=LinearRegression.from_dict(data.get("linreg_refpd_vs_adc")),
            pedestal_stats={
                key: MeanStats.from_dict(value)
                for key, value in ped.items()
                if isinstance(value, dict)
            },
            saturation_stats=SaturationStats.from_dict(data.get("saturation_stats")),
        )


@dataclass
class DataPreparation:
    original_num_rows: Optional[int]
    original_num_pedestals: Optional[int]
    original_num_saturated: Optional[int]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "DataPreparation":
        return cls(
            original_num_rows=data.get("original_num_rows"),
            original_num_pedestals=data.get("original_num_pedestals"),
            original_num_saturated=data.get("original_num_saturated"),
        )


@dataclass
class FileInfo:
    filename: Optional[str]
    date: Optional[str]
    board: Optional[str]
    sensor_id: Optional[str]
    wavelength: Optional[str]
    filterwheel: Optional[str]
    run: Optional[str]
    num_points: Optional[int]
    file_size_bytes: Optional[int]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "FileInfo":
        return cls(
            filename=data.get("filename"),
            date=data.get("date"),
            board=data.get("board"),
            sensor_id=data.get("sensor_id"),
            wavelength=data.get("wavelength"),
            filterwheel=data.get("filterwheel"),
            run=data.get("run"),
            num_points=data.get("num_points"),
            file_size_bytes=data.get("file_size_bytes"),
        )


@dataclass
class SweepFile:
    file_info: FileInfo
    time_info: TimeInfo
    analysis: FileAnalysis
    data_preparation: Optional[DataPreparation]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SweepFile":
        dp = data.get("data_preparation")
        return cls(
            file_info=FileInfo.from_dict(data.get("file_info", {})),
            time_info=TimeInfo.from_dict(data.get("time_info", {})),
            analysis=FileAnalysis.from_dict(data.get("analysis", {})),
            data_preparation=DataPreparation.from_dict(dp) if isinstance(dp, dict) else None,
        )


@dataclass
class FilesetMeta:
    wavelength: Optional[str]
    filter_wheel: Optional[str]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "FilesetMeta":
        return cls(
            wavelength=data.get("wavelength"),
            filter_wheel=data.get("filter_wheel"),
        )


@dataclass
class FilesetAnalysis:
    linreg_refpd_vs_adc: Optional[LinearRegression]
    pedestal_stats: Dict[str, MeanStats] = field(default_factory=dict)
    saturation_stats: Optional[SaturationStats] = None
    adc_to_power: Optional[ConversionFactor] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "FilesetAnalysis":
        ped = data.get("pedestal_stats", {}) or {}
        return cls(
            linreg_refpd_vs_adc=LinearRegression.from_dict(data.get("linreg_refpd_vs_adc")),
            pedestal_stats={
                key: MeanStats.from_dict(value)
                for key, value in ped.items()
                if isinstance(value, dict)
            },
            saturation_stats=SaturationStats.from_dict(data.get("saturation_stats")),
            adc_to_power=ConversionFactor.from_dict(data.get("adc_to_power")),
        )


@dataclass
class Fileset:
    meta: FilesetMeta
    time_info: TimeInfo
    analysis: FilesetAnalysis
    files: Dict[str, SweepFile] = field(default_factory=dict)
    plots: "FilesetPlots" = field(default_factory=lambda: FilesetPlots())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Fileset":
        files_raw = data.get("files", {}) or {}
        return cls(
            meta=FilesetMeta.from_dict(data.get("meta", {})),
            time_info=TimeInfo.from_dict(data.get("time_info", {})),
            analysis=FilesetAnalysis.from_dict(data.get("analysis", {})),
            files={
                key: SweepFile.from_dict(value)
                for key, value in files_raw.items()
                if isinstance(value, dict)
            },
            plots=FilesetPlots.from_dict(data.get("plots", {})),
        )


@dataclass
class FilesetPlots:
    timeseries: Optional[str] = None
    fit_slopes_intercepts_vs_run_vert: Optional[str] = None
    fit_slopes_intercepts_vs_run_horiz: Optional[str] = None
    saturation_points_vs_run: Optional[str] = None
    refpd_vs_laser_setpoint: Optional[str] = None
    refpd_vs_dut: Optional[str] = None
    dut_vs_laser_setpoint: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> "FilesetPlots":
        if not isinstance(data, Mapping):
            return cls()
        return cls(
            timeseries=data.get("timeseries"),
            fit_slopes_intercepts_vs_run_vert=data.get("fit_slopes_intercepts_vs_run_vert"),
            fit_slopes_intercepts_vs_run_horiz=data.get("fit_slopes_intercepts_vs_run_horiz"),
            saturation_points_vs_run=data.get("saturation_points_vs_run"),
            refpd_vs_laser_setpoint=data.get("refpd_vs_laser_setpoint"),
            refpd_vs_dut=data.get("refpd_vs_dut"),
            dut_vs_laser_setpoint=data.get("dut_vs_laser_setpoint"),
        )


@dataclass
class PhotodiodePlots:
    timeseries: Optional[str] = None
    refpd_pedestals_timeseries: Optional[str] = None
    refpd_pedestals_timeseries_temp: Optional[str] = None
    refpd_pedestals_histogram: Optional[str] = None
    filesets: Dict[str, FilesetPlots] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> "PhotodiodePlots":
        if not isinstance(data, Mapping):
            return cls()
        fs_raw = data.get("filesets", {}) or {}
        return cls(
            timeseries=data.get("timeseries"),
            refpd_pedestals_timeseries=data.get("refpd_pedestals_timeseries"),
            refpd_pedestals_timeseries_temp=data.get("refpd_pedestals_timeseries_temp"),
            refpd_pedestals_histogram=data.get("refpd_pedestals_histogram"),
            filesets={
                key: FilesetPlots.from_dict(value)
                for key, value in fs_raw.items()
                if isinstance(value, Mapping)
            },
        )


@dataclass
class PhotodiodeMeta:
    sensor_id: Optional[str]
    gain: Optional[str]
    resistor: Optional[str]
    expected_runs: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PhotodiodeMeta":
        return cls(
            sensor_id=data.get("sensor_id"),
            gain=data.get("gain"),
            resistor=data.get("resistor"),
            expected_runs=list(data.get("expected_runs", []) or []),
        )


@dataclass
class PhotodiodeAnalysis:
    pedestal_stats: Dict[str, MeanStats] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PhotodiodeAnalysis":
        ped = data.get("pedestal_stats", {}) or {}
        return cls(
            pedestal_stats={
                key: MeanStats.from_dict(value)
                for key, value in ped.items()
                if isinstance(value, dict)
            }
        )


@dataclass
class Photodiode:
    meta: PhotodiodeMeta
    time_info: TimeInfo
    analysis: PhotodiodeAnalysis
    filesets: Dict[str, Fileset] = field(default_factory=dict)
    plots: PhotodiodePlots = field(default_factory=lambda: PhotodiodePlots())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Photodiode":
        fs_raw = data.get("filesets", {}) or {}
        return cls(
            meta=PhotodiodeMeta.from_dict(data.get("meta", {})),
            time_info=TimeInfo.from_dict(data.get("time_info", {})),
            analysis=PhotodiodeAnalysis.from_dict(data.get("analysis", {})),
            filesets={
                key: Fileset.from_dict(value)
                for key, value in fs_raw.items()
                if isinstance(value, dict)
            },
            plots=PhotodiodePlots.from_dict(data.get("plots", {})),
        )


@dataclass
class Analysis:
    photodiodes: Dict[str, Photodiode] = field(default_factory=dict)
    pedestal_stats: Dict[str, MeanStats] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Analysis":
        pds_raw = data.get("photodiodes", {}) or {}
        ped_stats_raw = data.get("pedestal_stats", {}) or {}
        ped_stats = {
            key: MeanStats.from_dict(value)
            for key, value in ped_stats_raw.items()
            if isinstance(value, dict)
        }
        return cls(
            photodiodes={
                key: Photodiode.from_dict(value)
                for key, value in pds_raw.items()
                if isinstance(value, dict)
            },
            pedestal_stats=ped_stats,
        )


@dataclass
class Plots:
    photodiodes: Dict[str, PhotodiodePlots] = field(default_factory=dict)
    saturation_points_by_filter: Optional[str] = None
    refpd_vs_adc_linregs_1064: Optional[str] = None
    refpd_vs_adc_linregs_532: Optional[str] = None
    refpd_vs_adc_linregs_1064_simp: Optional[str] = None
    refpd_vs_adc_linregs_532_simp: Optional[str] = None
    power_vs_adc_linregs_1064_simp: Optional[str] = None
    power_vs_adc_linregs_532_simp: Optional[str] = None
    refpd_pedestals_timeseries: Optional[str] = None
    refpd_pedestals_timeseries_temp: Optional[str] = None
    refpd_pedestals_histogram: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Plots":
        pd_raw = data.get("photodiodes", {}) or {}
        return cls(
            photodiodes={
                key: PhotodiodePlots.from_dict(value)
                for key, value in pd_raw.items()
                if isinstance(value, Mapping)
            },
            saturation_points_by_filter=data.get("saturation_points_by_filter"),
            refpd_vs_adc_linregs_1064=data.get("refpd_vs_adc_linregs_1064"),
            refpd_vs_adc_linregs_532=data.get("refpd_vs_adc_linregs_532"),
            refpd_vs_adc_linregs_1064_simp=data.get("refpd_vs_adc_linregs_1064_simp"),
            refpd_vs_adc_linregs_532_simp=data.get("refpd_vs_adc_linregs_532_simp"),
            power_vs_adc_linregs_1064_simp=data.get("power_vs_adc_linregs_1064_simp"),
            power_vs_adc_linregs_532_simp=data.get("power_vs_adc_linregs_532_simp"),
            refpd_pedestals_timeseries=data.get("refpd_pedestals_timeseries"),
            refpd_pedestals_timeseries_temp=data.get("refpd_pedestals_timeseries_temp"),
            refpd_pedestals_histogram=data.get("refpd_pedestals_histogram"),
        )


@dataclass
class SanityCheckEntry:
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
    error_passed: int
    warning_passed: int
    error_failed: int
    warning_failed: int

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SanityChecksSummaryDetails":
        return cls(
            error_passed=int(data.get("error_passed", 0)),
            warning_passed=int(data.get("warning_passed", 0)),
            error_failed=int(data.get("error_failed", 0)),
            warning_failed=int(data.get("warning_failed", 0)),
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
            details=SanityChecksSummaryDetails.from_dict(data.get("details", {})),
        )


@dataclass
class SanityCheckDefinition:
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
    characterization_checks: Dict[str, SanityCheckDefinition] = field(default_factory=dict)
    fileset_checks: Dict[str, SanityCheckDefinition] = field(default_factory=dict)
    sweepfile_checks: Dict[str, SanityCheckDefinition] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SanityChecksDefined":
        sweepfile_raw = data.get("sweepfile_checks", data.get("file_checks", {})) or {}
        return cls(
            characterization_checks={
                check_name: SanityCheckDefinition.from_dict(check_data)
                for check_name, check_data in (data.get("characterization_checks", data.get("calibration_checks", {})) or {}).items()
                if isinstance(check_data, dict)
            },
            fileset_checks={
                check_name: SanityCheckDefinition.from_dict(check_data)
                for check_name, check_data in (data.get("fileset_checks", {}) or {}).items()
                if isinstance(check_data, dict)
            },
            sweepfile_checks={
                check_name: SanityCheckDefinition.from_dict(check_data)
                for check_name, check_data in sweepfile_raw.items()
                if isinstance(check_data, dict)
            },
        )


@dataclass
class FilesetSanity:
    checks: Dict[str, SanityCheckEntry] = field(default_factory=dict)
    sweepfiles: Dict[str, Dict[str, SanityCheckEntry]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "FilesetSanity":
        checks_raw = data.get("checks", {}) or {}
        files_raw = data.get("sweepfiles", data.get("files", {})) or {}
        sweepfiles: Dict[str, Dict[str, SanityCheckEntry]] = {}
        for file_name, checks in files_raw.items():
            if not isinstance(checks, dict):
                continue
            sweepfiles[file_name] = {
                ck: SanityCheckEntry.from_dict(cv)
                for ck, cv in checks.items()
                if isinstance(cv, dict)
            }
        return cls(
            checks={
                ck: SanityCheckEntry.from_dict(cv)
                for ck, cv in checks_raw.items()
                if isinstance(cv, dict)
            },
            sweepfiles=sweepfiles,
        )


@dataclass
class PhotodiodeSanity:
    checks: Dict[str, SanityCheckEntry] = field(default_factory=dict)
    filesets: Dict[str, FilesetSanity] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PhotodiodeSanity":
        filesets_raw = data.get("filesets", {}) or {}
        return cls(
            checks={
                ck: SanityCheckEntry.from_dict(cv)
                for ck, cv in (data.get("checks", {}) or {}).items()
                if isinstance(cv, dict)
            },
            filesets={
                fs: FilesetSanity.from_dict(fv)
                for fs, fv in filesets_raw.items()
                if isinstance(fv, dict)
            },
        )


@dataclass
class SanityRun:
    checks: Dict[str, SanityCheckEntry] = field(default_factory=dict)
    photodiodes: Dict[str, PhotodiodeSanity] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SanityRun":
        photodiodes_raw = data.get("photodiodes", {}) or {}
        legacy_filesets_raw = data.get("filesets", {}) or {}
        photodiodes: Dict[str, PhotodiodeSanity] = {
            sensor_id: PhotodiodeSanity.from_dict(pd_data)
            for sensor_id, pd_data in photodiodes_raw.items()
            if isinstance(pd_data, dict)
        }

        # Backward compatibility with older schema:
        # sanity_checks.<run>.filesets.<fileset>
        if legacy_filesets_raw and not photodiodes:
            photodiodes["unknown"] = PhotodiodeSanity(
                checks={},
                filesets={
                    fs: FilesetSanity.from_dict(fv)
                    for fs, fv in legacy_filesets_raw.items()
                    if isinstance(fv, dict)
                },
            )

        return cls(
            checks={
                ck: SanityCheckEntry.from_dict(cv)
                for ck, cv in (data.get("checks", {}) or {}).items()
                if isinstance(cv, dict)
            },
            photodiodes=photodiodes,
        )


@dataclass
class SanityChecks:
    runs: Dict[str, SanityRun] = field(default_factory=dict)
    summary: Optional[SanityChecksSummary] = None
    defined_checks: Optional[SanityChecksDefined] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SanityChecks":
        summary_data = data.get("summary")
        defined_checks_data = data.get("defined_checks")
        runs: Dict[str, SanityRun] = {}
        for key, value in (data or {}).items():
            if key in {"summary", "defined_checks"} or not isinstance(value, dict):
                continue
            runs[key] = SanityRun.from_dict(value)
        return cls(
            runs=runs,
            summary=SanityChecksSummary.from_dict(summary_data) if isinstance(summary_data, dict) else None,
            defined_checks=SanityChecksDefined.from_dict(defined_checks_data) if isinstance(defined_checks_data, dict) else None,
        )


@dataclass
class ReportData:
    meta: Meta
    analysis: Analysis
    time_info: TimeInfo
    plots: Plots = field(default_factory=Plots)
    calibration: Optional[CalibrationReference] = None
    conversion_factors: Dict[str, Dict[str, ConversionFactor]] = field(default_factory=dict)
    sanity_checks: SanityChecks = field(default_factory=SanityChecks)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ReportData":
        conv_raw = data.get("conversion_factors", {}) or {}
        conversion_factors: Dict[str, Dict[str, ConversionFactor]] = {}
        for sensor_id, configs in conv_raw.items():
            if not isinstance(configs, dict):
                continue
            conversion_factors[sensor_id] = {
                cfg: ConversionFactor.from_dict(cv)
                for cfg, cv in configs.items()
                if isinstance(cv, dict)
            }

        calibration = data.get("calibration")

        return cls(
            meta=Meta.from_dict(data.get("meta", {})),
            analysis=Analysis.from_dict(data.get("analysis", {})),
            time_info=TimeInfo.from_dict(data.get("time_info", {})),
            plots=Plots.from_dict(data.get("plots", {})),
            calibration=CalibrationReference.from_dict(calibration) if isinstance(calibration, dict) else None,
            conversion_factors=conversion_factors,
            sanity_checks=SanityChecks.from_dict(data.get("sanity_checks", {})),
        )
