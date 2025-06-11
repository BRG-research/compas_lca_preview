import json
from pathlib import Path
from collections import OrderedDict
import csv

# Emission keys for KBOB
ENV_KEYS_KBOB = [
    "Global Warming Potential Total [kgCO2-eqv]",
    "Global Warming Potential Manufacturing [kgCO2-eqv]",
    "Global Warming Potential Disposal [kgCO2-eqv]",
    "Biogenic Carbon [kg C]",
    "UBP (Total)",
    "UBP (Manufacturing)",
    "UBP (Disposal)",
    "Total Renewable Primary Energy [kWh oil-eq]",
    "Manufacturing Renewable Primary Energy [kWh oil-eq]",
    "Disposal Renewable Primary Energy [kWh oil-eq]",
    "Total Non-Renewable Primary Energy [kWh oil-eq]",
    "Manufacturing Non-Renewable Primary Energy [kWh oil-eq]",
    "Disposal Non-Renewable Primary Energy [kWh oil-eq]"
]

# Emission keys for OEKOBAUDAT
ENV_KEYS_OEKOBAUDAT = [
    "GWPtotal (A1)", "GWPtotal (A2)", "GWPtotal (A3)", "GWPtotal (A1-A3)",
    "GWPtotal (A4)", "GWPtotal (A5)", "GWPtotal (B1)", "GWPtotal (B2)",
    "GWPtotal (B3)", "GWPtotal (B4)", "GWPtotal (B5)", "GWPtotal (B6)",
    "GWPtotal (B7)", "GWPtotal (C1)", "GWPtotal (C2)", "GWPtotal (C3)",
    "GWPtotal (C4)", "GWPbiogenic", "GWPfossil", "GWPtotal"
]

def determine_multiplier(material, volume, area):
    ref = material.get("Reference", "").lower()
    if ref == "m":
        return None  # Skip linear meter-based materials
    elif ref == "kg":
        return float(material.get("Density (kg/m3)", 1)) * float(volume)
    elif ref == "qm":
        return float(area)
    elif ref == "m3":
        return float(volume)
    elif ref == "pcs":
        return 1
    else:
        return 1


def process_material(material, volume, area, keys, is_oekobaudat=False):
    multiplier = determine_multiplier(material, volume, area)
    if multiplier is None:
        return None  # Skip material

    bezugsgroesse = 1
    if is_oekobaudat:
        try:
            bezugsgroesse = float(material.get("Bezugsgroesse", 1))
        except ValueError:
            bezugsgroesse = 1

    for key in keys:
        if key in material:
            try:
                value = float(material[key])
                scaled = (value * multiplier) / bezugsgroesse
                material[key] = str(round(scaled, 4))
            except ValueError:
                pass
    return material





def process_file(input_path, output_path, quantity_lookup):
    with open(input_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    id_ = data.get("GlobalId") or data.get("CompilationGroupID")
    volume = area = 1
    if id_ and id_ in quantity_lookup:
        volume = quantity_lookup[id_]["Volume [m^3]"]
        area = quantity_lookup[id_]["Largest Surface Area [m^2]"]

    if "Matched Materials with KBOB Indicators" in data:
        key = "Matched Materials with KBOB Indicators"
        new_key = "Matched Materials with Gross Emissions (KBOB)"
        emission_keys = ENV_KEYS_KBOB
    elif "Matched Materials with OEKOBAUDAT Indicators" in data:
        key = "Matched Materials with OEKOBAUDAT Indicators"
        new_key = "Matched Materials with Gross Emissions (OEKOBAUDAT)"
        emission_keys = ENV_KEYS_OEKOBAUDAT
    else:
        return

    materials = data.pop(key, [])
    is_oekobaudat = "OEKOBAUDAT" in key

    processed = [
        m for m in (
            process_material(mat, volume, area, emission_keys, is_oekobaudat=is_oekobaudat)
            for mat in materials
        ) if m is not None
    ]



    # Build new ordered dictionary to control output key order
    new_data = OrderedDict()

    # Copy original keys except the matched materials key we just popped
    for k, v in data.items():
        new_data[k] = v

    # Insert volume and area explicitly
    new_data["Volume [m^3]"] = volume
    new_data["Largest Surface Area [m^2]"] = area

    # Insert the processed emissions key last
    new_data[new_key] = processed

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8-sig') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)

def load_quantity_lookup(boq_csv_path):
    lookup = {}
    with open(boq_csv_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            id_ = row.get("Id")
            if id_:
                try:
                    volume = float(row.get("Volume [m^3]", 1))
                    area = float(row.get("Largest Surface Area [m^2]", 1))
                except ValueError:
                    volume, area = 1.0, 1.0
                lookup[id_] = {
                    "Volume [m^3]": volume,
                    "Largest Surface Area [m^2]": area
                }
    return lookup



def calculate_gross_emissions(input_dirs, output_base_dir, input_boq_csv):
    output_base_path = Path(output_base_dir)
    quantity_lookup = load_quantity_lookup(input_boq_csv)
    for input_dir in input_dirs:
        input_dir_path = Path(input_dir)
        input_dir_name = input_dir_path.name
        output_subdir = output_base_path / input_dir_name
        output_subdir.mkdir(parents=True, exist_ok=True)

        for json_file in input_dir_path.glob("*.json"):
            original_name = json_file.name

            if original_name.endswith("_indicators.json"):
                new_filename = original_name.replace("_indicators.json", "_emissions.json")
            else:
                new_filename = original_name

            output_path = output_subdir / new_filename
            process_file(json_file, output_path, quantity_lookup)
