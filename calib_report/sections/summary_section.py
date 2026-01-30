
from ..helpers.data_holders import ReportData
from base_report.base_report import BaseReport
from ..report_elements.sanity_checks import add_sanity_check_box
from .base_section import BaseSection


class SummarySection(BaseSection):
    def __init__(self, report_data: ReportData, report: BaseReport) -> None:
        super().__init__(report_data, report)
        self.section_depth = 1  # Summary section is at depth 1

    def _build(self, depth):
        """Build the summary section of the report"""
        self.report.add_section('Calibration Summary', 'summary')
        # Further summary section building logic goes here
        self.add_failed_error_sanity_checks(depth)
        self.add_summary_table()
        
    def add_failed_error_sanity_checks(self, depth):
        """Add a subsection for failed sanity checks"""
        failed_checks = {'calibration': {} , 'fileset': {}, 'file': {}}
        errors = {'calibration': 0, 'fileset': 0, 'file': 0, 'total': 0}

        for name, check in self.report_data.sanity_checks.calibration_checks.items():
            if check.passed is False and check.severity == 'error':
                failed_checks['calibration'][name] = check
                errors['calibration'] +=1
                errors['total'] +=1
        if depth == 0 or depth >=2:
            for fs_name, fs_checks in self.report_data.sanity_checks.fileset_checks.items():
                for name, check in fs_checks.items():
                    if check.passed is False and check.severity == 'error':
                        failed_checks['fileset'].setdefault(fs_name, {})
                        failed_checks['fileset'][fs_name][name] = check
                        errors['fileset'] +=1
                        errors['total'] +=1
        if depth == 0 or depth >=3:
            for file_name, file_checks in self.report_data.sanity_checks.file_checks.items():
                for name, check in file_checks.items():
                    if check.passed is False and check.severity == 'error':
                        failed_checks['file'].setdefault(file_name, {})
                        failed_checks['file'][file_name][name] = check
                        errors['file'] +=1
                        errors['total'] +=1
        if errors['total'] == 0:
            return  # No failed error checks to report
        self.report.add_subsection('Failed Error Sanity Checks', 'failed_error_sanity_checks')
        if errors['calibration'] > 0:
            self.report.add_subsubsection(f"Calibration Level: {errors['calibration']} failed error checks.", "cal_failed_error_checks", include_in_toc=False)
            for name, check in failed_checks['calibration'].items():
                add_sanity_check_box(report = self.report, check=check, simplified=True)
        if errors['fileset'] > 0:
            for fs_name, fs_checks in failed_checks['fileset'].items():
                self.report.add_subsubsection(f"FileSet {fs_name} errors", f"fileset_{fs_name}_failed_error_checks", include_in_toc=False)
                for name, check in fs_checks.items():
                    add_sanity_check_box(report = self.report, check=check, simplified=True)
        if errors['file'] > 0:
            for file_name, file_checks in failed_checks['file'].items():
                self.report.add_subsubsection(f"File {file_name} errors", f"file_{file_name}_failed_error_checks", include_in_toc=False)
                for name, check in file_checks.items():
                    add_sanity_check_box(report = self.report, check=check, simplified=True)
        
    def add_summary_table(self):
        self.report.add_subsection('Calibration Summary Table', 'summary_table')
        units = 'W' if self.report_data.meta.calling_arguments.use_W_as_power_units else 'uW'
        sum_table = [["Wavelength", "Filter Wheel", f"slope ({units}/V)", f"intercept ({units})", "r value"]]
        for _, fs_data in self.report_data.analysis.filesets.items():
            sum_table.append([fs_data.meta.wave_length,
                              fs_data.meta.filter_wheel,
                              round(fs_data.analysis.lr_refpd_vs_pm.slope, 4),
                              round(fs_data.analysis.lr_refpd_vs_pm.intercept, 4),
                              round(fs_data.analysis.lr_refpd_vs_pm.r_value, 6)])
        self.report.add_table(sum_table, keep_together=True, 
                              description="Summary of calibration results for each file set.",
                              center=True, zebra=True)
        self.report.add_paragraph("The calibration analysis was executed with the following options:")
        exec_table = [
            ['Subtracted pedestals from values', 'No' if self.report_data.meta.calling_arguments.do_not_sub_pedestals else 'Yes'],
            ['Replace zero PM stds with resolution', 'No' if self.report_data.meta.calling_arguments.do_not_replace_zero_pm_stds else 'Yes'],
            ['Use first pedestal in linear regression', 'Yes' if self.report_data.meta.calling_arguments.use_first_ped_in_linreag else 'No'],
            ['Use W as power units', 'Yes' if self.report_data.meta.calling_arguments.use_W_as_power_units else 'No'],
        ]
        self.report.add_table(exec_table, keep_together=True, 
                              description="Summary of calibration execution options",
                              center=True, zebra=True, headers='col')