#!/bin/sh

# rm -rf constant/polyMesh 
rm -rf log.*
rm -rf 1/
rm -rf 2/
rm -rf 3/
rm -rf processor*/1/      # Castellated mesh
rm -rf processor*/2/      # Snapped mesh
rm -rf processor*/3/        # Mesh with layers

# blockMesh | tee log.blockMesh

# decomposePar | tee log.decomposeParMesh

mpirun -np 4 snappyHexMesh -parallel | tee log.snappyHexMesh

reconstructParMesh -time 3
reconstructPar -time 3    

checkMesh -allGeometry -allTopology -latestTime -writeAllFields -writeSets vtk | tee log.checkMesh
