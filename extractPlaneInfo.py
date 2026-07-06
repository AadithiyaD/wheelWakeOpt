from paraview.simple import *

wheelwakeoptfoam = OpenFOAMReader(registrationName='wheelWakeOpt.foam', FileName='/home/durai/OpenFOAM/durai-v2506/run/wheelWakeOpt/wheelWakeOpt.foam')

mergeBlocks1 = MergeBlocks(registrationName='MergeBlocks1', Input=wheelwakeoptfoam)

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

SaveData('/home/durai/OpenFOAM/durai-v2506/run/wheelWakeOpt/sliceExpo.csv', proxy=slice1, PointDataArrays=['U', 'UNear', 'k', 'nut', 'omega', 'p'],
    FieldDataArrays=['CasePath'])