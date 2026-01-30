import os

from base_report import BaseReport

lorem =         """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod 
        tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim 
        veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea 
        commodo consequat. Duis aute irure dolor in reprehenderit in voluptate 
        velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint 
        occaecat cupidatat non proident, sunt in culpa qui officia deserunt 
        mollit anim id est laborum."""


def build_example_report() -> None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    output_path = os.path.join(project_root, "example_report.pdf")
    logo_path = os.path.join(current_dir, "example_files", "chatgpt_logo.png")
    mex_image_path = os.path.join(current_dir, "example_files", "mex_vertical_image.png")
    image_path = os.path.join(
        current_dir,
        "example_files",
        "horizontal_plot.png",
    )
    second_image_path = os.path.join(
        current_dir,
        "example_files",
        "rectangular_portrait.png",
    )

    pdf_plot_path = os.path.join(
        current_dir,
        "example_files",
        "squared_plot.pdf",
    )

    report = BaseReport(
        output_path=output_path,
        title="Example Report",
        subtitle="Example Summary",
        logo_path=logo_path,
        serial_number="CAL-2025-001",
    )

    report.add_section("Overview", anchor="overview")
    report.add_paragraph(
        "This report demonstrates the base layout, section styling, and header "
        "metadata for calibration output."
    )
    report.add_paragraph(lorem)
    report.add_sanity_check(severity='Info', title='Sanity Check Passed', 
                            description='All parameters are within expected ranges.', passed=True)
    report.add_sanity_check(severity='Warning', title='Sanity Check Not Passed', 
                            description=lorem, passed=False)
    report.add_sanity_check(severity='Error', title='Error Sanity Check Not Passed', 
                            description=lorem, passed=False)
    report.add_sanity_check(severity='Error', title='Error Sanity Check Passed', 
                            description="Small text", passed=True)
    report.add_paragraph(lorem)
    report.add_paragraph(lorem)
    report.add_figure(pdf_plot_path, description="Sample PDF plot embedded as figure.",
                      center=True)
    report.add_paragraph(lorem)
    report.add_paragraph(lorem)
    report.add_paragraph(lorem)
    report.add_info_box(
        "This is an <b>info</b> box. Use <b>bold</b> or <i>italics</i> with "
        "inline tags in the text."
    )
    report.add_warning_box(
        "This is a warning box. You can mix <b>bold</b> and <i>italic</i> text."
    )
    report.add_error_box(
        "This is an error box using red styling for emphasis."
    )
    report.add_page()
    report.add_table_of_contents(page_break=False)
    report.add_page()
    report.add_section("Results (no anchor on ToC)")

    report.add_subsection("Sample Table", "sample_table")
    report.add_table(        data = [
            ["Parameter", "Value", "Unit"],
            ["Laser Power", "1.2", "W"],
            ["Temperature", "22.5", "C"],
            ["Humidity", "40", "%"],
        ])
    report.add_subsubsection("Sample Subsubsection")
    report.add_paragraph(lorem)
    report.add_subsection("Condensed Table", "condensed_table")

    table1_data = [
            ["", "1064 FW1", "1064 FW4", "532 FW1", "532 FW4", "532 FW7"],
            ["slope", "1,777", "1.7864", "1.6999", "1.98899", "532 FW7"],
            ["slope2", "1,777", "1.7864", "1.6999", "1.98899", "532 FW7"],
            ["slope3", "1,777", "1.7864", "1.6999", "1.98899", "532 FW7"],
            ["slope4", "1,777", "1.7864", "1.6999", "1.98899", "532 FW7"],
            ["slope5", "1,777", "1.7864", "1.6999", "1.98899", "532 FW7"],
        ]
    table2_data = [
            ["", "1064 FW1", "1064 FW4", "532 FW1", "532 FW4", "532 FW7", "whateverddfsf sf"],
            ["slope", "1,777", "1.7864", "1.6999", "1.98899", "532 FW7", "whateverddfsf sf"],
            ["slope2", "1,777", "1.7864", "1.6999", "1.98899", "532 FW7", "whateverddfsf sf"],
            ["slope3", "1,777", "1.7864", "1.6999", "1.98899", "532 FW7", "whateverddfsf sf"],
            ["slope4", "1,777", "1.7864", "1.6999", "1.98899", "532 FW7", "whateverddfsf sf"],
            ["slope5", "1,777", "1.7864", "1.6999", "1.98899", "532 FW7", "whateverddfsf sf"],
        ]

    report.add_condensed_table(data=table1_data, keep_together=True)
    report.add_condensed_table(data=table2_data, keep_together=True, description="A centered table", center=True)
    report.add_condensed_table(data=table2_data, keep_together=True, description="A zebra centered table", 
                                       center=True, zebra=True)

    report.add_subsection("Sample Image")
    report.add_figure(image_path, description="Sample horizontal image.", center=True, width_mm=200)
    report.add_figure(second_image_path, description="Sample rectangular portrait image. with width setting.", center=True, width_mm=100)
    report.add_paragraph('Image description with a link to <a href="https://www.openai.com">OpenAI</a>. It is big, so it does not fit on the current page and should be moved to the next page.')
    desc = "Image from <a href='https://chat.openai.com'>Chat GPT</a>"
    report.add_figure(mex_image_path, description=desc, center=True)

    report.add_page()
    report.add_section("Additional Notes", anchor="additional_notes")
    report.add_paragraph("Add new content using sections, tables, and images.")
    report.add_paragraph("This is an example report generated using the BaseReport class."
                         " Modify and extend it to suit your calibration reporting needs."
                         " You can add more sections, tables, images, and customize the layout as required." \
                         " You can also add links to sections within the report for easy navigation."
                         " <a href='document:overview'>this is a link to the overview section</a>.")



    report.build()


if __name__ == "__main__":
    build_example_report()
