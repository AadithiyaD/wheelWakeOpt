from pathlib import Path
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
'''
for CFD data ->
col 0 = U:0
col 9 = Y coord (height) => my x2, vertical axis
col 10 = Z coord (cross stream) => my x1, horizontal axis

for expt Data ->
col 0 -> Y coord -> my horizontal axis
col 1 -> Z coord -> my vertical axis
col 2 -> Vx
'''

def plot_contour_filled(x1_raw: np.ndarray, x2_raw: np.ndarray , u_raw: np.ndarray, 
                        plot_title: str,
                        img_save_name: str = 'contourPlot.png',
                        img_save_at: Path = './images/', 
                        show: bool = False, resolution: int = 100) -> None:
    '''
    Plots and saves a contour plot for given input
    '''
    x1_i = np.linspace(np.min(x1_raw), np.max(x1_raw), resolution)
    x2_i = np.linspace(np.min(x2_raw), np.max(x2_raw), resolution)
    x1g, x2g = np.meshgrid(x1_i, x2_i)
    Ug_i = griddata((x1_raw, x2_raw), u_raw, (x1g, x2g), method='linear')
    
    fig, ax = plt.subplots()
    cf = ax.contourf(x1g, x2g, Ug_i, cmap='viridis')
    ax.contour(x1g, x2g, Ug_i, colors='k')
    ax.set_xlim(-0.25309, 0.25309)
    ax.set_ylim(0, 0.1587)
    
    ax.set_xlabel('Cross-stream [m]') 
    ax.set_ylabel('Height [m]')
    fig.colorbar(cf)
    
    if plot_title:
        ax.set_title(f'{plot_title}')
    else:
        ax.set_title('Contour plot')      
    
    plt.savefig(img_save_at / img_save_name)      
    
    if show:
        plt.show()


if __name__ == "__main__":
    data = np.genfromtxt("data/medium/X_0.33.csv", delimiter=",", skip_header=1)

    x1_raw = data[:, 10]
    x2_raw = data[:, 9]
    Ux_raw = data[:, 0]
        
    plot_title = "Contour plot of Ux (m/s) CFD data at X = 0.33, medium grid"
    img_save_name = "Ux_X0.33_medium.png"
    img_save_at = Path('images/medium')
    
    plot_contour_filled(x1_raw=x1_raw, x2_raw=x2_raw, u_raw=Ux_raw,
                        plot_title=plot_title, 
                        img_save_name=img_save_name,
                        img_save_at=img_save_at)