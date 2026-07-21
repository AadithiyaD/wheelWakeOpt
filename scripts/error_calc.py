from pathlib import Path
import numpy as np
from scipy.interpolate import griddata

def calc_rmse(x_pos: float, case_dir) -> np.float64:
    '''
    Calculates Root Mean Square Error. Specify
    X position as float
    ex: x_pos = 0.33 will look at data for the plane at X = 330mm
    '''
    
    trialPath = Path(case_dir).resolve()
    cfdData  = np.genfromtxt(trialPath / f'X_{x_pos}.csv', delimiter=",", skip_header=1)
    exptDataPath = Path("./data/")
    exptData = np.genfromtxt(exptDataPath / 'experimental' / f'X{int(x_pos * 1000)}mm_Mean.csv', delimiter=",", skip_header=9)

    # Load CFD data
    x1_raw = cfdData[:, 10]
    x2_raw = cfdData[:, 9]
    Ux_raw = cfdData[:, 0]

    # Load experimental data
    x1e_raw = exptData[:, 0]
    # Add to shift reference point down
    x2e_raw = exptData[:, 1] + 0.1587 
    # Clip so that the few small negative values (created due to floating point addn) get set to 0
    x2e_raw = np.clip(x2e_raw, 0, None) 
    Uxe_raw = exptData[:, 2]

    # Interpolate and evaluate CFD data on the same points as experimental data
    Ug_i = griddata((x1_raw, x2_raw), Ux_raw, (x1e_raw, x2e_raw), method='linear')

    # Calculate root mean square and mean absolute error
    rmse = np.sqrt(np.mean((Uxe_raw - Ug_i) ** 2))
    
    return rmse