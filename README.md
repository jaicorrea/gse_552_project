# gse_552_project — Replication of Akhtari, Bau & Laliberté (2020)

This repository replicates **Table 1, Panels A and B** (columns 1 and 2 — Math and Verbal SAT scores) from:

> Akhtari, Mitra, Natalie Bau, and Jean-William P. Laliberté. 2020.
> "Affirmative Action and Pre-College Human Capital."
> *NBER Working Paper* No. 27779. http://www.nber.org/papers/w27779

The result of interest is a difference-in-differences estimate of the effect
of the *Grutter v. Bollinger* (2003) Supreme Court ruling — which reinstated
affirmative action in TX, LA, and MS — on mean SAT scores for underrepresented
minorities (Panel A) and white students (Panel B).

**Paper's headline number:** Panel A math DD coefficient = **8.009***
(s.e. 1.544).  Our replication obtains **8.009*** (s.e. 1.565) — exact
match on the point estimate; minor SE difference due to Stata vs. Python
degrees-of-freedom correction in clustered standard errors.

---

## Repository Layout

```
gse_552_project/
├── input/
│   ├── SAT_workfingfile.dta      # Raw data (state×race×year panel, 1998–2010)
│   └── data_dictionary.md        # Variable descriptions
├── code/
│   ├── preprocess.py             # Load raw data → temp/clean_data.csv
│   └── analysis.py               # DiD regressions → output/tables/*.tex
├── output/
│   ├── figures/                  # (empty for this replication)
│   └── tables/
│       └── table1_panels_ab.tex  # LaTeX table fragment consumed by paper.tex
├── temp/                         # Intermediate files — gitignored
├── paper/
│   ├── paper.tex                 # ~4-page write-up
│   └── paper.pdf                 # Compiled output
├── Makefile                      # Declarative pipeline
├── run_all.sh                    # Convenience wrapper: make clean && make
├── .gitignore
└── README.md
```

---

## Data Source

Data were digitized by Akhtari, Bau & Laliberté from College Board public
reports. The replication package (including `SAT_workfingfile.dta`) is
available at:

https://www.openicpsr.org/openicpsr/project/146381/version/V1/view

The raw data file is committed directly to `input/` (≈ 1 MB).
See `input/data_dictionary.md` for variable descriptions.

---

## Prerequisites

| Tool | Version tested |
|---|---|
| Python | 3.10+ |
| pandas | 2.x |
| numpy | 1.x |
| statsmodels | 0.14+ |
| pyreadstat | 1.x |
| pdflatex | TeX Live 2023 or MiKTeX |

Install Python dependencies:

```bash
pip install pandas numpy statsmodels pyreadstat
```

---

## Reproducing the Paper

```bash
git clone https://github.com/jaicorrea/gse_552_project.git
cd gse_552_project
# No data download needed — input/ is committed
make
```

Or use the convenience wrapper:

```bash
bash run_all.sh
```

The compiled paper will be at `paper/paper.pdf`.

To start from a completely clean state:

```bash
make clean
make
```

---

## Results

| | Math (Paper) | Math (Ours) | Verbal (Paper) | Verbal (Ours) |
|---|---|---|---|---|
| **Panel A — URMs** | 8.009*** (1.544) | 8.009*** (1.565) | −0.634 (1.784) | −0.634 (1.808) |
| **Panel B — Whites** | 4.048*** (0.984) | 4.048*** (1.024) | 0.034 (0.888) | 0.034 (0.925) |

Point estimates match exactly. N and R² are identical to the paper.
SE differences arise from Stata's `reghdfe` DOF correction vs. Python's
sandwich estimator.
