# Returns the cost per 1,000 tokens for a given model.
def get_token_cost(model_name):
    cost_table = {
        "gpt-4": {"prompt": 0.03, "completion": 0.06},
        "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
        "gpt-4o": {"prompt": 0.005, "completion": 0.015},
        "gpt-3.5-turbo": {"prompt": 0.001, "completion": 0.002},
    }
    return cost_table.get(model_name, {"prompt": 0.0, "completion": 0.0})
