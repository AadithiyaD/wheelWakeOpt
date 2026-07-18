from pyGCS import GCS
from error_calc import calc_rmse_mae

# Specify as coarse, medium, fine
cells = [2964899, 3016520 ]

# Volume of domain. Used to calculate representative size of mesh
volume = 8.085

# # The output of your cfd. Normally you'd use cl or cd, but im using rmse
# # Since that is the variable of interest here. Using total rmse here
# rmse_330 , _ = calc_rmse_mae(x_pos=0.33, case_name='medium')
# rmse_495 , _ = calc_rmse_mae(x_pos=0.495, case_name='medium')
# print(rmse_495 + rmse_330)


solution = [15.343398385604914, 15.305629818890305, ]

gcs = GCS(dimension=2,
        simulation_order=2,
        volume=volume,
        cells=cells,
        solution=[6.063, 5.972, 5.863])

# output information to Markdown-formated table
gcs.print_table(output_type='markdown', output_path='.')

