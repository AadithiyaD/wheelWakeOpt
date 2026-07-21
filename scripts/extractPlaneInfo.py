from paraview.simple import *
import sys
import os

trialDir = sys.argv[1] if len(sys.argv) > 1 else "default"
trialName = os.path.basename(trialDir)

trialFoam = OpenFOAMReader(registrationName=f'{trialName}.foam', FileName=f'/home/durai/OpenFOAM/durai-v2506/run/wheelWakeOpt/{trialDir}/{trialName}.foam')

reflect1 = Reflect(registrationName='Reflect1', Input=trialFoam)

reflect1.Plane = 'Z Min'

mergeBlocks1 = MergeBlocks(registrationName='MergeBlocks1', Input=reflect1)

cellDataConv = CellDatatoPointData(registrationName='CellDataConv', Input=mergeBlocks1)

clip1 = Clip(registrationName='Clip1', Input=cellDataConv)
clip1.ClipType = 'Box'
clip1.ClipType.Set(
    Position=[-0.1773358746750433, 0.0, -0.32172407634908295],
    Length=[2.651978071707739, 0.44184059919153773, 0.6297090114081989],
)

slice1 = Slice(registrationName='Slice1', Input=clip1)
slice1.SliceType.Origin = [0.33, 0.0, 0.0]

slice1.UpdatePipeline()

SaveData(f'/home/durai/OpenFOAM/durai-v2506/run/wheelWakeOpt/{trialDir}/X_0.33.csv', proxy=slice1, PointDataArrays=['U', 'UNear', 'k', 'nut', 'omega', 'p'],
    FieldDataArrays=['CasePath'])

slice2 = Slice(registrationName='Slice2', Input=clip1)
slice2.SliceType.Origin = [0.495, 0.0, 0.0]

slice2.UpdatePipeline()

SaveData(f'/home/durai/OpenFOAM/durai-v2506/run/wheelWakeOpt/{trialDir}/X_0.495.csv', proxy=slice2, PointDataArrays=['U', 'UNear', 'k', 'nut', 'omega', 'p'],
    FieldDataArrays=['CasePath'])