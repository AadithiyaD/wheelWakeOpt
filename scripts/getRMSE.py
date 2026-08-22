# from pyGCS import GCS
from error_calc import calc_rmse
from pathlib import Path
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
import sys
import os

caseName = sys.argv[1] if len(sys.argv) > 1 else "default"
# # Specify as coarse, medium, fine
# cells = [2964899, 3490768, 7204737]

# # Volume of domain. Used to calculate representative size of mesh
# volume = 8.085

# # The output of your cfd. Normally you'd use cl or cd, but im using rmse
# # Since that is the variable of interest here. Using total rmse here
rmse_330 = calc_rmse(x_pos=0.33, case_dir=f'images/{caseName}')
rmse_495 = calc_rmse(x_pos=0.495, case_dir=f'images/{caseName}')
print(rmse_495 + rmse_330)


# solution = [15.3434, 15.3056, 16.9517]

# gcs = GCS(dimension=3,
#         simulation_order=2,
#         volume=volume,
#         cells=cells,
#         solution=solution)

# # output information to Markdown-formated table
# gcs.print_table(output_type='markdown', output_path='.')

