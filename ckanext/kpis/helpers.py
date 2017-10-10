import json

from ckan.common import config


def get_goals():
    """
    Return a dictionary with the KPI goals.
    If no goals are defined in the config, return a dictionary with 
    placeholder values. If the goals are defined in an invalid way, 
    raise an exception.
    """
    default_goals = {
        'total_datasets': 10000000,
        'total_sources': 20,
        'monthly_users': 2000
    }

    valid_goals = [
        'total_datasets',
        'total_sources',
        'monthly_users',
    ]

    goals_json = config.get('ckanext.kpis.goals')

    if not goals_json:
        return default_goals

    goals = json.loads(goals_json)

    # Make sure the goals are valid
    invalid_goals = []
    for i in goals:
        if i not in valid_goals:
            invalid_goals.append(i)
    if invalid_goals:
        raise ValueError('Invalid KPI goals: {}'.format(invalid_goals))

    # Make sure the goals have valid values
    invalid_values = []
    for i in goals:
        if not isinstance(goals[i], int):
            invalid_values.append({i: goals[i]})
    if invalid_values:
        raise ValueError('Invalid KPI values: {}'.format(invalid_values))

    return goals
