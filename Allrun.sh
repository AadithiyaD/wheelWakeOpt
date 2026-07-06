#!/bin/sh
cd "${0%/*}" || exit                                # Run from this directory
. ${WM_PROJECT_DIR:?}/bin/tools/RunFunctions        # Tutorial run functions
#------------------------------------------------------------------------------

./Allclean

decompDict="-decomposeParDict system/decomposeParDict"

blockMesh | tee log.blockMesh

decomposePar | tee log.decomposeParMesh

mpirun -np 4 snappyHexMesh -parallel | tee log.snappyHexMesh

reconstructParMesh -time 3
reconstructPar -time 3    

checkMesh -allGeometry -allTopology -latestTime -writeAllFields -writeSets vtk | tee log.checkMesh

rm -rf constant/polyMesh
mv 3/polyMesh constant/
rm -rf 3/

rm -rf processor*
# rm -rf log.*

restore0Dir

decomposePar

runParallel $decompDict potentialFoam -writephi

runParallel $decompDict $(getApplication)

# For reference, the actual parallel command
# mpirun -np 4 simpleFoam -parallel

runApplication reconstructPar -latestTime

./residuals.sh

pvpython extractPlaneInfo.py