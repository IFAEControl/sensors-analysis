
from reportlab.lib import colors
from base_report.base_report_slides import BaseReportSlides, Frame

from ..helpers.data_holders import ReportData
from ..report_elements.sanity_checks import add_sanity_check_box
from .base_section import BaseSection


class SummarySection(BaseSection):
    def __init__(self, report_data: ReportData, report: BaseReportSlides) -> None:
        super().__init__(report_data, report)
        self.section_depth = 1  # Summary section is at depth 1

        self.checks_failed = {'calibration': {} , 'fileset': {}, 'file': {}}
        self.check_errors = {'calibration': 0, 'fileset': 0, 'file': 0, 'total': 0}


    def _build(self, depth):
        """Build the summary section of the report"""
        self.report.add_slide()
        frame = self.report.get_active_area()
        self.report.add_section('Calibration Summary',
                                x=frame.x, y=frame.y,
                                width=frame.width,
                                anchor='calib_summary', toc=True)
        self.find_failed_error_sanity_checks(depth)
        self.add_summary_table()
        
        # Further summary section building logic goes here
        if self.check_errors['total'] > 0:
            self.add_errors_warning()
            self.add_failed_error_sanity_checks(depth)
    
    def add_errors_warning(self):
        """Add a warning about errors in sanity checks"""
        # frame: 
        init_y = self.lf.y - self.lf.height - 60
        frame_width = self.end_x - self.init_x - 200
        frame_x = (960 - frame_width)/2
        self.report.add_badge(
            title="Warning: Failed Error Sanity Checks",
            description=f"There are {self.check_errors['total']} failed error sanity checks in the  analysis. Please review the <a href='failed_error_sanity_checks'><b>Failed Error Sanity Checks</b></a> section for details.",
            level="Error",
            x=frame_x,
            y=init_y,
            width=frame_width,
        )

    def find_failed_error_sanity_checks(self, depth):
        """Find failed sanity checks"""
        self.checks_failed = {'calibration': {} , 'fileset': {}, 'file': {}}
        self.check_errors = {'calibration': 0, 'fileset': 0, 'file': 0, 'total': 0}

        for name, check in self.report_data.sanity_checks.calibration_checks.items():
            if check.passed is False and check.severity == 'error':
                self.checks_failed['calibration'][name] = check
                self.check_errors['calibration'] +=1
                self.check_errors['total'] +=1
        if depth == 0 or depth >=2:
            for fs_name, fs_checks in self.report_data.sanity_checks.fileset_checks.items():
                for name, check in fs_checks.items():
                    if check.passed is False and check.severity == 'error':
                        self.checks_failed['fileset'].setdefault(fs_name, {})
                        self.checks_failed['fileset'][fs_name][name] = check
                        self.check_errors['fileset'] +=1
                        self.check_errors['total'] +=1
        if depth == 0 or depth >=3:
            for file_name, file_checks in self.report_data.sanity_checks.file_checks.items():
                for name, check in file_checks.items():
                    if check.passed is False and check.severity == 'error':
                        self.checks_failed['file'].setdefault(file_name, {})
                        self.checks_failed['file'][file_name][name] = check
                        self.check_errors['file'] +=1
                        self.check_errors['total'] +=1
    
    def add_failed_error_sanity_checks(self, depth=0):
        """Add a subsection for failed sanity checks"""
        self.report.add_slide("Failed Error Sanity Checks", subtitle="Only error level failed checks")
        f = self.report.get_active_area()
        self.report.add_subsection(
            'Failed Error Sanity Checks', 
            x = self.init_x,
            y = f.y,
            width = f.width,
            anchor='failed_error_sanity_checks',
            toc=False)
        
        self.report.add_badge(
            title="Pending to implement this view",
            description="This section is intended to show the failed sanity checks that have an error severity level in the analysis. The implementation of this section is pending and will be added in a future update of the report.\n \n You can check the json file to look which errors sanity checks have failed in the analysis.",
            level="Warning",
            x=self.init_x,
            y=self.lf.y - self.lf.height - 60,
            width=500,
        )
        # if self.check_errors['calibration'] > 0:
        #     self.report.add_subsubsection(f"Calibration Level: {self.check_errors['calibration']} failed error checks.", "cal_failed_error_checks", include_in_toc=False)
        #     for name, check in self.checks_failed['calibration'].items():
        #         add_sanity_check_box(report = self.report, check=check, simplified=True)
        # if self.check_errors['fileset'] > 0:
        #     for fs_name, fs_checks in self.checks_failed['fileset'].items():
        #         self.report.add_subsubsection(f"FileSet {fs_name} errors", f"fileset_{fs_name}_failed_error_checks", include_in_toc=False)
        #         for name, check in fs_checks.items():
        #             add_sanity_check_box(report = self.report, check=check, simplified=True)
        # if self.check_errors['file'] > 0:
        #     for file_name, file_checks in self.checks_failed['file'].items():
        #         self.report.add_subsubsection(f"File {file_name} errors", f"file_{file_name}_failed_error_checks", include_in_toc=False)
        #         for name, check in file_checks.items():
        #             add_sanity_check_box(report = self.report, check=check, simplified=True)
        
    def add_summary_table(self):
        """Add a summary table of calibration results"""
        self.report.add_subsection(
            'Calibration Summary Table', 
            x = self.init_x,
            y = self.lf.y - self.lf.height - 12,
            width = self.end_x - self.init_x,
            anchor='summary_table')
        sum_table = [["Wavelength", "Filter Wheel", f"slope ({self.units}/V)", f"intercept ({self.units})", "r value"]]
        for _, fs_data in self.report_data.analysis.filesets.items():
            sum_table.append([str(fs_data.meta.wave_length),
                              str(fs_data.meta.filter_wheel),
                              f'{fs_data.analysis.lr_refpd_vs_pm.slope:.4f}',
                              f'{fs_data.analysis.lr_refpd_vs_pm.intercept:.4f}',
                              f'{fs_data.analysis.lr_refpd_vs_pm.r_value:.6f}'])
        
        self.report.add_table(sum_table,
                              x=self.init_x + 300,
                              y=self.lf.y - self.lf.height - 12,
                              width=360,
                               zebra=True)
        self.report.add_paragraph(
            "The calibration analysis was executed with the following options:",
            x=self.init_x,
            y=self.lf.y - self.lf.height - 12,
            width=self.end_x - self.init_x
            )
        exec_table = [
            ['Subtracted pedestals from values', 'No' if self.report_data.meta.calling_arguments.do_not_sub_pedestals else 'Yes'],
            ['Replace zero PM stds with resolution', 'No' if self.report_data.meta.calling_arguments.do_not_replace_zero_pm_stds else 'Yes'],
            ['Use first pedestal in linear regression', 'Yes' if self.report_data.meta.calling_arguments.use_first_ped_in_linreag else 'No'],
            ['Use W as power units', 'Yes' if self.report_data.meta.calling_arguments.use_W_as_power_units else 'No'],
        ]
        self.report.add_table(exec_table,
                                x=self.init_x + 300,
                                y=self.lf.y - self.lf.height - 12,
                                width=360, zebra=True)