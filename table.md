Generated using pyGCS (Grid Convergence Study)
- https://github.com/tomrobin-teschner/pyGCS
- https://pypi.org/project/pygcs/

Table 1: Grid convergence study over 3 grids. phi represents the {INSERT MEANING OF PHI HERE} and phi_extrapolated its extrapolated value. N_cells is the number of grid elements, r the refinement ration between two successive grids. GCI is the grid convergence index in percent and its asymptotic value is provided by GCI_asymptotic, where a value close to unity indicates a grid independent solution. The order achieved in the simulation is given by p.

|        |  phi      |   N_cells   |  r  |  GCI  | GCI_asymptotic |  p   | phi_extrapolated |
|--------|:---------:|:-----------:|:---:|:-----:|:--------------:|:----:|:----------------:|
|        |           |             |     |       |                |      |                  |
| Grid 1 | 1.695e+01 |     7204737 | 1.3 | 13.76% |                |      |                  |
| Grid 2 | 1.531e+01 |     3016520 | 1.0 | 24.47% |      0.945     | 2.18 |     1.88e+01     |
| Grid 3 | 1.534e+01 |     2964899 | -   | -     |                |      |                  |
|        |           |             |     |       |                |      |                  |