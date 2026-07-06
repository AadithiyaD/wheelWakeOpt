import csv
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata

dataPath = Path("./data/")
data = np.genfromtxt("data/coarse/X_0.33.csv", delimiter=",", skip_header=1)
exptData = np.genfromtxt("data/experimental/X330mm_Mean.csv", delimiter=",")

print(exptData[0])

'''
col 0 = U:0
col 9 = Y coord (height) => my x2, vertical axis
col 10 = Z coord (cross stream) => my x1, horizontal axis
'''
resolution = 100
x1_raw, x2_raw, Ux_raw = data[:, 10], data[:, 9], data[:, 0]
x1_i = np.linspace(np.min(x1_raw), np.max(x1_raw), resolution)
x2_i = np.linspace(np.min(x2_raw), np.max(x2_raw), resolution)
x1g, x2g = np.meshgrid(x1_i, x2_i)

Ug_i = griddata((x1_raw, x2_raw), Ux_raw, (x1g, x2g), method='linear')

# fig, ax = plt.subplots()
# cf = ax.contourf(x1g, x2g, Ug_i, levels=8, cmap='viridis')
# ax.contour(x1g, x2g, Ug_i, colors='k')
# ax.plot(x1_raw, x2_raw, 'x', color='k', markersize=5)
# ax.set_xlabel('Cross-stream [m]') 
# ax.set_ylabel('Height [m]')
# fig.colorbar(cf)
# ax.set_title('Contour plot of Ux (m/s) at x=0.33m')      
# plt.savefig("Ux_X0.33_coarse.png")      
# plt.show()
            
            
