from error_calc import calc_rmse
import sys
import os
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
import numpy as np
from pathlib import Path


caseName = sys.argv[1] if len(sys.argv) > 1 else "default"

# ===================== NOTE ===================================
# This gci script calculates U_{95%}, not u_{num}
# ===================== NOTE ====================================

# ============================ USER INPUT =======================
# List values for phi_1, phi_2, phi_3
solutionList = [15.3434, 15.3056, 16.9517]

# Factor of safety for GCI. Use 3 if using unstructured grid refinement
# 1.25 otherwise
Fs = 3

# Fixed point iterations and convergence tolerance
fixedPointIterations = 1000
fixedPointConvergenceTol = 1e-6
# ============================ USER INPUT ========================

# ============================ ACTUAL CALCULATION ================
# Dict maps: meshNumber -> h_{number}
meshNameDict = {
    "1": 0,
    "2": 0,
    "3": 0
}

# Step 1 - Calculate representative mesh size h
for meshName,h in meshNameDict.items():
    VList = ParsedParameterFile(
        Path(f"/home/durai/OpenFOAM/durai-v2506/run/wheelWakeOpt/forGCI/V{meshName}"),
        treatBinaryAsASCII=True,
    )
    V = VList["internalField"]
    hNew=(sum(V)/len(V))**(1/3)
    meshNameDict[meshName] = hNew

# Step 2 - Select three sets of grids, with a refinement factor r and get the desired result variable phi .
# Recommended to have r > 1.3

# Step 3 - Let h1 < h2 < h3, and r21 = h2/h1. Calculate p
r_21 = meshNameDict["2"]/meshNameDict["1"]
r_32 = meshNameDict["3"]/meshNameDict["1"]

phi_1 = solutionList[0]
phi_2 = solutionList[1]
phi_3 = solutionList[2]

epsilon_21 = phi_2 - phi_1
epsilon_32 = phi_3 - phi_2

## Solve equations simulataneously for p, using fixed point iteration
s = 1 * np.sign(epsilon_32 / epsilon_21)

### Initial assumption is q(p) = 0
qP = 0
p  = 0

for _ in range(fixedPointIterations):
    p_new = (1/np.log(r_21))*(np.log(abs(epsilon_32 - epsilon_21)) + qP)
    qP_new = np.log((r_21**p_new - s)/(r_32**p_new - s))
    
    ### Break loop if p has converged
    if abs(p_new - p) < fixedPointConvergenceTol:
        p = p_new
        break
    
    ### Update p and qP and proceed to next iteration
    p = p_new
    qP = qP_new
    
# Step 4 - Calculate extrapolated values
phi_21_ex = (((r_21**p)*phi_1) - phi_2)/((r_21**p) - 1)
phi_32_ex = (((r_32**p)*phi_1) - phi_2)/((r_32**p) - 1)

# Step 5 - Calculate and report the following error estimates along with 
# observed order of the method p
if phi_1 == 0:
    e_21_a = abs(phi_1 - phi_2)
    e_32_a = abs(phi_2 - phi_3)
else:
    e_21_a = abs((phi_1 - phi_2) / phi_1)
    e_32_a = abs((phi_2 - phi_3) / phi_2)

## Estimated extrapolated relative error
e_21_ext = abs((phi_21_ex - phi_1)/phi_21_ex)
e_32_ext = abs((phi_32_ex - phi_1)/phi_32_ex)

## Grid convergence index
gci_21 = (Fs * e_21_a)/((r_21**p) - 1)
gci_32 = (Fs * e_32_a)/((r_32**p) - 1)

# Print out estimates
print(f"Refinement factor r_21 = {r_21:.4f}")
print(f"Refinement factor r_32 = {r_32:.4f}")
print(f"Extrapolated relative error e_21_ext = {e_21_ext:.4f}")
print(f"Grid convergence index GCI_21 = {gci_21:.4f}")
print(f"Extrapolated relative error e_32_ext = {e_32_ext:.4f}")
print(f"Grid convergence index GCI_32 = {gci_32:.4f}")

# ============================ ACTUAL CALCULATION ============================
