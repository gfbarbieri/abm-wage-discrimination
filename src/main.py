###############################################################################
# IMPORTS
###############################################################################

from concurrent.futures import ProcessPoolExecutor, as_completed

from config.exp_config import experiment_params
from models.market import Market

###############################################################################
# RUN EXPERIMENTS
###############################################################################

def run_experiment(exp_key):

    print(f"Retrieving Experiment Details: {exp_key}")
    exp_details = experiment_params[exp_key]
    exp_name = exp_details['name']
    parameters = exp_details['parameters']

    print(f"Starting Experiment: {exp_name} for {parameters['steps']} Steps")
    model = Market(parameters)
    results = model.run()

    print(f"Experiment Complete: {exp_name}")
    results.save(exp_name=exp_name, path='data')

def main():

    print(
        """
        WARNING: The experimental design runs sample parameter sets independently.
        This can lead to inconsistent samples. E.g. changes to random values may
        occur  across samples, violating ceteris paribus assumptions. For consistency
        across samples, implement Sample(parameters) -> Experiment(model, sample) design.
        """
    )

    num_workers = 4

    # Experiments are run independently, but concurrently.
    with ProcessPoolExecutor(max_workers=num_workers) as executor:

        # Submit each experiment to the executor.
        futures = {executor.submit(run_experiment, exp_key): exp_key for exp_key in experiment_params}

        # Wait for all experiments to complete and handle exceptions.
        for future in as_completed(futures):
            exp_key = futures[future]
            
            # Retrieves the result or raises an exception.
            try:
                future.result()
            except Exception as e:
                print(f"Experiment {exp_key} generated an exception: {e}")

if __name__ == '__main__':
    main()