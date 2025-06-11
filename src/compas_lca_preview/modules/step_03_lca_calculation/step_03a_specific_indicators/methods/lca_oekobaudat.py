import json
from pathlib import Path

def extract_oekobaudat_data(input_dirs, output_base_dir, selected_keys=None):
    if selected_keys is None:
        selected_keys = [
            "Name",
            "ID",
            "Reference",
            "Density (kg/m3)",
            "Bezugsgroesse",
            "GWPtotal (A1)",
            "GWPtotal (A2)",
            "GWPtotal (A3)",
            "GWPtotal (A1-A3)",
            "GWPtotal (A4)",
            "GWPtotal (A5)",
            "GWPtotal (B1)",
            "GWPtotal (B2)",
            "GWPtotal (B3)",
            "GWPtotal (B4)",
            "GWPtotal (B5)",
            "GWPtotal (B6)",
            "GWPtotal (B7)",
            "GWPtotal (C1)",
            "GWPtotal (C2)",
            "GWPtotal (C3)",
            "GWPtotal (C4)",
            "GWPbiogenic",
            "GWPfossil",
            "GWPtotal",
            "Conformity",
            "Laenderkennung",
            "Declaration owner",
            "Registrierungsnummer"
        ]

    input_dirs = [Path(d) for d in input_dirs]
    output_base_dir = Path(output_base_dir)

    for input_dir in input_dirs:
        subfolder_name = input_dir.name
        output_dir = output_base_dir / subfolder_name
        output_dir.mkdir(parents=True, exist_ok=True)

        for file_path in input_dir.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON: {file_path}")
                    continue

            # Get identifier and name
            identifier_key = "CompilationGroupID" if "CompilationGroupID" in data else "GlobalId"
            identifier_value = data.get(identifier_key, None)
            name_value = data.get("name", None)

            # Default output structure
            output_json = {
                identifier_key: identifier_value,
                "Name": name_value,
                "Matched Materials with OEKOBAUDAT Indicators": []
            }

            material_steps = [
                step for step in data.get("inference_steps", [])
                if step.get("matched_type") == "material"
            ]
            new_filename = file_path.name.replace("_inference.json", "_indicators.json")
            output_file = output_dir / new_filename

            if not material_steps:
                output_json["Matched Materials with OEKOBAUDAT Indicators"].append({"Name": "None"})
                with open(output_file, "w", encoding="utf-8") as out_f:
                    json.dump(output_json, out_f, ensure_ascii=False, indent=2)
                continue

            last_material_step = material_steps[-1]
            matched_names = last_material_step.get("matched_name", [])
            matched_path = last_material_step.get("matched_path", "")

            if isinstance(matched_names, str):
                matched_names = [matched_names]

            index_path = Path(matched_path) / "index.json"
            if not index_path.exists():
                print(f"Missing index.json at: {index_path}")
                output_json["Matched Materials with OEKOBAUDAT Indicators"].append({"Name": "None"})
                with open(output_file, "w", encoding="utf-8") as out_f:
                    json.dump(output_json, out_f, ensure_ascii=False, indent=2)
                continue

            try:
                with open(index_path, "r", encoding="utf-8") as idx_file:
                    index_data = json.load(idx_file)
                    items = index_data.get("items", [])
            except json.JSONDecodeError:
                print(f"Invalid index.json: {index_path}")
                output_json["Matched Materials with OEKOBAUDAT Indicators"].append({"Name": "None"})
                with open(output_file, "w", encoding="utf-8") as out_f:
                    json.dump(output_json, out_f, ensure_ascii=False, indent=2)
                continue

            enriched_materials = []
            for name in matched_names:
                match = next((item for item in items if item.get("Name") == name), None)
                if match:
                    enriched = {k: match.get(k, 0) for k in selected_keys}
                    enriched_materials.append(enriched)
                else:
                    pass

            if not enriched_materials:
                enriched_materials.append({"Name": "None"})

            output_json["Matched Materials with OEKOBAUDAT Indicators"] = enriched_materials

            with open(output_file, "w", encoding="utf-8") as out_f:
                json.dump(output_json, out_f, ensure_ascii=False, indent=2)
