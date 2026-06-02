# gse_552_project — Replication of Akhtari, Bau & Laliberté (2020)

This repository replicates **Figure 3** from:

> Akhtari, Mitra, Natalie Bau, and Jean-William P. Laliberté. 2020.
> "Affirmative Action and Pre-College Human Capital."
> *NBER Working Paper* No. 27779. http://www.nber.org/papers/w27779

Figure 3 presents **synthetic control estimates** of the effect of the
*Grutter v. Bollinger* (2003) Supreme Court ruling — which reinstated
affirmative action in TX, LA, and MS — on mean math SAT scores for
underrepresented minorities (URMs) and white students.

**Paper's headline numbers:** URMs +10.778 pts, Whites +6.273 pts.
**Our replication:** URMs +8.434 pts, Whites +5.239 pts (using the
weights in the shipped replication package; see paper for discussion).

---

## Repository Layout

```
gse_552_project/
├── input/
│   ├── SC_workingfile.dta         # State-year panel (TX+LA+MS collapsed)
│   ├── SCweights/
│   │   ├── nonURMm10.dta          # SC weights for whites (spec10)
│   │   └── URMm10.dta             # SC weights for URMs (spec10)
│   ├── SAT_workfingfile.dta       # Raw SAT panel (kept for reference)
│   └── data_dictionary.md
├── code/
│   ├── preprocess.py              # Merge SC data + weights → temp/sc_panel.csv
│   └── analysis.py                # Apply weights, plot Figure 3, write scalars
├── output/
│   ├── figures/
│   │   └── figure3.png            # Replication of Figure 3 (tracked in git)
│   └── tables/
│       ├── sc_dd_urm.tex          # Scalar: SC DD estimate for URMs
│       └── sc_dd_non.tex          # Scalar: SC DD estimate for whites
├── temp/                          # Intermediate files — gitignored
├── paper/
│   ├── paper.tex                  # 4-page write-up
│   └── paper.pdf                  # Compiled output
├── Makefile                       # Declarative pipeline
├── run_all.sh                     # Convenience wrapper: make clean && make
├── .gitignore
└── README.md
```

---

## Data Source

The SC_workingfile.dta and SCweights were prepared by the original authors
using Stata's `synth` command. The replication package is available at:

https://www.openicpsr.org/openicpsr/project/146381/version/V1/view

All input files are committed directly to `input/` (well under 25 MB total).
See `input/data_dictionary.md` for variable descriptions.

---

## Prerequisites

| Tool | Version tested |
|---|---|
| Python | 3.10+ |
| pandas | 2.x |
| numpy | 1.x |
| matplotlib | 3.x |
| pyfixest | 0.x |
| pyreadstat | 1.x |
| pdflatex | TeX Live 2023 or MiKTeX |

Install Python dependencies:

```bash
pip install pandas numpy matplotlib pyfixest pyreadstat
```

---

## Reproducing the Paper

```bash
git clone https://github.com/jaicorrea/gse_552_project.git
cd gse_552_project
make
```

Or use the convenience wrapper:

```bash
bash run_all.sh
```

The compiled paper will be at `paper/paper.pdf`.

---

## Results

| | Paper | Our Replication |
|---|---|---|
| **URMs — SC DD estimate** | +10.778 pts | +\input{output/tables/sc_dd_urm.tex} pts |
| **Whites — SC DD estimate** | +6.273 pts | +\input{output/tables/sc_dd_non.tex} pts |

Point estimates are directionally consistent and qualitatively identical.
The gap from the paper's values reflects a difference between the weights
in the shipped replication package and those used to produce the published
figure (see paper Section 4 for full discussion).
