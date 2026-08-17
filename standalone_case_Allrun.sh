#!/bin/sh
cd "${0%/*}" || exit                                # Run from this directory
. ${WM_PROJECT_DIR:?}/bin/tools/RunFunctions        # Tutorial run functions
#------------------------------------------------------------------------------

CASE_NAME="negZ"

# ./standalone_case_Allclean.sh

# touch test.foam

# decompDict="-decomposeParDict system/decomposeParDict"

# ============ Create mesh =========================================================================
# blockMesh | tee log.blockMesh

decomposePar | tee log.decomposeParMesh

# mpirun -np 6 snappyHexMesh -parallel | tee log.snappyHexMesh
# runParallel snappyHexMesh -parallel

# reconstructParMesh -time 3
# reconstructPar -time 3    

# checkMesh -allGeometry -allTopology -latestTime -writeAllFields -writeSets vtk | tee log.checkMesh
# checkMesh -allGeometry -allTopology | tee log.checkMesh
# ==================================================================================================

# rm -rf constant/polyMesh
# mv 3/polyMesh constant/
# rm -rf 3/

# rm -rf processor*
# rm -rf log.*

# ============== Solve =============================
# restore0Dir
restore0Dir -processor

runParallel $decompDict potentialFoam -writephi -writePhi -writep

runParallel $decompDict $(getApplication)

# # For reference, the actual parallel command
# # mpirun -np 4 simpleFoam -parallel
# # ==================================================

# # ====== Reconstruct and post-process ===========================================================
# runApplication reconstructParMesh -constant
# runApplication reconstructPar -latestTime

# ./residuals.sh # Technically not needed since im using graphObject, but i just want to use this

# touch wheelWakeOpt.foam

# mkdir images/$CASE_NAME

# pvpython scripts/extractPlaneInfo.py "$CASE_NAME"

# python3 scripts/contourPlot.py "$CASE_NAME"
# =================================================================================================
