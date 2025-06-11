import csv
import json
from pathlib import Path

def append_emissions_to_csv(csv_path, json_dir, output_csv_path, config_database):
    """
    Appends min, mean, and max values for emissions from JSON files
    into a new CSV file based on matching GlobalId or CompilationGroupID.
    """

    if config_database.lower() == "kbob":
        indicator_field = "Matched Materials with Gross Emissions (KBOB)"
        total_gwp_key = "Global Warming Potential Total [kgCO2-eqv]"
        keys_to_analyze = [
            "Global Warming Potential Manufacturing [kgCO2-eqv]",
            "Global Warming Potential Disposal [kgCO2-eqv]",
            "Global Warming Potential Total [kgCO2-eqv]",
            "Biogenic Carbon [kg C]",
            "UBP (Total)",
            "Total Renewable Primary Energy [kWh oil-eq]",
            "Total Non-Renewable Primary Energy [kWh oil-eq]"
        ]
    else:  # Assume OEKOBAUDAT
        indicator_field = "Matched Materials with Gross Emissions (OEKOBAUDAT)"
        total_gwp_key = "GWPtotal"
        keys_to_analyze = [
            "GWPbiogenic",
            "GWPfossil",
            "GWPtotal",
            "GWPtotal (A1-A3)",
            "GWPtotal (A4)",
            "GWPtotal (A5)",
            "GWPtotal (C1)",
            "GWPtotal (C2)",
            "GWPtotal (C3)",
            "GWPtotal (C4)"
        ]

    csv_path = Path(csv_path)
    json_dir = Path(json_dir)
    output_csv_path = Path(output_csv_path)

    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames.copy()

    for key in keys_to_analyze:
        fieldnames.append(f"{key} (min)")
        fieldnames.append(f"{key} (mean)")
        fieldnames.append(f"{key} (max)")

    for row in rows:
        match_id = row["Id"]

        matching_file = None
        for json_file in json_dir.rglob("*.json"):
            with open(json_file, encoding="utf-8-sig") as jf:
                try:
                    data = json.load(jf)
                except json.JSONDecodeError:
                    continue

            if data.get("GlobalId") == match_id or data.get("CompilationGroupID") == match_id:
                matching_file = data
                break

        if not matching_file:
            for key in keys_to_analyze:
                row[f"{key} (min)"] = "not matched"
                row[f"{key} (mean)"] = "not matched"
                row[f"{key} (max)"] = "not matched"
            continue

        materials = matching_file.get(indicator_field, [])
        valid_mats = [m for m in materials if m.get("Name", "").lower() != "none"]

        def safe_float(val):
            try:
                return float(val)
            except (TypeError, ValueError):
                return None

        mats_with_gwp = [
            (mat, safe_float(mat.get(total_gwp_key))) for mat in valid_mats
            if safe_float(mat.get(total_gwp_key)) is not None
        ]

        if not mats_with_gwp:
            for key in keys_to_analyze:
                row[f"{key} (min)"] = "not matched"
                row[f"{key} (mean)"] = "not matched"
                row[f"{key} (max)"] = "not matched"
            continue

        min_mat = min(mats_with_gwp, key=lambda x: x[1])[0]
        max_mat = max(mats_with_gwp, key=lambda x: x[1])[0]

        for key in keys_to_analyze:
            # --- Handle A1-A3 special case ---
            def get_a1_a3_sum(mat):
                raw = mat.get("GWPtotal (A1-A3)")
                val = safe_float(raw)
                if val is not None and abs(val) > 1e-6:
                    return val  # use if valid and non-zero

                # fallback to A1, A2, A3
                a1 = safe_float(mat.get("GWPtotal (A1)"))
                a2 = safe_float(mat.get("GWPtotal (A2)"))
                a3 = safe_float(mat.get("GWPtotal (A3)"))
                if None not in (a1, a2, a3):
                    return round(a1 + a2 + a3, 4)

                return val if val is not None else None


            if key == "GWPtotal (A1-A3)":
                val_min = get_a1_a3_sum(min_mat)
                val_max = get_a1_a3_sum(max_mat)
            else:
                val_min = safe_float(min_mat.get(key))
                val_max = safe_float(max_mat.get(key))

            if val_min is not None:
                row[f"{key} (min)"] = round(val_min, 4)
            else:
                row[f"{key} (min)"] = ""

            if val_max is not None:
                row[f"{key} (max)"] = round(val_max, 4)
            else:
                row[f"{key} (max)"] = ""

            if val_min is not None and val_max is not None:
                row[f"{key} (mean)"] = round((val_min + val_max) / 2, 4)
            else:
                row[f"{key} (mean)"] = ""


    with open(output_csv_path, "w", newline='', encoding="utf-8-sig") as outf:
        writer = csv.DictWriter(outf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Final Bill of Quantities saved under: {output_csv_path}")
