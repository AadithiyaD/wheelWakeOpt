"""
Main optimisation script
"""
from centralControl import BETASTAR, A1_COEFF,SIGMAOMEGA1,SIGMAOMEGA2, X_POS, TIME_BW_POLLS, FAILURE_TOLERANCE, PARALLEL_RUNS, NPROC, MAX_TRIALS, PVPYTHON_SCRIPT
import os
import re
import shutil
from subprocess import Popen, DEVNULL
from pathlib import Path

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from ax.api.client import Client
from ax.api.protocols.metric import IMetric
from ax.api.protocols.runner import IRunner
from ax.core.trial_status import TrialStatus
from ax.service.utils.report_utils import exp_to_df
from ax.analysis.plotly.plotly_analysis import PlotlyAnalysisCard
from scripts.error_calc import calc_rmse


# ===================================================================================================
# Initialize ax client
client = Client()

# ===================================================================================================

# Add data from any pre-existing trials
preexisting_trials = [
    (
        {"betaStar": 0.09, "sigmaOmega1": 0.5, "sigmaOmega2": 0.856},
        {"TOTAL_RMSE": 14.892201262697139},
    ),
    (
        {"betaStar": 0.11771830081939698, "sigmaOmega1": 0.5123859286308289, "sigmaOmega2": 0.7448952572345733},
        {"TOTAL_RMSE": 14.783879883022014},
    ),
    (
        {"betaStar": 0.05879643544554711, "sigmaOmega1": 0.4235952913761139, "sigmaOmega2": 0.8562350478768348},
        {"TOTAL_RMSE": 14.849035873343762},
    ),
    (
        {"betaStar": 0.07692515857517719, "sigmaOmega1": 0.5945613663643599, "sigmaOmega2": 0.8115444962084293},
        {"TOTAL_RMSE": 14.833491858315751},
    ),
    (
        {"betaStar": 0.09585666842758656, "sigmaOmega1": 0.4819365257397294, "sigmaOmega2": 0.9341342871189118},
        {"TOTAL_RMSE": 14.900662685563077},
    ),
    (
        {"betaStar": 0.10503554542097225, "sigmaOmega1": 0.5723664859307134, "sigmaOmega2": 0.730182550461256},
        {"TOTAL_RMSE": 14.912429590575147},
    ),
    (
        {"betaStar": 0.12395389425880628, "sigmaOmega1": 0.5012908062741086, "sigmaOmega2": 0.733392790239503},
        {"TOTAL_RMSE": 14.351269204418541},
    ),
    (
        {"betaStar": 0.1199682455396507, "sigmaOmega1": 0.5171386737732502, "sigmaOmega2": 0.8481593024400778},
        {"TOTAL_RMSE": 14.783898240410796},
    ),
    (
        {"betaStar": 0.1259106644213064, "sigmaOmega1": 0.4977196378393798, "sigmaOmega2": 0.7286890273250077},
        {"TOTAL_RMSE": 14.57531284213221},
    ),
    (
        {"betaStar": 0.12388747863880833, "sigmaOmega1": 0.47220554437371115, "sigmaOmega2": 0.712},
        {"TOTAL_RMSE": 14.645118275713784},
    ),
]

class Runner(IRunner):
    def __init__(self) -> None:
        # Dict to store simpleFoam popen instances
        self.sf_runners = {}
    
    def run_trial(self, trial_index, parameterization) -> dict[str, str]:
        """Sets up and executes an instance of simpleFoam for the case

        Args:
            trial_index (int): trial index
            parameterization (list): parameter values for current trial

        Returns:
            trial_metadata: dict of trial metadata containing location of case_dir,
            log_file and state_file
        """
    
        # Setup case dir
        case_dir = os.path.join("cases", f"trial_{trial_index}")
        os.makedirs(case_dir, exist_ok=True)
        
        # Copy base files
        for folder in ['0', 'constant', 'system']:
            shutil.copytree(src=folder, 
                            dst=os.path.join(case_dir, folder), dirs_exist_ok = True)
        
        # Modify turbulenceProperties with new coeffs
        turb_props = ParsedParameterFile(
            os.path.join(case_dir, 'constant', 'turbulenceProperties'),
            treatBinaryAsASCII=True
        )
        coeffs = turb_props["RAS"]["kOmegaSSTCoeffs"]
        # coeffs["a1"] = parameterization["a1"]
        coeffs["betaStar"] = parameterization["betaStar"]
        coeffs["alphaOmega1"] = parameterization["sigmaOmega1"]
        coeffs["alphaOmega2"] = parameterization["sigmaOmega2"]
        turb_props.writeFile()
    
        # Non-blocking execution of simpleFoam
        decompose = Popen(
            [f'decomposePar -case {os.path.normpath(case_dir)}'],
            stdin = DEVNULL,
            stdout= DEVNULL,
            shell= True
            )
        
        # Wait for decompose to finish 
        decompose.wait()
        
        potentialFoam = Popen(
            [f'pyFoamRunner.py --procnr={NPROC} potentialFoam -writep -writephi -writePhi -case {os.path.normpath(case_dir)} '],
            stdin = DEVNULL,
            stdout= DEVNULL,
            shell= True
        )
        
        potentialFoam.wait()
        
        simpleFoam = Popen(
            [f'pyFoamRunner.py --procnr={NPROC} simpleFoam -case {os.path.normpath(case_dir)} '],
            stdin = DEVNULL,
            stdout= DEVNULL,
            shell= True
        )
        
        # Store insance for use in poll_trial()
        self.sf_runners[trial_index] = simpleFoam

        # Return metadata
        return {
            'case_dir': case_dir,
            'log_file': os.path.join(case_dir, 'PyFoamRunner.simpleFoam.logfile'),
            'state_file': os.path.join(case_dir, 'PyFoamState.TheState'),
            'trial_index': trial_index
        }
    
    def poll_trial(self, trial_index, trial_metadata) -> TrialStatus:
        """Checks the status of a trial

        Args:
            trial_index (int): index of current trial
            trial_metadata (dict): metadata dict of current trial

        Returns:
            TrialStatus: TrialStatus
        """
        # Get simpleFoam instance
        sf_instance = self.sf_runners[trial_index]
        
        # Check if its still running
        # You could use the State file that pyfoam creates, but 
        # It takes time for that file to be created, and if ax polls
        # before its created, it leads to a file not found error
        if sf_instance.poll() is None:
            return TrialStatus.RUNNING
        
        elif sf_instance.poll() == 0 :
            #  Question - How do you determine divergence / failure of the trial
            #  Ans - I'm doing a VERY simple check here
            #  If the first and last time steps do not exist, I consider
            #  that as a divergence and return a TrialStatus.FAILED
            #  If any of the initial residuals from the last time step are > those of the first time step.
            #  I return a TrialStatus.FAILED
            
            with open(trial_metadata['log_file'], 'r') as f:
                content = f.read().splitlines()
            
            # Extract relevant lines for first and last time steps
            # re.search pattern explanation - \b => line must start with Time and have one or more digits (i.e \d+)
            time_lines = [i for i, line in enumerate(content) if re.search(r"\bTime = \d+", line)]
            if time_lines:
                first_time_idx = time_lines[0]
                time_1_content = content[first_time_idx+2 : first_time_idx+10]
                last_time_idx = time_lines[-1] 
                time_end_content = content[last_time_idx+2 : last_time_idx+10]

            # If sim crashed and did not write any time steps
            if not time_1_content or not time_end_content:
                return TrialStatus.FAILED
            
            # Pattern for extracting decimals
            # \d+ => start with one or more (i.e +) digits (i.e \d)
            # [.?] => match an optional (i.e ?) . (i.e [.])
            # \d* => end with zero or more (i.e *) digits
            # [e]?[-]?\d* => optionally match an e-{number} pattern 
            
            pattern = r"\d+[.]?\d*[e]?[-]?\d*"
            
            # Dict to store residuals
            residuals_1 = {} 
            residuals_2 = {}
            variables = ["Ux", "Uy", "Uz", "p", "omega", "k"]

            # Extract residual values from content
            for line in time_1_content:
                for var in variables:
                    if re.search(f"Solving for {var}", line):
                        residuals_1[var] = float(re.findall(pattern, line)[0])

            for line in time_end_content:
                for var in variables:
                    if re.search(f"Solving for {var}", line):
                        residuals_2[var] = float(re.findall(pattern, line)[0])

            # Simple divergence check
            if any(residuals_2[var] > residuals_1[var] for var in variables):
                return TrialStatus.FAILED
            
            else:
                return TrialStatus.COMPLETED
        
        else:
            print(f"Non-zero exit code {sf_instance.poll()}")
            return TrialStatus.FAILED

class ErrorMetric(IMetric):   
    """IMetric def for calculating RMSE. 
    
    Note - ax calls fetch only if trial status is completed
    """
    def fetch(self, trial_index, trial_metadata: dict) :
        """Calculates rmse and returns dict of {self.name : (total_error, 0)}
        total_error = rmse(x/h) where x/h values are pre-specified in setup
        
        If exception encountered, returns None and ax will ignore the sepcific
        iteration / trialS
        """
        try:
            # Move sampled csv files to new dir for convenience
            # sample_dir = os.path.join(trial_metadata['postProcessing'], 'sample')
            # source_dir_path = os.path.join(sample_dir, os.listdir(sample_dir)[0])
            # dest_dir_path = trial_metadata['dataForOptLoop']
            
            # for file in X_BY_H:
            #     shutil.copy(src= os.path.join(source_dir_path, f'x_by_h_{file:02d}_U.csv'),
            #                 dst= os.path.join(dest_dir_path, f'x_by_h_{file:02d}_U.csv'))
            
            case_dir = trial_metadata['case_dir']
            
            # Reconstruct and extract sim data
            reconstruct = Popen(
                [f'reconstructPar -case {os.path.normpath(case_dir)} -latestTime'],
                stdin = DEVNULL,
                stdout= DEVNULL,
                shell= True
            )
            reconstruct.wait()
            pvpython = Popen(
                [f'pvpython {PVPYTHON_SCRIPT} "cases/trial_{trial_index}"'],
                stdin = DEVNULL,
                stdout= DEVNULL,
                shell= True
            )
            pvpython.wait()
            
            # Calculate trial error
            total_error = 0
            for x_pos in X_POS:
                total_error += calc_rmse(x_pos= x_pos,
                                        case_dir=case_dir)
            
            return (0, total_error)
        
        except Exception as e:
            print(f"Encountered error {e}")
            return None

client.configure_experiment(
    parameters=[BETASTAR, SIGMAOMEGA1, SIGMAOMEGA2],
    name="3D Rotating Wheel Wake Calibration",
    description="Optimising the wake prediction behind a 3D rotating wheel with the k-omega SST model",
    owner="me"
)

runner = Runner()
error_metric = ErrorMetric(name="TOTAL_RMSE") 

client.configure_optimization(objective="-TOTAL_RMSE")

client.configure_runner(runner=runner)
client.configure_metrics(metrics=[error_metric])

for parameters, data in preexisting_trials:
    # Attach the parameterization to the Client as a trial 
    trial_index = client.attach_trial(parameters=parameters)
    
    # and immediately complete it with the preexisting data
    client.complete_trial(trial_index=trial_index, raw_data=data)

client.run_trials(
    max_trials=MAX_TRIALS,
    parallelism=PARALLEL_RUNS,
    tolerated_trial_failure_rate=FAILURE_TOLERANCE,
    initial_seconds_between_polls=TIME_BW_POLLS
)

best_parameters, prediction, index, name = client.get_best_parameterization()
print("Best Parameters:", best_parameters)
print("Prediction (mean, variance):", prediction)

# Saving results to json and csv
experiment = client._experiment
df = exp_to_df(experiment)

results_dir = Path('ax_result_data')
results_dir.mkdir(exist_ok=True)

df.to_csv(f'{results_dir}/experiment_results.csv', index=False)
df.to_json(f'{results_dir}/experiment_results.json', indent=2)

# Generate visualisations
cards = client.compute_analyses(display=False)

html_dir = results_dir / 'html'
html_dir.mkdir(exist_ok=True)

for card_index, card in enumerate(
    leaf_card
    for card_group in cards
    for leaf_card in card_group.flatten()
):
    card_name = card.title.replace(' ', '_').replace('/', '_')
    html_file = html_dir / f'{card_index}_{card_name}.html'

    if isinstance(card, PlotlyAnalysisCard):
        card.get_figure().write_html(html_file)
    else:
        html_file.write_text(card._repr_html_(), encoding='utf-8')

