from error_calc import calc_rmse
from pathlib import Path
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
import sys
import os

from helperFuncs import *

# Used this for my manual runs

# caseName = sys.argv[1] if len(sys.argv) > 1 else "default"

# rmse_330 = calc_rmse(x_pos=0.33, case_dir=f'images/{caseName}')
# rmse_495 = calc_rmse(x_pos=0.495, case_dir=f'images/{caseName}')
# print(rmse_495 + rmse_330)


# ----------
exptData_330mm = loadExptData(pos=330, normal = "X")
exptData_495mm = loadExptData(pos=495, normal = "X")

cfdCaseName = sys.argv[1] if len(sys.argv) > 1 else "default"

cfd_330mm = pd.read_csv((Path("images") / cfdCaseName / "X_0.33.csv"))
cfd_495mm = pd.read_csv((Path("images") / cfdCaseName / "X_0.495.csv"))

rmse_330, _ = computeRmse(exptData=exptData_330mm, cfdData=cfd_330mm)
rmse_495, _ = computeRmse(exptData=exptData_495mm, cfdData=cfd_495mm) 

print(rmse_330 + rmse_495)