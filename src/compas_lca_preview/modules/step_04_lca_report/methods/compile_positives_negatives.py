import json
import re
from pathlib import Path

def collect_match_status(parent_dir, output_dir):
    parent_dir = Path(parent_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Pattern for detecting _L{n} suffix
    layer_pattern = re.compile(r"^(.*)_L(\d+)$")

    matched_keys = [
        "Matched Materials with KBOB Indicators",
        "Matched Materials with OEKOBAUDAT Indicators"
    ]

    negatives = {"Unique Elements": [], "ObjectTypes": []}
    positives = {"Unique Elements": [], "ObjectTypes": []}

    for subdir in ["Elements", "Target_Layers"]:
        current_dir = parent_dir / subdir
        if not current_dir.exists():
            continue

        for json_file in current_dir.rglob("*.json"):
            with open(json_file, encoding="utf-8-sig") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON: {json_file}")
                    continue

            # Check for material match key
            matched_data = None
            for key in matched_keys:
                if key in data and isinstance(data[key], list):
                    matched_data = data[key]
                    break

            if matched_data is None:
                continue

            # Determine if negative match (only "None" entries)
            is_negative = all(
                entry.get("Name", "").strip().lower() == "none"
                for entry in matched_data
            )

            # Clean name
            name = data.get("Name", "")
            layer_match = layer_pattern.match(name)
            if layer_match:
                base, layer_num = layer_match.groups()
                transformed_name = f"{base} (Layer {layer_num})"
            else:
                transformed_name = name

            # Determine target dict
            target = negatives if is_negative else positives

            if "GlobalId" in data:
                target["Unique Elements"].append(transformed_name)
            elif "CompilationGroupID" in data:
                target["ObjectTypes"].append(transformed_name)

    # Deduplicate and sort
    for d in [negatives, positives]:
        for key in d:
            d[key] = sorted(set(d[key]))

    # Write both JSON files
    with open(output_dir / "inference_negatives.json", "w", encoding="utf-8-sig") as nf:
        json.dump(negatives, nf, indent=2, ensure_ascii=False)

    with open(output_dir / "inference_positives.json", "w", encoding="utf-8-sig") as pf:
        json.dump(positives, pf, indent=2, ensure_ascii=False)
