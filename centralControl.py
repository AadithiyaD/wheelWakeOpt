"""Central configuration script. Make changes here, execute this file, and then run 
bayesOpt.py
"""

from ax.api.configs import RangeParameterConfig
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
import os

# Ax experiment setup
MAX_TRIALS = 6
PARALLEL_RUNS = 1 # 1 => serial
FAILURE_TOLERANCE = 0.3 # 0.3 => exception raised if 30% of trials fail
TIME_BW_POLLS = 50     # In seconds

# Max number of simpleFoam iterations
MAX_ITER = 4000

# Number of intervals to wait before writing out data
write_control = 1000

# Number of processors for each trial
NPROC = 6

# Define parameters
A1_COEFF = RangeParameterConfig(name="a1", parameter_type="float", 
                        bounds=(0.155, 0.465))
BETASTAR = RangeParameterConfig(name="betaStar", parameter_type="float", 
                                bounds=(0.045, 0.135))

# x/H positions
# X_BY_H=[1,4,6,10]

# Data comparison locations
X_POS = [0.33, 0.495]
Y_POS = [0, 50]

# Script locations
PVPYTHON_SCRIPT = "/home/durai/OpenFOAM/durai-v2506/run/wheelWakeOpt/scripts/extractPlaneInfo.py"


# ===============================================================================
# Dict modification
decomposeParDict = ParsedParameterFile(
        os.path.join('system', 'decomposeParDict'),
        treatBinaryAsASCII=True
)
decomposeParDict['numberOfSubdomains'] = NPROC
decomposeParDict.writeFile()

controlDict = ParsedParameterFile(
        os.path.join('system', 'controlDict'),
        treatBinaryAsASCII=True
        )

controlDict['endTime'] = MAX_ITER
controlDict['writeInterval'] = write_control
controlDict.writeFile()
