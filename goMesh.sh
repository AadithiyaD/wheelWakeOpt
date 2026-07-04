#!/bin/sh

rm -rf log.*
rm -rf 3/
rm -rf processor*/3/

# blockMesh | tee log.blockMesh

# decomposePar | tee log.decomposeParMesh

mpirun -np 4 snappyHexMesh -parallel | tee log.snappyHexMesh

# reconstructParMesh -time 1 # Reconstruct the castellated mesh
# reconstructParMesh -time 2 # Reconstruct the snapped mesh
reconstructParMesh -time 3 # Reconstruct the mesh after layer addition
reconstructPar -time 3     # Reconstruct layerFields

# Check the latest mesh and write out problematic zones for viz in paraview
checkMesh -allGeometry -allTopology -latestTime -writeAllFields -writeSets vtk | tee log.checkMesh
# checkMesh -allGeometry -allTopology -latestTime

rm -rf constant/polyMesh 
mv 3/polyMesh constant/
rm -rf 3/ 


