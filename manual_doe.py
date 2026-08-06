import csv
import json
import os
import shutil
from subprocess import Popen, DEVNULL

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

from centralControl import NPROC, PVPYTHON_SCRIPT
from scripts.error_calc import calc_rmse

coeffs = {
    # "betaStar": [0.05, 0.07, 0.11, 0.13],  # Default = 0.09
    "betaStar": [0.13],
    "sigmaOmega1": [0.4, 0.45, 0.55, 0.6],  # Default = 0.5
    "sigmaOmega2": [0.712, 0.784, 0.928, 1.0],  # Default = 0.856
}

# Map the manual DOE parameter names to the keys used inside turbulenceProperties.
TURB_COEFF_MAP = {
    "betaStar": "betaStar",
    "sigmaOmega1": "alphaOmega1",
    "sigmaOmega2": "alphaOmega2",
}

# Default values for the coefficients that are not being varied in a given trial.
DEFAULT_TURB_COEFFS = {
    "betaStar": 0.09,
    "alphaOmega1": 0.5,
    "alphaOmega2": 0.856,
}


def setup_and_run_case(case_dir, coeff_name, coeff_value):
    """Create a fresh case directory, update the turbulence coefficients, run it, and score it."""
    os.makedirs(case_dir, exist_ok=True)
    shutil.rmtree(case_dir, ignore_errors=True)
    os.makedirs(case_dir, exist_ok=True)

    for folder in ["0", "constant", "system"]:
        shutil.copytree(
            src=folder,
            dst=os.path.join(case_dir, folder),
            dirs_exist_ok=True,
        )

    turb_props = ParsedParameterFile(
        os.path.join(case_dir, "constant", "turbulenceProperties"),
        treatBinaryAsASCII=True,
    )
    coeffs_dict = turb_props["RAS"]["kOmegaSSTCoeffs"]

    # Start from the defaults and overwrite the coefficient being tested.
    for key, value in DEFAULT_TURB_COEFFS.items():
        coeffs_dict[key] = value
    coeffs_dict[TURB_COEFF_MAP[coeff_name]] = coeff_value
    turb_props.writeFile()

    decompose = Popen(
        [f"decomposePar -case {os.path.normpath(case_dir)}"],
        stdin=DEVNULL,
        stdout=DEVNULL,
        shell=True,
    )
    decompose.wait()

    if decompose.returncode != 0:
        raise RuntimeError(f"decomposePar failed for {case_dir}")

    simpleFoam = Popen(
        [f"pyFoamRunner.py --procnr={NPROC} simpleFoam -case {os.path.normpath(case_dir)}"],
        stdin=DEVNULL,
        stdout=DEVNULL,
        shell=True,
    )
    simpleFoam.wait()

    if simpleFoam.returncode != 0:
        raise RuntimeError(f"simpleFoam failed for {case_dir}")

    reconstruct = Popen(
        [f"reconstructPar -case {os.path.normpath(case_dir)} -latestTime"],
        stdin=DEVNULL,
        stdout=DEVNULL,
        shell=True,
    )
    reconstruct.wait()

    if reconstruct.returncode != 0:
        raise RuntimeError(f"reconstructPar failed for {case_dir}")

    pvpython = Popen(
        [f"pvpython {PVPYTHON_SCRIPT} {os.path.normpath(case_dir)}"],
        stdin=DEVNULL,
        stdout=DEVNULL,
        shell=True,
    )
    pvpython.wait()

    if pvpython.returncode != 0:
        raise RuntimeError(f"pvpython failed for {case_dir}")

    total_rmse = 0.0
    for x_pos in [0.33, 0.495]:
        total_rmse += calc_rmse(x_pos=x_pos, case_dir=case_dir)

    return total_rmse


results = {coeff_name: [] for coeff_name in coeffs}
trial_rows = []
trial_index = 0
for coeff_name, values in coeffs.items():
    for coeff_value in values:
        case_dir = os.path.join("cases", f"manual_doe_trial_{trial_index+3}")
        print(f"Running {coeff_name}={coeff_value} in {case_dir}")
        try:
            rmse_value = setup_and_run_case(case_dir, coeff_name, coeff_value)
            trial_status = "COMPLETED"
        except Exception as exc:
            rmse_value = None
            trial_status = f"FAILED: {exc}"
            print(f"Trial failed: {exc}")

        results[coeff_name].append([coeff_value, rmse_value])

        trial_row = {
            "trial_name": os.path.basename(case_dir),
            "trial_status": trial_status,
            "TOTAL_RMSE": rmse_value,
            "betaStar": DEFAULT_TURB_COEFFS["betaStar"],
            "sigmaOmega1": DEFAULT_TURB_COEFFS["alphaOmega1"],
            "sigmaOmega2": DEFAULT_TURB_COEFFS["alphaOmega2"],
        }

        if coeff_name == "betaStar":
            trial_row["betaStar"] = coeff_value
        elif coeff_name == "sigmaOmega1":
            trial_row["sigmaOmega1"] = coeff_value
        elif coeff_name == "sigmaOmega2":
            trial_row["sigmaOmega2"] = coeff_value

        trial_rows.append(trial_row)

        output_path = os.path.join("cases", "manual_doe_results.json")
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(results, handle, indent=2)
        print(f"Saved results to {output_path}")

        csv_output_path = os.path.join("cases", "manual_doe_results.csv")
        with open(csv_output_path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["trial_name", "trial_status", "TOTAL_RMSE", "betaStar", "sigmaOmega1", "sigmaOmega2"],
            )
            writer.writeheader()
            writer.writerows(trial_rows)
        print(f"Saved CSV results to {csv_output_path}")
        trial_index += 1
