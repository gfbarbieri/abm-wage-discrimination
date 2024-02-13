from .base_config import base_params

def get_experiment_parameters(static, updates):
    """
    Update base parameter values with the experimental parameter values.

    Parameters
    ----------
    static (dict): The base parameters.
    updates (dict): The experiment parameters.

    Returns
    -------
    dict : A dictionary of parameters for the experiment.
    """

    exp_params = static.copy()
    exp_params.update(updates)

    return exp_params

# zd_zp = {
#     'd_range': [0, 0],
#     'premium': 0
# }

# zd_pp = {
#     'd_range': [0, 0],
#     'premium': 0.20
# }

pd_zp = {
    'd_range': [0, 1],
    'premium': 0
}

pd_pp = {
    'd_range': [0, 1],
    'premium': 0.20
}

experiment_params = {
    # 'zd_zp': {
    #     'name': 'zero_discrim_zero_premium',
    #     'parameters': get_experiment_parameters(base_params, zd_zp)
    # },
    # 'zd_pp': {
    #     'name': 'zero_discrim_pos_premium',
    #     'parameters': get_experiment_parameters(base_params, zd_pp),
    # },
    'pd_zp': {
        'name': 'pos_discrim_zero_premium',
        'parameters': get_experiment_parameters(base_params, pd_zp)
    },
    'pd_pp': {
        'name': 'pos_discrim_pos_premium',
        'parameters': get_experiment_parameters(base_params, pd_pp),
    },
}