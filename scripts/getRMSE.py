# from pyGCS import GCS
from error_calc import calc_rmse
from pathlib import Path
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
import sys
import os

# Used this for my manual runs

caseName = sys.argv[1] if len(sys.argv) > 1 else "default"

rmse_330 = calc_rmse(x_pos=0.33, case_dir=f'images/{caseName}')
rmse_495 = calc_rmse(x_pos=0.495, case_dir=f'images/{caseName}')
print(rmse_495 + rmse_330)
