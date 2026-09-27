from pathlib import Path
import numpy as np
import pandas as pd
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

import os
import shutil
from subprocess import Popen, DEVNULL
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

from centralControl import NPROC, PVPYTHON_SCRIPT

'''
for expt Data ->
col 0 -> Y coord -> horizontal axis
col 1 -> Z coord -> vertical axis
col 2 -> Vx
'''

# skip the bottom 0.02m of measurements due to some funkiness in the PIV measurements
# Bound the cross stream to exclude the wake of the wheel support structure 
ROW_SKIP = 0.02
COL_EXTENT = 0.21

IMG_DIR = Path('./images/')

def loadExptData(pos: int, normal: str,
                rowSkip = ROW_SKIP, colExtent = COL_EXTENT):
    '''
    Load and return expt data as dataframe. 
    `pos` is specified in mm. ex: `330` for 330mm position
    `normal` refers to the normal vector of the measurement plane
    '''
    exptDirPath = Path("data/experimental")
    df = pd.read_csv(
        Path( exptDirPath / f"{normal}{pos}mm_Mean.csv"),
        skiprows=8,
        sep=r'\s*,\s*',
        encoding='utf-8',
        engine='python'
    )
    
    # Make the z coordinate positive for convenience
    df['z'] = df['z'] + 0.15871

    exclusionMask = np.zeros(len(df), dtype=bool)
    exclusionMask = (df['z'] < rowSkip) | ~df['y'].between(-colExtent,colExtent)
    
    return df[~exclusionMask].reset_index(drop=True)


def plotContour(x1: np.ndarray, x2: np.ndarray, u: np.ndarray,
                plotTitle: str = "Contour Plot",
                imgName: str = 'contourPlot.png',
                show: bool = False, resolution:int = 100):
    '''
    Plots a 2D contour plot for given input
    '''
    # x1_i = np.linspace(np.min(x1), np.max(x1), resolution)
    # x2_i = np.linspace(np.min(x2), np.max(x2), resolution)
    # x1g, x2g = np.meshgrid(x1_i, x2_i)
    # Ug_i = griddata((x1, x2), u, (x1g, x2g), method='linear')
    
    vmin = -10
    vmax = 32
    levels = np.linspace(vmin, vmax, 10)
    
    #? Is there a downside to using tricountour over contour here?
    fig, ax = plt.subplots()
    # cf = ax.contourf(x1g, x2g, Ug_i, levels=levels, cmap='viridis', extend='both')
    # ax.contour(x1g, x2g, Ug_i, levels=levels, colors='k', linewidths=0.5)
    cf = ax.tricontourf(x1, x2, u, levels=levels, cmap='viridis', extend='both')
    ax.tricontour(x1, x2, u, levels=levels, colors='k', linewidths=0.5)
    
    # I just manually arrived at these limits
    ax.set_xlim(-0.2, 0.2)
    ax.set_ylim(0.02179, 0.16)
    
    ax.set_xlabel('Cross-stream [m]')
    ax.set_ylabel('Height [m]')
    fig.colorbar(cf)

    ax.set_title(f'{plotTitle}') 
    plt.savefig(IMG_DIR / imgName)      
    
    if show:
        plt.show()

def plotContourComparison(exptData: pd.DataFrame, cfdData: pd.DataFrame,
                        plotTitle: str = "Contour Velocity Plot Comparison",
                        imgName: str = 'contourPlotComparison.png',
                        show: bool = False):
    '''
    Creates a side by side comparsion of the contour plots for the given 
    CFD run and experimental data
    '''
    vmin = -10
    vmax = 32
    levels = np.linspace(vmin, vmax, 10)
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True, sharey=True)
    
    cf0 = axes[0].tricontourf(cfdData['Points:2'], cfdData['Points:1'], cfdData['U:0'], levels=levels, cmap='viridis', extend='both')
    axes[0].tricontour(cfdData['Points:2'], cfdData['Points:1'], cfdData['U:0'], levels=levels, colors='k', linewidths=0.5)
    axes[0].set_title('CFD Data')
    axes[0].set_xlabel('Cross-stream [m]')
    axes[0].set_ylabel('Height [m]')
    
    cf1 = axes[1].tricontourf(exptData['y'], exptData['z'], exptData['Vx'], levels=levels, cmap='viridis', extend='both')
    axes[1].tricontour(exptData['y'], exptData['z'], exptData['Vx'], levels=levels, colors='k', linewidths=0.5)
    axes[1].set_title('Experimental Data')
    axes[1].set_xlabel('Cross-stream [m]')
    axes[1].set_ylabel('Height [m]')

    axes[0].set_xlim(-0.2, 0.2)
    axes[0].set_ylim(0.02179, 0.16)
    
    fig.colorbar(cf1, ax=axes, orientation='vertical', label='Ux Velocity [m/s]')
    fig.suptitle(f'{plotTitle}')
    fig.savefig(IMG_DIR / imgName)
    
    if show:
        plt.show()  

def computeRmse(exptData: pd.DataFrame, cfdData: pd.DataFrame):
    '''
    Calculates Root Mean Square Error by interpolating CFD data onto expt grid
    and evaluating. Return the interpolated velocity field which can be used in 
    plotting the error distribution contour
    '''
    # Load CFD Data
    x1_cfd = cfdData['Points:2'].to_numpy()
    x2_cfd = cfdData['Points:1'].to_numpy()
    ux_cfd = cfdData['U:0'].to_numpy()
    
    # Load Experimental Data
    x1_expt = exptData['y'].to_numpy()
    x2_expt = exptData['z'].to_numpy()
    ux_expt = exptData['Vx'].to_numpy()
    
    ug_i = griddata(
        points=(x1_cfd, x2_cfd),
        values=ux_cfd,
        xi=(x1_expt, x2_expt),
        method='linear'
    )
    
    rmse = np.sqrt(np.mean((ux_expt - ug_i) ** 2))
    
    return rmse, ug_i

def plotErrorContour(exptData: pd.DataFrame, cfdInterpolated: np.ndarray,
                    plotTitle: str = "Velocity absolute error distribution",
                    imgName: str = 'errorDistPlot.png',
                    show: bool = False):
    '''
    Plots the spatial variation of absolute error of velocity
    '''
    exptData['abs_error'] = np.abs(exptData['Vx'].to_numpy() - cfdInterpolated)
    
    levels = np.linspace(0, exptData['abs_error'].max(), 10)
    
    x1 = exptData['y']
    x2 = exptData['z']
    
    fig, ax = plt.subplots()
    cf = ax.tricontourf(x1, x2, exptData['abs_error'], levels=levels, cmap='magma', extend='both')
    ax.tricontour(x1, x2, exptData['abs_error'], levels=levels, colors='k', linewidths=0.5)

    ax.set_xlim(-0.2, 0.2)
    ax.set_ylim(0.02179, 0.16)
    
    ax.set_xlabel('Cross-stream [m]')
    ax.set_ylabel('Height [m]')
    fig.colorbar(cf)

    ax.set_title(f'{plotTitle}') 
    plt.savefig(IMG_DIR / imgName)      
    
    if show:
        plt.show()

def setupTrial(trialName: str, trialDir: Path = Path("./cases"), coeffName: str | None = None,
            coeffValue: float | None = None, customCoeffs: dict | None = None):
    '''
    Sets up a case with the specified turbulence coefficient variation.
    If `customCoeffs` is provided, it will override the default coefficients with
    the provided values. Providen `customCoeffs` as ex: `{'betaStar': 0.09, 'sigmaOmega1': 0.5, 'sigmaOmega2': 0.856} `
    Otherwise, it will use `coeffName` and `coeffValue` to set a single coefficient variation.
    '''
    
    trialPath = trialDir / trialName
    
    # Remove the trial directory if it exists and create a new one
    os.makedirs(trialPath, exist_ok=True)
    shutil.rmtree(trialPath, ignore_errors=True)
    os.makedirs(trialPath, exist_ok=True)

    # Copy the base case folders into the trial directory
    for folder in ["0", "constant", "system"]:
        shutil.copytree(
            src=folder,
            dst=os.path.join(trialPath, folder),
            dirs_exist_ok=True,
        )

    # Parse the turbulenceProperties file and update the coefficients
    turbProps = ParsedParameterFile(
        os.path.join(trialPath, "constant", "turbulenceProperties"),
        treatBinaryAsASCII=True,
    )
    caseCoeffsDict = turbProps["RAS"]["kOmegaSSTCoeffs"]

    if customCoeffs is not None:
        for param_name, param_value in customCoeffs.items():
            caseCoeffsDict[param_name] = param_value
    else:
        if coeffName is None or coeffValue is None:
            raise ValueError("coeffName and coeffValue are required when customCoeffs is not provided")
        caseCoeffsDict[coeffName] = coeffValue

    turbProps.writeFile()
    print(f"Trial {trialName} setup complete with coefficients: {customCoeffs if customCoeffs else {coeffName: coeffValue}}")
    

def executeCase(trialName: str, trialDir: Path = Path("./cases")):
    '''
    Executes the OpenFOAM case in the specified trial directory and postprocesses results.
    Raises RuntimeError if any of the subprocesses fail.
    '''
    
    trialPath = trialDir / trialName
    
    # Decompose the case for parallel execution
    decompose = Popen(
        [f"decomposePar -case {os.path.normpath(trialPath)}"],
        stdin=DEVNULL,
        stdout=DEVNULL,
        shell=True,
    )
    decompose.wait()

    if decompose.returncode != 0:
        raise RuntimeError(f"decomposePar failed for {trialPath}")

    # Execute simplefoam
    simpleFoam = Popen(
        [f"pyFoamRunner.py --procnr={NPROC} simpleFoam -case {os.path.normpath(trialPath)}"],
        stdin=DEVNULL,
        stdout=DEVNULL,
        shell=True,
    )
    simpleFoam.wait()

    if simpleFoam.returncode != 0:
        raise RuntimeError(f"simpleFoam failed for {trialPath}")

    # Reconstruct the case after parallel execution
    reconstruct = Popen(
        [f"reconstructPar -case {os.path.normpath(trialPath)} -latestTime"],
        stdin=DEVNULL,
        stdout=DEVNULL,
        shell=True,
    )
    reconstruct.wait()

    if reconstruct.returncode != 0:
        raise RuntimeError(f"reconstructPar failed for {trialPath}")

    # Run paraview and get velocity data
    pvpython = Popen(
        [f"pvpython {PVPYTHON_SCRIPT} {os.path.normpath(trialPath)}"],
        stdin=DEVNULL,
        stdout=DEVNULL,
        shell=True,
    )
    pvpython.wait()

    if pvpython.returncode != 0:
        raise RuntimeError(f"pvpython failed for {trialPath}")

    print(f"Trial {trialName} executed successfully.")

    return None

if __name__ == "__main__":
    exptData = loadExptData(pos=330, normal="X")
        
    # plotContour(x1=exptData['y'].to_numpy(),
    #             x2=exptData['z'].to_numpy(),
    #             u=exptData['Vx'].to_numpy())
    
    # plotContourComparison(exptData=exptData,
    #                       cfdData=pd.read_csv("data/medium/X_0.33.csv"))
    
    # rmse, cfdInterpolated = computeRmse(exptData=exptData,
    #                     cfdData=pd.read_csv("data/medium/X_0.33.csv"))

    # plotErrorContour(exptData=exptData,
    #                 cfdInterpolated=cfdInterpolated, show=True)
    
    