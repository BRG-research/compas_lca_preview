import json
import csv
from pathlib import Path
from collections import OrderedDict

def append_quantities(json_dirs, boq_path, database):
    # Load CSV data into a dictionary keyed by ID
    boq_data = {}
    with open(boq_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            boq_id = row.get("Id")
            if boq_id:
                boq_data[boq_id] = {
                    "Layer Thickness [m]": row.get("Layer Thickness [m]"),
                    "Length [m]": row.get("Length [m]"),
                    "Largest Surface Area [m^2]": row.get("Largest Surface Area [m^2]"),
                    "Volume [m^3]": row.get("Volume [m^3]")
                }

    for json_dir in json_dirs:
        json_dir = Path(json_dir)
        for file in json_dir.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f, object_pairs_hook=OrderedDict)
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON: {file}")
                    continue

            # Determine the ID key
            json_id = data.get("CompilationGroupID") or data.get("GlobalId")
            if not json_id or json_id not in boq_data:
                continue

            if database == "kbob":
                # Inject BOQ values before the materials list
                insert_before_key = "Matched Materials with KBOB Indicators"
                new_data = OrderedDict()
                inserted = False
            else:
                # Inject BOQ values before the materials list
                insert_before_key = "Matched Materials with OEKOBAUDAT Indicators"
                new_data = OrderedDict()
                inserted = False


            for key, value in data.items():
                # Inject BOQ fields before the target key
                if not inserted and key == insert_before_key:
                    for field, val in boq_data[json_id].items():
                        new_data[field] = try_cast_number(val)
                    inserted = True

                new_data[key] = value

            # Write updated JSON back to file
            with open(file, "w", encoding="utf-8") as f:
                json.dump(new_data, f, indent=2, ensure_ascii=False)

def try_cast_number(value):
    """Attempt to cast a string to float, fallback to original."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return value
