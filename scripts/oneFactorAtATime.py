import os

from helperFuncs import *

TRIAL_VALUES = [
    {'coeff': 'a1', 'value': 0.248, 'rmse': 0.0},
    {'coeff': 'a1', 'value': 0.279, 'rmse': 0.0},
    {'coeff': 'a1', 'value': 0.341, 'rmse': 0.0},
    {'coeff': 'a1', 'value': 0.372, 'rmse': 0.0},

    {'coeff': 'betaStar', 'value': 0.072, 'rmse': 0.0},
    {'coeff': 'betaStar', 'value': 0.081, 'rmse': 0.0},
    {'coeff': 'betaStar', 'value': 0.099, 'rmse': 0.0},
    {'coeff': 'betaStar', 'value': 0.108, 'rmse': 0.0},

    # alphaK1 ==> sigmaK1 in the model, alphaK2 ==> sigmaK2
    {'coeff': 'alphaK1', 'value': 0.68, 'rmse': 0.0},
    {'coeff': 'alphaK1', 'value': 0.765, 'rmse': 0.0},
    {'coeff': 'alphaK1', 'value': 0.935, 'rmse': 0.0},
    {'coeff': 'alphaK1', 'value': 1.02, 'rmse': 0.0},

    {'coeff': 'alphaK2', 'value': 0.8, 'rmse': 0.0},
    {'coeff': 'alphaK2', 'value': 0.9, 'rmse': 0.0},
    {'coeff': 'alphaK2', 'value': 1.1, 'rmse': 0.0},
    {'coeff': 'alphaK2', 'value': 1.2, 'rmse': 0.0},

    # alphaOmega1 ==> sigmaOmega1, alphaOmega2 ==> sigmaOmega2
    {'coeff': 'alphaOmega1', 'value': 0.4, 'rmse': 0.0},
    {'coeff': 'alphaOmega1', 'value': 0.45, 'rmse': 0.0},
    {'coeff': 'alphaOmega1', 'value': 0.55, 'rmse': 0.0},
    {'coeff': 'alphaOmega1', 'value': 0.6, 'rmse': 0.0},

    {'coeff': 'alphaOmega2', 'value': 0.6848, 'rmse': 0.0},
    {'coeff': 'alphaOmega2', 'value': 0.7704, 'rmse': 0.0},
    {'coeff': 'alphaOmega2', 'value': 0.9416, 'rmse': 0.0},
    {'coeff': 'alphaOmega2', 'value': 1.0272, 'rmse': 0.0},
]

for entry in TRIAL_VALUES:
    coeff = entry['coeff']
    coeffValue = entry['value']
    
    # Setup and execute trial
    trialName = f"{coeff}_{coeffValue}"
    print(f"Setting up trial: {trialName}")
    setupTrial(trialName, coeffName=coeff, coeffValue=coeffValue)
    executeCase(trialName)

    # Now to calculate rmse
    exptData_330mm = loadExptData(pos=330, normal = "X")
    exptData_330mm = smoothData(exptData_330mm)
    exptData_495mm = loadExptData(pos=495, normal = "X")
    exptData_495mm = smoothData(exptData_495mm)
    
    cfd_330mm = pd.read_csv(Path("cases") / trialName / "X_0.33.csv")
    cfd_495mm = pd.read_csv(Path("cases") / trialName / "X_0.495.csv")
    
    rmse_330, interpolatedVelocityField_330 = computeRmse(exptData=exptData_330mm, cfdData=cfd_330mm)
    rmse_495, interpolatedVelocityField_495 = computeRmse(exptData=exptData_495mm, cfdData=cfd_495mm) 
    totalRmse = rmse_330 + rmse_495
    
    # Update TRIAL_VALUES dict
    entry['rmse'] = totalRmse
    
    print(f"For trial {trialName} total RMSE = {totalRmse}")
    
    # Write out to csv to save values
    pd.DataFrame(TRIAL_VALUES).to_csv('./data/oneFactorAtATime_results.csv', index=False)
    
    # Plot contours
    imgDir = Path("./images")
    os.makedirs(imgDir/ trialName, exist_ok=True)
    plotContourComparison(exptData=exptData_330mm,
                        cfdData=cfd_330mm,
                        plotTitle="Contour velocity comparison",
                        imgName=f"{trialName}/uxComparison_0.33_{trialName}.png")
    plotContourComparison(exptData=exptData_495mm,
                            cfdData=cfd_495mm,
                            plotTitle="Contour velocity comparison",
                            imgName=f"{trialName}/uxComparison_0.495_{trialName}.png")
    
    plotErrorContour(exptData=exptData_330mm,
                    cfdInterpolated=interpolatedVelocityField_330,
                    plotTitle= "Ux Velocity absolute error distribution",
                    imgName=f"{trialName}/errorDist_0.33_{trialName}.png")
    plotErrorContour(exptData=exptData_495mm,
                        cfdInterpolated=interpolatedVelocityField_495,
                        plotTitle= "Ux Velocity absolute error distribution",
                        imgName=f"{trialName}/errorDist_0.495_{trialName}.png")