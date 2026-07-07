import csv
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata

dataPath = Path("./data/")
imgPath = Path("./images/")
data = np.genfromtxt("data/coarse/X_0.33.csv", delimiter=",", skip_header=1)
exptData = np.genfromtxt("data/experimental/X330mm_Mean.csv", delimiter=",")

print(exptData[0])

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
# Plot contour for expt data
resolution = 100
x1e_raw, x2e_raw, Uxe_raw = exptData[:, 0], exptData[:, 1], exptData[:, 2]
x1e_i = np.linspace(np.min(x1e_raw), np.max(x1e_raw), resolution)
x2e_i = np.linspace(np.min(x2e_raw), np.max(x2e_raw), resolution)
x1e_g, x2e_g = np.meshgrid(x1e_i, x2e_i)

Uge_i = griddata((x1e_raw, x2e_raw), Uxe_raw, (x1e_g, x2e_g), method='linear')        

fig, ax = plt.subplots()
ax.contour(x1e_g, x2e_g, Uge_i, colors='k')
cfe = ax.contourf(x1e_g, x2e_g, Uge_i, cmap='viridis')

# # ax.plot(x1e_raw, x2e_raw, 'x', color='k', markersize=5)
# ax.set_xlabel('Cross-stream [m]') 
# ax.set_ylabel('Height [m]')
# fig.colorbar(cfe)
# ax.set_title('Contour plot of expt data of Ux (m/s) at x=0.33m')      
# plt.savefig(imgPath / "experimental"/ "Ux_X0.33_expt_linear.png")      
# plt.show()

# Plot contour for CFD data
x1_raw, x2_raw, Ux_raw = data[:, 10], data[:, 9], data[:, 0]
x1_i = np.linspace(np.min(x1_raw), np.max(x1_raw), resolution)
x2_i = np.linspace(np.min(x2_raw), np.max(x2_raw), resolution)
x1g, x2g = np.meshgrid(x1_i, x2_i)

Ug_i = griddata((x1_raw, x2_raw), Ux_raw, (x1g, x2g), method='linear')

# Evaluate interpolation on the experimental grid to compare with expt data
#* Use this to calc RMSE. It is 1D array of (15502,) shape, same as Uxe_raw
#* But can this be used to plot contour on expt grid?
# Ug_i = griddata((x1_raw, x2_raw), Ux_raw, (x1e_raw, x2e_raw), method='linear')

fig, ax = plt.subplots()
cf = ax.contourf(x1g, x2g, Ug_i, cmap='viridis')
ax.contour(x1g, x2g, Ug_i, colors='k')
ax.plot(x1_raw, x2_raw, 'x', color='k', markersize=5)
ax.set_xlabel('Cross-stream [m]') 
ax.set_ylabel('Height [m]')
fig.colorbar(cf)
ax.set_title('Contour plot of Ux (m/s) at x=0.33m')      
plt.savefig(imgPath / "coarse" / "Ux_X0.33_coarse.png")      
plt.show()