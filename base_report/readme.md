

In order to render formulas you have to follow the instructions in the math_assets/README.md file. The formulas are written in LaTeX and rendered using Katex.

There is an example on how to generate a slide full of formulas. To run it, from the root of the repo:

```bash
PYTHONPATH='.' python -m base_report.example_formulas_slides
```

For it to work, you need to have katex on the assets and install playwright and chromium