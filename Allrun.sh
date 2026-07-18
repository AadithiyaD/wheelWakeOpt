#!/bin/sh
cd "${0%/*}" || exit                                # Run from this directory
. ${WM_PROJECT_DIR:?}/bin/tools/RunFunctions        # Tutorial run functions
#------------------------------------------------------------------------------

CASE_NAME="medium"

./Allclean

decompDict="-decomposeParDict system/decomposeParDict"

# ============ Create mesh =========================================================================
blockMesh | tee log.blockMesh

decomposePar | tee log.decomposeParMesh

# mpirun -np 4 snappyHexMesh -parallel | tee log.snappyHexMesh
runParallel snappyHexMesh -overwrite

# reconstructParMesh -time 3
# reconstructPar -time 3    

# checkMesh -allGeometry -allTopology -latestTime -writeAllFields -writeSets vtk | tee log.checkMesh
# checkMesh -allGeometry -allTopology -parallel -writeAllFields -writeSets vtk | tee log.checkMesh
# ==================================================================================================

# rm -rf constant/polyMesh
# mv 3/polyMesh constant/
# rm -rf 3/

# rm -rf processor*
# rm -rf log.*

# ============== Solve =============================
# restore0Dir
restore0Dir -processor

# decomposePar

runParallel $decompDict potentialFoam -writephi

runParallel $decompDict $(getApplication)

# For reference, the actual parallel command
# mpirun -np 4 simpleFoam -parallel
# ==================================================

# ====== Reconstruct and post-process ===========================================================
runApplication reconstructParMesh -constant
runApplication reconstructPar -latestTime

./residuals.sh # Technically not needed since im using graphObject, but i just want to use this

# TODO: compress all of postData and mesh for tracking, move into data folder

touch wheelWakeOpt.foam

mkdir images/$CASE_NAME

pvpython extractPlaneInfo.py "$CASE_NAME"

# python3 contourPlot.py "$CASE_NAME"
# =================================================================================================
