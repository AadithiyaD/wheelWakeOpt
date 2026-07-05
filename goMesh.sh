#!/bin/sh

rm -rf log.*
rm -rf 3/
rm -rf processor*
rm -rf constant/polyMesh

blockMesh | tee log.blockMesh

decomposePar | tee log.decomposeParMesh

mpirun -np 10 snappyHexMesh -parallel | tee log.snappyHexMesh

reconstructParMesh -time 3 

# Check the latest mesh and write out problematic zones for viz in paraview
checkMesh -allGeometry -allTopology -latestTime | tee log.checkMesh
# checkMesh -allGeometry -allTopology -latestTime

rm -rf constant/polyMesh 
mv 3/polyMesh constant/
rm -rf 3/ 


