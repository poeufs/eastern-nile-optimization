# Script for baseline optimization

import pandas as pd
import numpy as np

import pickle

from ema_workbench import (RealParameter, ScalarOutcome, Constant,
                           Model)
from ema_workbench import MultiprocessingEvaluator, SequentialEvaluator, ema_logging
from ema_workbench.em_framework.optimization import HyperVolume, EpsilonProgress, ArchiveLogger

from data_generation import generate_input_data
from wrapper import model_wrapper

from datetime import datetime

import os
import sys

my_path = sys.path[0]
while (my_path[-1] != "/") and (my_path[-1] != "\\"):
    my_path = my_path[:-1]

sys.path.insert(1, my_path + "Model")

from model_nile import ModelNile

if __name__ == '__main__':

    output_directory = "../Outputs/"
    model_object = ModelNile()
    model_object = generate_input_data(model_object, sim_horizon=20)

    parameter_count = model_object.overarching_policy.get_total_parameter_count()

    em_model = Model('NileProblem', function=model_wrapper)

    em_model.levers = [RealParameter('v' + str(i), 0, 1) for i in range(parameter_count)]

    em_model.constants = [Constant("model", model_object)]

    #specify outcomes
    em_model.outcomes = [ScalarOutcome('egypt_irr', ScalarOutcome.MINIMIZE),
                    ScalarOutcome('egypt_90', ScalarOutcome.MINIMIZE),
                    ScalarOutcome('egypt_low_had', ScalarOutcome.MINIMIZE),
                    ScalarOutcome('sudan_irr', ScalarOutcome.MINIMIZE),
                    ScalarOutcome('sudan_90', ScalarOutcome.MINIMIZE),
                    ScalarOutcome('ethiopia_hydro', ScalarOutcome.MAXIMIZE)]

    convergence_metrics = [
        EpsilonProgress(),
        ArchiveLogger(f"{output_directory}archive_logs",
            [lever.name for lever in em_model.levers],
            [outcome.name for outcome in em_model.outcomes])
        ]

    ema_logging.log_to_stderr(ema_logging.INFO)

    NFE_count = 100000
    epsilon_list = [1e2,1e1,1e-2,1e2,1e1,1e3]

    before = datetime.now()

    with MultiprocessingEvaluator(em_model) as evaluator:
        results, convergence = evaluator.optimize(nfe=NFE_count, searchover='levers', logging_freq=5,
        epsilons=epsilon_list, convergence_freq=500, convergence=convergence_metrics)

    after = datetime.now()

    f = open(f"{output_directory}time_counter.txt", "w")
    f.write(f"It took {after-before} time to do {NFE_count} NFEs with epsilons: {epsilon_list}")
    f.close()

    # pickle.dump(results, open("baseline_results.p", "wb"))
    # pickle.dump(convergence, open("baseline_convergence.p", "wb"))

    results.to_csv(f"{output_directory}baseline_results.csv")
    convergence.to_csv(f"{output_directory}baseline_convergence.csv")

    

    


    
