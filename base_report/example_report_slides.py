import os

from base_report_slides import BaseReportSlides, TextStyle, Frame
from reportlab.lib import colors
import random

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
    mex_image_path = os.path.join(
        current_dir, "example_files", "mex_vertical_image.png")
    image_path = os.path.join(
        current_dir,
        "example_files",
        "horizontal_plot.png",
    )
    moon_image_path = os.path.join(
        current_dir,
        "example_files",
        "moon.png",
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
        logo_path=logo_path,
    )

    report.serial_number = "Calibration-123456"

    ###################################################

    report.add_slide(title="Images", subtitle="Placing both height and width")

    frames = [
        Frame(x=10, y=480, width=360, height=100),
        Frame(x=375, y=480, width=100, height=100),
        Frame(x=10, y=375, width=100, height=370),
        Frame(x=115, y=375, width=360, height=370),
        Frame(x=485, y=480, width=465, height=475),
    ]
    for f in frames:
        report.debug = True
        report.add_rectangle(
            x=f.x,
            y=f.y,
            width=f.width,
            height=f.height,
            fill_color=colors.HexColor("#EDEDED"),
            stroke_color=colors.HexColor("#474747"),
            stroke_width=0.5,
        )
        report.debug = False
        report.add_plot(moon_image_path, x=f.x, y=f.y, width=f.width,
                        height=f.height)

    ###################################################

    report.add_slide(title="Images", subtitle="Placing only width on plot")

    frames = [
        Frame(x=10, y=480, width=360, height=100),
        Frame(x=375, y=480, width=100, height=100),
        Frame(x=10, y=375, width=100, height=370),
        Frame(x=115, y=375, width=360, height=370),
        Frame(x=485, y=480, width=465, height=475),
    ]
    for f in frames:
        report.debug = True
        report.add_rectangle(
            x=f.x,
            y=f.y,
            width=f.width,
            height=f.height,
            fill_color=colors.HexColor("#EDEDED"),
            stroke_color=colors.HexColor("#474747"),
            stroke_width=0.5,
        )
        report.debug = False
        report.add_plot(moon_image_path, x=f.x, y=f.y, width=f.width)

    ###################################################

    report.add_slide(title="Images", subtitle="Placing only height on plot")

    frames = [
        Frame(x=10, y=480, width=360, height=100),
        Frame(x=375, y=480, width=100, height=100),
        Frame(x=10, y=375, width=100, height=370),
        Frame(x=115, y=375, width=360, height=370),
        Frame(x=485, y=480, width=465, height=475),
    ]
    for f in frames:
        report.debug = True
        report.add_rectangle(
            x=f.x,
            y=f.y,
            width=f.width,
            height=f.height,
            fill_color=colors.HexColor("#EDEDED"),
            stroke_color=colors.HexColor("#474747"),
            stroke_width=0.5,
        )
        report.debug = False
        report.add_plot(moon_image_path, x=f.x, y=f.y, height=f.height)

    ###################################################

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
    frame = report.add_table(
        data=[["Header 1", "Header 2", "Header 3"],
              ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],
              ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"],
              ["Row 3 Col 1", "Row 3 Col 2", "Row 3 Col 3"],
              ["Row 4 Col 1", "Row 4 Col 2", "Row 4 Col 3"],],
        x=480,
        y=frame.y - frame.height - 20,
        width=210,
        col_widths=[50, 160, 100],
        zebra=True,
    )
    report.add_paragraph(
        "This table was provided specific column widths and table width. "
        "Table width overrides column widths, but columns widths then are used " \
        "as relative proportions." \
        "" \
        "Col_widths provided: [50, 160, 100]. Total: 310. " \
        "Table width provided: 210. " \
        "So the actual column widths are: [33.87, 108.39, 67.74].",
        x=480,
        y=frame.y - frame.height - 30,
        width=400,
        font_size=12
    )

    ###################################################

    report.add_slide(title="ToC", subtitle="Table of Contents")
    frames = []
    num_columns = 3
    margin_x = 20
    margin_y = 10
    full_width = 960
    full_height = 540 - 50
    column_width = (full_width - (num_columns + 1) * margin_x) / num_columns
    x = margin_x
    y = full_height - margin_y
    toc_height = full_height - 2 * margin_y
    for i in range(3):
        frames.append(Frame(x=x, y=y, width=column_width, height=toc_height))
        x += column_width + margin_x
    for f in frames:
        report.debug = True
        report.add_rectangle(
            x=f.x - margin_x / 3,  # 3 to leave space between columns
            y=f.y + margin_y / 2,
            width=f.width + 0.666 * margin_x,
            height=f.height + margin_y,
            fill_color=colors.HexColor("#EDEDED"),
            stroke_color=colors.HexColor("#474747"),
            stroke_width=0.5,
        )
        report.debug = False
    report.add_table_of_contents(frames=frames, dot_leader=True)

    ###################################################

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
    total_height = (lorem_expexted.height +
                    lorem_double_expected.height + 10 + 20)
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

    ###################################################

    report.add_slide(title="Table styling",
                     subtitle="Without style and with style")
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
        header_style=TextStyle("Helvetica-Bold", 11, 13,
                               colors.HexColor("#EEEEEE")),
        body_style=TextStyle("Times-Roman", 11, 13,
                             colors.HexColor("#5E5E5E")),
        header_background=colors.HexColor("#930073"),
        zebra_background=colors.HexColor("#FBC4F4"),
    )
    report.add_table(table_data, x=480, y=410, width=420, zebra=True)

    ###################################################

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
            x=x,
            y=y,
            width=500,
            font_size=10,
        )
    report.add_paragraph("x = 100, y = 200", x=100,
                         y=200, width=500, font_size=30)
    report.add_section("Overview", x=10, y=400, width=500,
                       anchor="overview", toc=True)
    report.add_paragraph(
        "See the <a href='introduction'>Introduction section</a> for details.",
        x=700, y=300, width=200
    )
    ###################################################

    report.add_slide(title="Second Slide", subtitle="With a plot")
    frame = report.get_plot_frame(image_path, x=30, y=480, width=800)
    report.add_rectangle(frame.x-10, frame.y+10, frame.width+20, frame.height+20,
                         fill_color=colors.HexColor("#FFF4DF"),
                         stroke_color=colors.HexColor("#B06B0B"), stroke_width=1)
    report.add_plot(image_path, x=30, y=480, width=800)

    ###################################################

    report.add_slide(title="Third Slide", subtitle="With multiple images")
    report.debug = True
    report.add_plot(mex_image_path, x=50, y=400, width=200)
    report.add_plot(second_image_path, x=300, y=400, width=200)
    report.add_plot(pdf_plot_path, x=550, y=400, width=200)
    report.debug = False
    ###################################################

    report.add_slide(title="Fourth Slide", subtitle="Font sizes")

    y = 480
    linespace = 6
    sizes = [10, 14, 16, 18, 24, 32, 40, 48, 56, 64, 72, 80]
    for s in sizes:
        frame = report.add_paragraph(
            f"Font size: {s}", x=20, y=y, width=500, font_size=s)
        y -= s + linespace

    ###################################################

    report.add_slide(title="5th Slide", subtitle="Font sizes bold")

    y = 480
    linespace = 6
    sizes = [10, 14, 16, 18, 24, 32, 40, 48, 56, 64, 72, 80]
    for s in sizes:
        report.add_paragraph(f"Bold font size: {s}", x=20, y=y, width=890, font_size=s, bold=True,
                             font_color=colors.HexColor("#0B6B46"))
        y -= s + linespace

    ###################################################

    report.add_slide(title="Sections")
    report.add_section("Introduction", x=20, y=480,
                       width=300, anchor="introduction", toc=True)
    report.add_paragraph(
        "See the <a href='overview'>Overview section</a> for details.",
        x=40, y=300, width=500
    )

    ###################################################

    report.add_slide(title="Final Slide", subtitle="The End")
    report.add_paragraph(
        "This is the final slide of the example report."*100,
        x=40,
        y=480,
        width=440,
        font_size=15,
    )
    report.add_plot(
        mex_image_path,
        x=500,
        y=480,
        width=440
    )

    ###################################################

    report.add_slide(title="ToC", subtitle="Table of Contents")
    report.add_table_of_contents(x=40, y=480, width=430)

    # Let's add a lot of slides with sections and subsections to test the ToC generation
    for i in range(1, 7):
        ###################################################

        report.add_slide(
            title=f"Section Slide {i}", subtitle=f"Section {i} Overview")
        y = 480
        report.add_section(f"Section {i}", x=20, y=y,
                           width=300, anchor=f"section_{i}", toc=True)
        for j in range(1, 4):
            if random.random() < 0.3:
                ###################################################

                report.add_slide(
                    title=f"Random Slide {i}.{j}", subtitle=f"Random content")
                y = 480
            y -= 20
            report.add_subsection(f"Subsection {i}.{j}", x=40, y=y,
                                  width=260, anchor=f"subsection_{i}_{j}", toc=True)
            for k in range(1, 3):
                y -= 20
                report.add_subsubsection(f"SubSubsection {i}.{j}.{k}", x=40, y=y - (j-1)*60,
                                         width=260, anchor=f"subsection_{i}_{j}", toc=True)
                y -= 20
                fontsize = random.random()*10 + 7
                frame = report.add_paragraph(
                    f"This is subsubsection {i}.{j}.{k} using fontsize {fontsize:.2f}. "*10,
                    x=60,
                    y=y,
                    width=620,
                    font_size=fontsize
                )
                y -= frame.height - 10

    report.build(multibuild=True)


if __name__ == "__main__":
    build_example_report()
