from __future__ import annotations

import os

from reportlab.lib import colors

from base_report import BaseReportSlides


def build_formula_gallery_report() -> None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    output_path = os.path.join(project_root, "example_formulas_slides.pdf")
    logo_path = os.path.join(current_dir, "example_files", "chatgpt_logo.png")

    report = BaseReportSlides(
        output_path=output_path,
        title="Formula Gallery",
        subtitle="Complex equations rendered with local KaTeX scaffold",
        logo_path=logo_path,
    )

    report.add_slide(title="Formula Gallery", subtitle="Well-known equations")
    frame = report.get_active_area()

    formulas: list[tuple[str, str]] = [
        ("Einstein Field Equations", r"R_{\mu\nu} - \frac{1}{2}R g_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4}T_{\mu\nu}"),
        ("Navier-Stokes", r"\rho\left(\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u}\cdot\nabla)\mathbf{u}\right) = -\nabla p + \mu \nabla^2\mathbf{u} + \mathbf{f}"),
        ("Time-dependent Schrodinger", r"i\hbar\frac{\partial}{\partial t}\Psi(\mathbf{r},t)=\left[-\frac{\hbar^2}{2m}\nabla^2+V(\mathbf{r},t)\right]\Psi(\mathbf{r},t)"),
        ("Black-Scholes PDE", r"\frac{\partial V}{\partial t}+\frac{1}{2}\sigma^2 S^2\frac{\partial^2V}{\partial S^2}+rS\frac{\partial V}{\partial S}-rV=0"),
        ("Euler-Lagrange", r"\frac{\partial \mathcal{L}}{\partial q_i}-\frac{d}{dt}\left(\frac{\partial \mathcal{L}}{\partial \dot q_i}\right)=0"),
        ("Fourier Transform", r"\hat f(\xi)=\int_{-\infty}^{\infty} f(x)e^{-2\pi i x \xi}\,dx"),
        ("Riemann Zeta Functional Eq.", r"\zeta(s)=2^s\pi^{s-1}\sin\!\left(\frac{\pi s}{2}\right)\Gamma(1-s)\zeta(1-s)"),
        ("Maxwell (Differential Form)", r"\nabla\cdot\mathbf{E}=\frac{\rho}{\varepsilon_0},\ \nabla\cdot\mathbf{B}=0,\ \nabla\times\mathbf{E}=-\frac{\partial \mathbf{B}}{\partial t},\ \nabla\times\mathbf{B}=\mu_0\mathbf{J}+\mu_0\varepsilon_0\frac{\partial \mathbf{E}}{\partial t}"),
    ]

    cols = 2
    rows = 4
    gap_x = 12
    gap_y = 10
    tile_width = (frame.width - gap_x) / cols
    tile_height = (frame.height - (rows - 1) * gap_y) / rows

    header_pad = 6
    formula_pad = 8
    title_height = 15
    start_y = frame.y

    for idx, (name, formula) in enumerate(formulas):
        r = idx // cols
        c = idx % cols
        x = frame.x + c * (tile_width + gap_x)
        y = start_y - r * (tile_height + gap_y)

        report.add_rectangle(
            x=x,
            y=y,
            width=tile_width,
            height=tile_height,
            fill_color=colors.HexColor("#F7FAFD"),
            stroke_color=colors.HexColor("#B7C3D0"),
            stroke_width=0.6,
        )
        report.add_paragraph(
            text=name,
            x=x + header_pad,
            y=y - header_pad,
            width=tile_width - 2 * header_pad,
            font_size=9.5,
            bold=True,
        )
        report.add_formula(
            formula=formula,
            x=x + formula_pad,
            y=y - title_height - formula_pad,
            width=tile_width - 2 * formula_pad,
            height=tile_height - title_height - 2 * formula_pad,
            font_size=10.5,
            display_mode=True,
            fallback_to_text=True,
        )

    report.build()


if __name__ == "__main__":
    build_formula_gallery_report()
