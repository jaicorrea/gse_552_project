.PHONY: all clean

all: paper/paper.pdf

# ------------------------------------------------------------------
# Step 1 — Preprocessing
# ------------------------------------------------------------------
temp/sc_panel.csv: input/SC_workingfile.dta \
                   input/SCweights/nonURMm10.dta \
                   input/SCweights/URMm10.dta \
                   code/preprocess.py
	python code/preprocess.py

# ------------------------------------------------------------------
# Step 2 — Analysis (produces Figure 3 and scalar .tex files)
# ------------------------------------------------------------------
output/figures/figure3.png output/tables/sc_dd_urm.tex output/tables/sc_dd_non.tex: \
    temp/sc_panel.csv code/analysis.py
	python code/analysis.py

# ------------------------------------------------------------------
# Step 3 — Paper compilation (run pdflatex twice for references)
# ------------------------------------------------------------------
paper/paper.pdf: paper/paper.tex \
                 output/figures/figure3.png \
                 output/tables/sc_dd_urm.tex \
                 output/tables/sc_dd_non.tex
	cd paper && pdflatex paper.tex && pdflatex paper.tex

# ------------------------------------------------------------------
# Clean: remove all regenerable files
# ------------------------------------------------------------------
clean:
	rm -f temp/*.csv \
	      output/tables/*.tex \
	      output/figures/*.png output/figures/*.pdf \
	      paper/paper.pdf paper/paper.aux paper/paper.log \
	      paper/paper.out paper/paper.toc
