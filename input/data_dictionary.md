# Data Dictionary — SAT_workfingfile.dta

Source: Akhtari, Bau & Laliberté (2020), NBER Working Paper 27779.
Replication package: https://www.openicpsr.org/openicpsr/project/146381/version/V1/view

Each row is a **state × ethnicity × year** cell, covering 1998–2010.
Data were digitized by the authors from College Board public reports.

| Variable | Type | Description |
|---|---|---|
| year | int | Calendar year (1998–2010) |
| geography | str | State name |
| ethnicity | str | Ethnicity group label |
| geo_id | float | Numeric state identifier (used for state fixed effects) |
| ethn_id | float | Numeric ethnicity identifier (used for ethnicity fixed effects) |
| mathscoretotalN | float | Mean math SAT score for the cell (main outcome, Panels A–C) |
| verbalscoretotalN | float | Mean verbal SAT score for the cell |
| takesattotalN | float | Number of SAT test-takers in the cell (used as analytical weight) |
| regsattotalN | float | Number of registered SAT takers |
| treat | float | 1 if state is treated (TX, LA, MS — banned AA before *Grutter*) |
| post | float | 1 if year > 2003 (post-*Grutter v. Bollinger*) |
| ban | float | 1 if state has an AA ban in the control group (policy control) |
| AA | float | 1 if state actively uses AA in a given year |
| BH | float | 1 if ethnicity is Black or Hispanic (URM; used for Panel A) |
| W | float | 1 if ethnicity is White (used for Panel B) |
| A | float | 1 if ethnicity is Asian (used for Panel C) |
| B | float | 1 if ethnicity is Black |
| H | float | 1 if ethnicity is Hispanic |
| minority | float | 1 if ethnicity is any underrepresented minority |
| BHvsWA | float | 1 if BH, 0 if White or Asian (used for DDD Panel D) |
| ethn | str | Short ethnicity label |
| noban_sample | float | 1 if state is in the no-ban robustness sample |
| sc_sample | float | 1 if state is in the synthetic-control sample |
| fixed_weights | float | Pre-treatment average test-taker count (used for col 3 weights) |
| math_detrend | float | Math SAT score, linearly de-trended (used in robustness) |
| verbal_detrend | float | Verbal SAT score, linearly de-trended |
| TX / MS / LA / MSLA | float | Individual treated-state indicators |
