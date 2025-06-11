import pandas as pd
import json
from pathlib import Path

def generate_emission_totals(csv_file, database_config, output_path):
    # Define indicator sets
    kbob_indicators = [
        "Global Warming Potential Manufacturing [kgCO2-eqv]",
        "Global Warming Potential Disposal [kgCO2-eqv]",
        "Global Warming Potential Total [kgCO2-eqv]",
        "Biogenic Carbon [kg C]",
        "UBP (Total)",
        "Total Renewable Primary Energy [kWh oil-eq]",
        "Total Non-Renewable Primary Energy [kWh oil-eq]",
    ]

    okobau_indicators = [
        "GWPtotal (A1-A3)",
        "GWPtotal (A4)",
        "GWPtotal (A5)",
        "GWPtotal (C1)",
        "GWPtotal (C2)",
        "GWPtotal (C3)",
        "GWPtotal (C4)",
        "GWPtotal",
        "GWPbiogenic",
        "GWPfossil"
    ]

    if database_config.lower() == "kbob":
        indicators = kbob_indicators
    elif database_config.lower() == "oekobaudat":
        indicators = okobau_indicators
    else:
        raise ValueError("Invalid database_config: must be 'kbob' or 'oekobaudat'")

    df = pd.read_csv(csv_file, na_values=["not matched", "not available", ""])

    totals = {}
    for indicator in indicators:
        min_col = f"{indicator} (min)"
        mean_col = f"{indicator} (mean)"
        max_col = f"{indicator} (max)"

        missing = [col for col in [min_col, mean_col, max_col] if col not in df.columns]
        if missing:
            print(f"Warning: Missing columns for '{indicator}': {', '.join(missing)}. Skipping.")
            continue

        min_sum = df[min_col].dropna().sum()
        mean_sum = df[mean_col].dropna().sum()
        max_sum = df[max_col].dropna().sum()

        output_key = f"{indicator} [kgCO2-eqv]" if database_config.lower() == "oekobaudat" else indicator

        totals[output_key] = {
            "min": round(min_sum, 3),
            "mean": round(mean_sum, 3),
            "max": round(max_sum, 3)
        }


    output_path = Path(output_path)

    # If it's a directory, append default filename
    if output_path.is_dir() or output_path.suffix == "":
        output_path = output_path / "emissions_overview.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(totals, f, ensure_ascii=False, indent=2)
