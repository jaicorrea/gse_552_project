.PHONY: all clean

all: paper/paper.pdf

# ------------------------------------------------------------------
# Step 1 — Preprocessing
# ------------------------------------------------------------------
temp/clean_data.csv: input/SAT_workfingfile.dta code/preprocess.py
	python code/preprocess.py

# ------------------------------------------------------------------
# Step 2 — Analysis (produces LaTeX table fragment)
# ------------------------------------------------------------------
output/tables/table1_panels_ab.tex: temp/clean_data.csv code/analysis.py
	python code/analysis.py

# ------------------------------------------------------------------
# Step 3 — Paper compilation (run pdflatex twice for references)
# ------------------------------------------------------------------
paper/paper.pdf: paper/paper.tex output/tables/table1_panels_ab.tex
	cd paper && pdflatex paper.tex && pdflatex paper.tex

# ------------------------------------------------------------------
# Clean: remove all regenerable files (temp/ and outputs)
# ------------------------------------------------------------------
clean:
	rm -f temp/*.csv \
	      output/tables/*.tex \
	      output/figures/*.png output/figures/*.pdf \
	      paper/paper.pdf paper/paper.aux paper/paper.log \
	      paper/paper.out paper/paper.toc
