#!/bin/sh
cd "${0%/*}" || exit                                # Run from this directory
. ${WM_PROJECT_DIR:?}/bin/tools/RunFunctions        # Tutorial run functions
#------------------------------------------------------------------------------
rm -rf 0/
rm -rf processor*
# rm -rf log.*

decompDict="-decomposeParDict system/decomposeParDict"

restore0Dir

decomposePar

runParallel $decompDict potentialFoam -writephi

runParallel $decompDict $(getApplication)

# For reference, the actual parallel command
# mpirun -np 4 simpleFoam -parallel

runApplication reconstructPar -latestTime

./residuals.sh