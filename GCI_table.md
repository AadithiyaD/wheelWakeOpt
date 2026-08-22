Grid convergence study over 3 grids. phi represents the RMSE between predicted velocity and PIV measurements over two streamwise planes in the wake, and phi_extrapolated its extrapolated value. N_cells is the number of grid elements, r the refinement ration between two successive grids. GCI is the grid convergence index in percent. The order achieved in the simulation is given by p.

|        |    phi    |   N_cells   |   r    |  GCI    |    p   | phi_extrapolated |
|--------|:---------:|:-----------:|:------:|:-------:|:------:|:----------------:|
|        |           |             |        |         |        |                  |
| Grid 1 | 15.143524 |   5170522   | 1.4264 | 6.9695% |        |                  |
| Grid 2 | 14.718514 |   1781589   | 1.3455 | 3.8291% | 2.2303 |     15.4953      |
| Grid 3 | 14.894821 |   731383    | -      | -       |        |                  |

Therefore we can say:
- The total RMSE for the second grid is: 14.71 +- 0.563
- With p being close to the nominal order of accuracy 2, we can say that the 3 grids are in the asymptotic region
- Choosing Grid 2 as the choice for all subsequent use,
    - $U_{95\%} = +- 0.563 m/s$, (3.8291% of 14.718) 
        - $U_{95\%}$ is a $2\sigma$ uncertainty estimate
    - Similarly, $u_{num} = GCI/k => u_{num} = +- 0.2815 m/s$ 
        - $k=2$, since we have oscillatory covergence
        - $u_{num}$ is a $\sigma$ uncertainty estimate

