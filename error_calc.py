from pathlib import Path
import numpy as np
from scipy.interpolate import griddata

def calc_rmse_mae(x_pos: float, case_name: str):
    '''
    Calculates Root Mean Square and Mean Absolute Error. Specify
    X position as float
    ex: x_pos = 0.33 will look at data for the plane at X = 330mm
    '''
    
    data_Path = Path("./data/")
    cfdData  = np.genfromtxt(data_Path / f'{case_name}' / f'X_{x_pos}.csv', delimiter=",", skip_header=1)
    exptData = np.genfromtxt(data_Path / 'experimental' / f'X{int(x_pos * 1000)}mm_Mean.csv', delimiter=",", skip_header=9)

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
    mae  = np.mean(np.absolute(Uxe_raw - Ug_i))
    
    return rmse, mae