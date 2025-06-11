# metrics.py
def compute_llm_cost_and_impact(token_usage):
    prompt_tokens = token_usage.prompt_tokens
    completion_tokens = token_usage.completion_tokens
    total_tokens = token_usage.total_tokens

    cached_tokens = getattr(token_usage, 'cached_tokens', 0)
    non_cached_tokens = prompt_tokens - cached_tokens

    price = (non_cached_tokens * 0.0000025) + (cached_tokens * 0.00000125) + (completion_tokens * 0.00001)
    electricity_kwh = total_tokens * 0.000002
    gwp_kgco2eqv = electricity_kwh * 0.242

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "cached_tokens": cached_tokens,
        "non_cached_tokens": non_cached_tokens,
        "total_price": price,
        "electricity_kwh": electricity_kwh,
        "gwp_kgco2eqv": gwp_kgco2eqv
    }
