import os

from base_report_slides import BaseReportSlides, TextStyle
from reportlab.lib import colors

lorem = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod 
        tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim 
        veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea 
        commodo consequat. Duis aute irure dolor in reprehenderit in voluptate 
        velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint 
        occaecat cupidatat non proident, sunt in culpa qui officia deserunt 
        mollit anim id est laborum."""

lorem_double_paragraph = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus laoreet scelerisque rhoncus. Duis fringilla sapien a ipsum posuere ullamcorper. Phasellus nec justo ante. Pellentesque lectus nibh, convallis vitae suscipit in, eleifend sed felis. Donec hendrerit metus vel nulla ultrices, a condimentum neque maximus. Nullam interdum nibh id accumsan gravida. Cras at molestie risus. Quisque vehicula vel quam vitae molestie. Curabitur mollis lacus id semper congue. Ut eget tristique ligula, non molestie lacus. Nunc fringilla risus ipsum, in porta augue sodales sit amet. Suspendisse potenti.


Nam tristique fermentum risus, non molestie turpis. Donec accumsan lacinia sem, in aliquam sapien rutrum sit amet. Pellentesque dignissim luctus massa eget mattis. Suspendisse potenti. Sed consectetur risus in nisl porttitor convallis. Pellentesque eu ultricies purus. Donec varius quam ac tellus cursus tincidunt. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Nullam accumsan nisi vel orci mollis, nec luctus lectus sodales. Nulla lectus tellus, efficitur viverra molestie at, pretium sit amet erat. Vivamus eget erat nibh. Proin bibendum, orci quis convallis dictum, tortor felis pulvinar ligula, eget eleifend arcu turpis finibus felis.
"""


def build_example_report() -> None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    output_path = os.path.join(project_root, "example_report_slides.pdf")
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

    report = BaseReportSlides(
        output_path=output_path,
        title="Example Report",
        subtitle="Example Summary",
        logo_path=logo_path
    )

    report.add_slide(title="Example Slide", subtitle="Table")
    frame = report.add_table(
        data=[["Header 1", "Header 2", "Header 3"],
              ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],    
              ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"],
              ["Row 3 Col 1", "Row 3 Col 2", "Row 3 Col 3"],
              ["Row 4 Col 1", "Row 4 Col 2", "Row 4 Col 3"],],
        x=20,
        y=480,
        width=400,
        zebra=True,
    )
    report.add_table(
        data=[["Header 1", "Header 2", "Header 3"],
              ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],    
              ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"],
              ["Row 3 Col 1", "Row 3 Col 2", "Row 3 Col 3"],
              ["Row 4 Col 1", "Row 4 Col 2", "Row 4 Col 3"],],
        x=20,
        y=frame.y - frame.height - 20,
        width=400,
        col_widths=[150, 100, 130],
        zebra=True,
    )

    report.add_slide(title="Title Slide", subtitle="Subtitle Slide")
    report.debug = True
    lorem_expexted = report.get_paragraph_frame(
        lorem,
        x=40,
        y=480,
        width=880,
        font_size=25,
    )
    lorem_double_expected = report.get_paragraph_frame(
        lorem_double_paragraph,
        x=40,
        y=lorem_expexted.y - lorem_expexted.height - 10,
        width=880,
        font_size=12,
        preserve_newlines=True,
    )
    total_height = (lorem_expexted.height + lorem_double_expected.height + 10 + 20)
    report.add_rectangle(
        x=30, y=480, width=900, height=total_height,
        fill_color=colors.HexColor("#FFF4DF"),
        stroke_color=colors.HexColor("#B06B0B"),
        stroke_width=1,
    )
    frame = report.add_paragraph(
        lorem,
        x=40,
        y=480,
        width=880,
        font_size=25,
    )
    frame = report.add_paragraph(
        lorem_double_paragraph,
        x=40,
        y=frame.y - frame.height - 10,
        width=880,
        font_size=12,
        preserve_newlines=True,
    )
    report.add_paragraph(
        f"Paragraph height = {frame.height:.1f}",
        x=40,
        y=frame.y - frame.height - 20,
        width=880,
        font_size=19,
        font_color=colors.HexColor("#0B6B46"),
        bold=True,
    )
    report.debug = False

    report.add_slide(title="Table styling", subtitle="Without style and with style")
    table_data = [
        ["Metric", "Value", "Unit"],
        ["Offset", "0.12", "mV"],
        ["Gain", "1.03", "x"],
        ["Drift", "0.004", "mV/min"],
    ]
    report.add_table(
        table_data,
        x=40,
        y=410,
        width=420,
        zebra=True,
        col_align=["left", "right", "center"],
    )
    report.set_table_style(
        header_style=TextStyle("Helvetica-Bold", 11, 13, colors.HexColor("#EEEEEE")),
        body_style=TextStyle("Times-Roman", 11, 13, colors.HexColor("#5E5E5E")),
        header_background=colors.HexColor("#930073"),
        zebra_background=colors.HexColor("#FBC4F4"),
    )
    report.add_table(table_data, x=480, y=410, width=420, zebra=True)
    
    report.add_slide(title="First Slide", subtitle="With a section")    
    report.add_rectangle(
        x=20,
        y=480,
        width=880,
        height=460,
        fill_color=colors.HexColor("#DFFFF4"),
        stroke_color=colors.HexColor("#0B6B46"),
        stroke_width=1,
    )
    para_frame = report.add_paragraph(
        "x=20, y=480, width=880, height=460",
        x=30,
        y=480,
        width=100,
        font_size=10,
    )
    report.add_paragraph(
        f"paragraph height = {para_frame.height:.1f}",
        x=30,
        y=480 - para_frame.height - 6,
        width=200,
        font_size=9,
        font_color=colors.HexColor("#0B6B46"),
    )
    for i in range(60):
        report.add_paragraph(
            f"x = {i * 10} , y = {i * 10}",
            x=i * 10,
            y=i * 10,
            width=500,
            font_size=10,
        )
        x = 400 + i * 10
        y = 500 - i * 10
        report.add_paragraph(
            f"x = {x} , y = {y}",
            x= x,
            y= y,
            width=500,
            font_size=10,
        )
    report.add_paragraph("x = 100, y = 200", x=100, y=200, width=500, font_size=30)
    report.add_section("Overview", x=10, y=400, width=500, anchor="overview", toc=True)
    report.add_slide(title="Second Slide", subtitle="With a plot")
    frame = report.get_plot_frame(image_path, x=30, y=480, width=800)
    report.add_rectangle(frame.x-10, frame.y+10, frame.width+20, frame.height+20,
                         fill_color=colors.HexColor("#FFF4DF"), 
                         stroke_color=colors.HexColor("#B06B0B"), stroke_width=1)
    report.add_plot(image_path, x=30, y=480, width=800)

    report.add_slide(title="Third Slide", subtitle="With multiple images")
    report.debug = True
    report.add_plot(mex_image_path, x=50, y=400, width=200)
    report.add_plot(second_image_path, x=300, y=400, width=200)
    report.add_plot(pdf_plot_path, x=550, y=400, width=200)
    report.debug = False
    report.add_slide(title="Fourth Slide", subtitle="Font sizes")

    y = 480
    linespace = 6
    sizes = [10, 14,16,18,24,32,40,48, 56,64,72,80]
    for s in sizes:
        frame = report.add_paragraph(f"Font size: {s}", x=20, y=y, width=500, font_size=s)
        y -= s + linespace
    
    report.add_slide(title="5th Slide", subtitle="Font sizes bold")

    y = 480
    linespace = 6
    sizes = [10, 14,16,18,24,32,40,48, 56,64,72,80]
    for s in sizes:
        report.add_paragraph(f"Bold font size: {s}", x=20, y=y, width=890, font_size=s, bold=True,
                             font_color=colors.HexColor("#0B6B46"))
        y -= s + linespace
    
    report.save()


if __name__ == "__main__":
    build_example_report()
